# -*- coding: utf-8 -*-

import time
import datetime
import threading

from logging import getLogger
from functools import reduce
from enum import Enum, unique
from decimal import Decimal

from . import errors, utils, weather, sensor


@unique
class State(Enum):
    OFF = 0
    HEAT = 1
    COOL = 2

    def __str__(self):
        return self.name


@unique
class WeekDay(Enum):
    monday = 0
    tuesday = 1
    wednesday = 2
    thursday = 3
    friday = 4
    saturday = 5
    sunday = 6


class Thermostat(metaclass=utils.Singleton):
    # bounds for input range
    MIN_TEMPERATURE = 0
    MAX_TEMPERATURE = 35

    # decision matrix thresholds, within range(-1, 1)
    # -1              COOL_THRESHOLD      HEAT_THRESHOLD          1
    # --------COOL--------|--------OFF--------|--------HEAT--------
    DM_HEAT_THRESHOLD = Decimal('0.5')
    DM_COOL_THRESHOLD = Decimal('-0.5')

    # decision matrix parameters and their weighting, weightings must sum to 1
    DM_WEIGHTINGS = {
        'internal_temperature': Decimal('0.4'),
        'external_temperature': Decimal('0.2'),
        'history_temperature': Decimal('0.2'),
        'energy_price': Decimal('0.2'),
    }

    def __init__(self):
        self._settings = utils.init_settings()
        self._history = utils.init_history()
        self._current_temperature = Decimal(0)
        self._temperature_range = (Decimal(0), Decimal(0))
        self._on_rpi = utils.on_rpi()
        self.temperature_increment = Decimal('0.5')
        self.update_interval = 5
        self.state = State.OFF
        self.logger = getLogger('app.thermostat')
        self.weather_thread = weather.WeatherAPI(
            self._settings['temperature_unit'],
            self._settings['city'],
            self._settings['country_code'],
        )
        # TODO: actively record user actions (input range, changes after prediction)
        self.history_thread = threading.Timer(600, self.set_history)
        self.history_thread.daemon = True

    def run(self):
        """ Entry method.

        Main event loop is here.
        """
        # initialize sensor
        if self.on_rpi:
            sensor.init_sensor()
            self.current_temperature = sensor.read_temperature()

        # start daemon thread to fetch weather data
        self.weather_thread.start()

        # start daemon thread to record history data
        self.history_thread.start()

        while True:
            self.update_state()
            time.sleep(self.update_interval)

    def stop(self):
        """ Exit handler.

        Write data stored in memory back to files.
        """
        utils.write_to_file(utils.SETTINGS_FILENAME, self._settings)
        utils.write_to_file(utils.HISTORY_FILENAME, self._history)
        self.logger.info('cleanup completed')

    def update_state(self):
        """ Decision maker.

        Gathers input and data to update thermostat state.
        """
        self.logger.debug('thermostat state is {0}'.format(self.state))
        if self.on_rpi:
            self.current_temperature = sensor.read_temperature()

        low, high = self.temperature_range
        if self.current_temperature < (low - self.temperature_increment):
            self.state = State.HEAT
        elif self.current_temperature > (high + self.temperature_increment):
            self.state = State.COOL
        else:
            # within range, build and evaluate decision matrix
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

            # TODO: price
            matrix = self.build_decision_matrix(params_list)
            self.state = self.evaluate_decision_matrix(matrix)

        self.logger.debug('thermostat state updated to {0}'.format(self.state))

    def build_decision_matrix(self, params_list):
        """ Creates decision matrix data structure.

        Matches passed in parameter and rating tuple to the respective weighting in DM_WEIGHTINGS.
        Parameters that do not exist in DM_WEIGHTINGS are ignored. Conversely, if no matching tuple is passed in for
        a key in DM_WEIGHTINGS, it will not be included in the final matrix (other parameter weightings will be
        recalculated accordingly).

        :param params: list of tuples, (parameter_name, rating)
            - parameter_name must match a key in DM_WEIGHTINGS
        :return: decision matrix, dictionary of the form { parameter: (weight, rating), ... }
        """
        matrix = {}
        total_weight = Decimal(0)
        for parameter, rating in params_list:
            weight = self.DM_WEIGHTINGS.get(parameter)
            if weight is not None:
                matrix[parameter] = (weight, rating)
                total_weight += weight
            self.logger.debug('parameter {0} has weight {1} and rating {2}'.format(parameter, weight, rating))

        # if there are missing parameter ratings, recalculate weightings
        if len(matrix) != len(self.DM_WEIGHTINGS):
            for key, value in matrix.items():
                weight, rating = value
                matrix[key] = (weight/total_weight, rating)
                self.logger.debug('parameter {0} has recalculated weight, rating {1}'.format(key, matrix[key]))

        return matrix

    def evaluate_decision_matrix(self, matrix):
        """ Evaluates decision matrix.

        Calculates the total score based on weighting and rating of each parameter.
        Determines new thermostat state based on total score and preset thresholds.

        Normalizes ratings to be within range(-1, 1) before multiplying weight.

        :param matrix: decision matrix
        :return: new thermostat state
        """
        total_score = Decimal(0)
        total_rating = reduce(lambda x, y: x+y, [value[1] for value in matrix.values()])

        for key, value in matrix.items():
            score = reduce(lambda weight, rating: weight*(rating/total_rating), value)
            total_score += score
        self.logger.debug('total rating is {0}'.format(total_rating))
        self.logger.debug('total score is {0}'.format(total_score))

        new_state = State.OFF
        if total_score > self.DM_HEAT_THRESHOLD:
            new_state = State.HEAT
        elif total_score < self.DM_COOL_THRESHOLD:
            new_state = State.COOL

        return new_state

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
        day = WeekDay(rounded_dt.weekday()).name
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
        day = WeekDay(rounded_dt.weekday()).name
        time_block = rounded_dt.strftime('%H:%M')
        self._history[day][time_block] = str(temperature)  # store as str to avoid conversion to JSON float

    @classmethod
    def validate_temperature(cls, value):
        if value < cls.MIN_TEMPERATURE:
            raise errors.TemperatureValidationError('Temperature cannot be below {}'.format(cls.MIN_TEMPERATURE))
        if value > cls.MAX_TEMPERATURE:
            raise errors.TemperatureValidationError('Temperature cannot be above {}'.format(cls.MAX_TEMPERATURE))

    @property
    def on_rpi(self):
        return self._on_rpi

    @property
    def is_active(self):
        return self.state != State.OFF

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
        low, high = t_range
        if high < low:
            raise errors.TemperatureValidationError('Invalid range.')
        self.validate_temperature(low)
        self.validate_temperature(high)
        self._temperature_range = t_range

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
