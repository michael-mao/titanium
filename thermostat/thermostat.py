# -*- coding: utf-8 -*-

import time
import datetime
import threading

from logging import getLogger
from decimal import Decimal
from collections import OrderedDict

from pubnub import Pubnub

from . import errors, utils, weather, sensor, sql, config, decision

if utils.on_rpi():
    import RPi.GPIO as GPIO


class Thermostat(threading.Thread, metaclass=utils.Singleton):
    """ Main class.

    Contains decision making algorithm. Gathers all available input and data from sources.
    Maintains settings and history in memory.
    Spawns a number of daemon threads to perform background tasks.

    Notes:
        - All floating point arithmetic should use Decimal type, pass in number as str to maintain precision
    """

    def __init__(self):
        super().__init__()
        self._settings = OrderedDict(sorted(utils.init_settings().items(), key=lambda t: t[0]))
        self._history = utils.init_history()
        self._current_temperature = Decimal(0)
        self._temperature_range = (Decimal(0), Decimal(0))
        self._on_rpi = utils.on_rpi()
        self._state = utils.State.IDLE

        self.logger = getLogger('app.thermostat')
        self.temperature_offset = Decimal('1.5')
        self.mode = utils.Mode.OFF
        self.last_state_update = 0

        self.cost_table = None  # must init after thread starts
        self.pubnub = Pubnub(
            publish_key=config.PUBLISH_KEY,
            subscribe_key=config.SUBSCRIBE_KEY,
            uuid=config.THERMOSTAT_ID,
        )
        self.weather_thread = weather.WeatherAPI(
            self._settings['temperature_unit'],
            self._settings['city'],
            self._settings['country_code'],
        )
        # TODO: actively record user actions (input range, changes after prediction)
        self.history_thread = threading.Timer(600, self.set_history)
        self.history_thread.daemon = True
        self.locks = {
            'settings': threading.Lock(),
            'temperature_range': threading.Lock(),
        }

    def run(self):
        """ Entry method.

        Main event loop is here.
        """
        # initialize db
        self.cost_table = sql.CostTable()

        # initialize sensor and pins
        if self.on_rpi:
            utils.init_rpi()
            sensor.init_sensor()
            self.current_temperature = sensor.read_temperature()

        # start daemon thread to fetch weather data
        self.weather_thread.start()

        # start daemon thread to record history data
        self.history_thread.start()

        # subscribe to remote access messages
        self.pubnub.subscribe(
            channels=config.THERMOSTAT_ID,
            callback=self._callback,
            error=self._error,
        )

        while True:
            if self.mode != utils.Mode.OFF:
                self.update_state()
            time.sleep(config.UPDATE_INTERVAL)

    def stop(self):
        """ Exit handler.

        Write data stored in memory back to files.
        """
        self.pubnub.unsubscribe(config.THERMOSTAT_ID)
        utils.write_to_file(config.SETTINGS_FILENAME, self._settings)
        utils.write_to_file(config.HISTORY_FILENAME, self._history)
        self.cost_table.close()
        self.logger.info('cleanup completed')

    def toggle_power(self):
        self.mode = utils.Mode.AUTO if self.mode == utils.Mode.OFF else utils.Mode.OFF
        self.state = utils.State.IDLE
        # self.last_state_update = time.time()
        self.publish_mode()

    def toggle_mode(self, mode=None):
        if isinstance(mode, utils.Mode):
            self.mode = mode
        else:
            if self.mode == utils.Mode.AUTO:
                self.mode = utils.Mode.HEAT
            elif self.mode == utils.Mode.HEAT:
                self.mode = utils.Mode.COOL
            elif self.mode == utils.Mode.COOL:
                self.mode = utils.Mode.AUTO
        self.publish_mode()

    def update_state(self):
        """ Decision maker.

        Gathers input and data to update thermostat state.
        """
        self.logger.debug('thermostat state is {0}'.format(self.state))
        if self.on_rpi:
            self.current_temperature = sensor.read_temperature()

        low, high = self.temperature_range
        if self.current_temperature < (low - self.temperature_offset):
            new_state = utils.State.HEAT
        elif self.current_temperature > (high + self.temperature_offset):
            new_state = utils.State.COOL
        else:
            # within range, make decision
            new_state = self.make_decision()

        # prevent oscillation
        if (time.time() - self.last_state_update) > config.OSCILLATION_DELAY:
            if self.state != new_state:
                self.last_state_update = time.time()

            # check mode to determine if new state is allowed
            if self.mode == utils.Mode.HEAT:
                self.state = new_state if new_state != utils.State.COOL else self.state
            elif self.mode == utils.Mode.COOL:
                self.state = new_state if new_state != utils.State.HEAT else self.state
            else:
                self.state = new_state
            self.publish_state()
            self.logger.debug('thermostat state updated to {0}'.format(self.state))

    def make_decision(self):
        params_list = list()

        # TODO: likely needs an additional multiplier to amplify difference
        # TODO: score is always max when this is the only parameter in DM
        rating = self.temperature_range_equilibrium - self.current_temperature
        params_list.append(('internal_temperature', rating))

        # use external temperature if the data is recent
        # TODO: factor in external humidity
        if (datetime.datetime.now() - self.weather_thread.last_updated).total_seconds() < 3600:
            rating = self.temperature_range_ceiling - self.weather_thread.temperature
            params_list.append(('external_temperature', rating))

        # use history if the data exists
        past_temperature = self.get_history()
        if past_temperature is not None:
            rating = past_temperature - self.current_temperature
            params_list.append(('history_temperature', rating))

        # use energy cost if data exists
        cost_data = self.cost_table.select(
            select='start_time,cost',
            where={'country_code': self._settings['country_code'], 'city': self._settings['city']}
        )
        if cost_data:
            cost_data = dict(cost_data)
            lowest_cost = min(cost_data.values())
            current_hour = utils.round_time(datetime.datetime.now(), 3600).hour
            current_cost = cost_data.get(current_hour)
            if current_cost is not None:
                ratio = Decimal(lowest_cost) / Decimal(current_cost)
                rating = ratio * params_list[0][1]  # ratio * (internal temperature rating)
                params_list.append(('energy_cost', rating))

        matrix = decision.build_decision_matrix(params_list)
        return decision.evaluate_decision_matrix(matrix)

    def get_setting(self, name):
        """ Get setting value.

        :param name: setting name
        :return: setting value, None if setting does not exist
        """
        return self._settings.get(name)

    def set_setting(self, name, value):
        """ Set setting value.

        :param name: setting name
        :param value: setting value
        :return: None
        """
        if name in self._settings:
            self._settings[name] = value

    def get_history(self, dt=None):
        """ Get temperature at specified datetime.

        If dt is None, defaults to current time. Full datetime is needed to evaluate day of week.

        :param dt: datetime.datetime object
        :return: temperature
        """
        if dt is None:
            dt = datetime.datetime.now()
        elif not isinstance(dt, datetime.datetime):
            self.logger.error('must be datetime object')
            return None

        rounded_dt = utils.round_time(dt)
        day = utils.WeekDay(rounded_dt.weekday()).name
        time_block = rounded_dt.strftime('%H:%M')
        temperature = self._history[day][time_block]
        return Decimal(temperature) if temperature is not None else None

    def set_history(self, dt=None, temperature=None):
        """ Set temperature at specified datetime.

        If dt is None, defaults to current time. Full datetime is need to evaluate day of week.
        If temperature is None, defaults to current temperature.

        :param dt: datetime.datetime object
        :param temperature: temperature to record
        :return: None
        """
        if temperature is None:
            temperature = self.current_temperature

        if dt is None:
            dt = datetime.datetime.now()
        elif not isinstance(dt, datetime.datetime):
            self.logger.error('must be datetime object')
            return None

        rounded_dt = utils.round_time(dt)
        day = utils.WeekDay(rounded_dt.weekday()).name
        time_block = rounded_dt.strftime('%H:%M')
        self._history[day][time_block] = str(temperature)  # store as str to avoid conversion to JSON float

    def publish_temperatures(self, current=True, range=True):
        data = {
            'action': 'temperature_data',
            'data': {
                'current_temperature': round(self.current_temperature) if current else None,
                'temperature_low': round(self.temperature_range_floor) if range else None,
                'temperature_high': round(self.temperature_range_ceiling) if range else None,
            }
        }
        self.pubnub.publish(config.THERMOSTAT_ID, data, error=self._error)
        self.logger.debug('published message: {0}'.format(data))

    def publish_mode(self):
        data = {
            'action': 'mode_data',
            'data': {
                'mode': str(self.mode).lower()
            }
        }
        self.pubnub.publish(config.THERMOSTAT_ID, data, error=self._error)
        self.logger.debug('published message: {0}'.format(data))

    def publish_state(self):
        data = {
            'action': 'state_data',
            'data': {
                'state': str(self.state).lower()
            }
        }
        self.pubnub.publish(config.THERMOSTAT_ID, data, error=self._error)
        self.logger.debug('published message: {0}'.format(data))

    def publish_settings(self):
        data = {
            'action': 'settings_data',
            'data': utils.prettify_settings(self.settings)
        }
        self.pubnub.publish(config.THERMOSTAT_ID, data, error=self._error)
        self.logger.debug('published message: {0}'.format(data))

    def _callback(self, message, channel):
        """ Pubnub message callback.

        :param message: received payload
        :param channel: channel name
        :return: None
        """
        self.logger.debug(message)

        if message['action'] == 'request_temperatures':
            self.publish_temperatures(range=(message['value'] == 'all'))
        elif message['action'] == 'request_mode':
            self.publish_mode()
        elif message['action'] == 'request_settings':
            self.publish_settings()
        elif message['action'] == 'update_temperature_range':
            low = message.get('temperature_low')
            high = message.get('temperature_high')
            if low is not None and high is not None:
                self.temperature_range = (Decimal(low), Decimal(high))
        elif message['action'] == 'update_mode':
            mode = message.get('mode')
            if mode is not None:
                mode = utils.Mode[mode.upper()]
                self.toggle_mode(mode)
        elif message['action'] == 'update_setting':
            name = message.get('setting_name')
            value = message.get('setting_value')
            if name is not None and value is not None:
                self.settings = utils.unprettify_setting_name(self.settings, name, value)

    def _error(self, message):
        """ Pubnub error callback.

        :param message:
        :return: None
        """
        self.logger.error(message)

    @staticmethod
    def validate_temperature(value):
        if value < config.MIN_TEMPERATURE:
            raise errors.TemperatureValidationError('Temperature cannot be below {}'.format(config.MIN_TEMPERATURE))
        if value > config.MAX_TEMPERATURE:
            raise errors.TemperatureValidationError('Temperature cannot be above {}'.format(config.MAX_TEMPERATURE))

    @property
    def on_rpi(self):
        return self._on_rpi

    @property
    def is_on(self):
        return self.mode != utils.Mode.OFF

    @property
    def is_active(self):
        return self.state != utils.State.IDLE

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if self.on_rpi:
            if state == utils.State.IDLE:
                GPIO.output(config.FAN_PIN, config.RELAY_OFF)
                GPIO.output(config.HEAT_PIN, config.RELAY_OFF)
                GPIO.output(config.COOL_PIN, config.RELAY_OFF)
            elif state == utils.State.HEAT:
                GPIO.output(config.FAN_PIN, config.RELAY_ON)
                GPIO.output(config.HEAT_PIN, config.RELAY_ON)
                GPIO.output(config.COOL_PIN, config.RELAY_OFF)
            elif state == utils.State.COOL:
                GPIO.output(config.FAN_PIN, config.RELAY_ON)
                GPIO.output(config.HEAT_PIN, config.RELAY_OFF)
                GPIO.output(config.COOL_PIN, config.RELAY_ON)
        self._state = state

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, t):
        # TODO: validation
        self.locks['settings'].acquire(False)
        key, value = t
        if self._settings.get(key):
            self._settings[key] = value
            self.publish_settings()
        self.locks['settings'].release()

    @property
    def current_temperature(self):
        return self._current_temperature

    @current_temperature.setter
    def current_temperature(self, value):
        self._current_temperature = value

    @property
    def temperature_range(self):
        return self._temperature_range

    @temperature_range.setter
    def temperature_range(self, t_range):
        self.locks['temperature_range'].acquire(False)
        try:
            low, high = t_range
            if high < low:
                raise errors.TemperatureValidationError('Invalid range.')
            self.validate_temperature(low)
            self.validate_temperature(high)
            self._temperature_range = t_range
            # send update
            self.publish_temperatures(current=False)
        finally:
            self.locks['temperature_range'].release()

    @property
    def temperature_range_floor(self):
        return min(self.temperature_range)

    @property
    def temperature_range_ceiling(self):
        return max(self.temperature_range)

    @property
    def temperature_range_equilibrium(self):
        # biased towards range ceiling
        low, high = self.temperature_range
        bias = (high - low) / 4
        equilibrium = sum(self.temperature_range) / 2
        return equilibrium + bias
