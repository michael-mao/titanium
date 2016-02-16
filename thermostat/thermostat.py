# -*- coding: utf-8 -*-

import time

from logging import getLogger
from functools import reduce
from enum import Enum, unique

from . import errors, utils, weather, sensor


@unique
class State(Enum):
    OFF = 0
    HEAT = 1
    COOL = 2

    def __str__(self):
        return self.name


class Thermostat(metaclass=utils.Singleton):
    # bounds for input range
    MIN_TEMPERATURE = 0
    MAX_TEMPERATURE = 35

    # decision matrix thresholds, within range(-1, 1)
    # -1              COOL_THRESHOLD      HEAT_THRESHOLD          1
    # --------COOL--------|--------OFF--------|--------HEAT--------
    DM_HEAT_THRESHOLD = 0.5
    DM_COOL_THRESHOLD = -0.5

    # decision matrix parameters and their weighting, weightings must sum to 1
    DM_WEIGHTINGS = {
        'internal_temperature': 0.4,
        'external_temperature': 0.2,
        'history_temperature': 0.2,
        'energy_price': 0.2,
    }

    def __init__(self):
        self._settings = utils.init_settings()
        self._current_temperature = 0.0
        self._temperature_range = (0.0, 0.0)
        self._on_rpi = utils.on_rpi()
        self.temperature_increment = 0.5
        self.update_interval = 5
        self.state = State.OFF
        self.logger = getLogger('app.thermostat')

    def run(self):
        """ Entry method.

        Main event loop is here.
        """
        # initialize sensor
        if self.on_rpi:
            sensor.init_sensor()
            self.current_temperature = sensor.read_temperature()

        # daemon thread to fetch weather data
        weather_thread = weather.WeatherAPI(
            self._settings['temperature_unit'],
            self._settings['city'],
            self._settings['country_code'],
        )
        weather_thread.start()

        while True:
            self.update_state()
            time.sleep(self.update_interval)

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
            # within range, use decision matrix
            params_list = list()
            params_list.append(('internal_temperature', self.temperature_range_equilibrium - self.current_temperature))
            # TODO: weather, history, price
            matrix = self.build_decision_matrix(params_list)
            self.state = self.evaluate_decision_matrix(matrix)

        self.logger.debug('thermostat state updated to {0}'.format(self.state))

    @classmethod
    def build_decision_matrix(cls, params_list):
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
        total_weight = 0.0
        for parameter, rating in params_list:
            weight = cls.DM_WEIGHTINGS.get(parameter)
            if weight is not None:
                matrix[parameter] = (weight, rating)
                total_weight += weight

        # if there are missing parameter ratings, recalculate weightings
        if len(matrix) != len(cls.DM_WEIGHTINGS):
            for key, value in matrix.items():
                weight, rating = value
                matrix[key] = (weight/total_weight, rating)

        return matrix

    @classmethod
    def evaluate_decision_matrix(cls, matrix):
        """ Evaluates decision matrix.

        Calculates the total score based on weighting and rating of each parameter.
        Determines new thermostat state based on total score and preset thresholds.

        Normalizes ratings to be within range(-1, 1) before multiplying weight.

        :param matrix: decision matrix
        :return: new thermostat state
        """
        total_score = 0.0
        total_rating = reduce(lambda x, y: x+y, [value[1] for value in matrix.values()])

        for key, value in matrix.items():
            score = reduce(lambda weight, rating: weight*(rating/total_rating), value)
            total_score += score

        new_state = State.OFF
        if total_score > cls.DM_HEAT_THRESHOLD:
            new_state = State.HEAT
        elif total_score < cls.DM_COOL_THRESHOLD:
            new_state = State.COOL
        print('Total score is {}'.format(total_score))
        return new_state

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
    def temperature_range_equilibrium(self):
        # biased towards range ceiling
        low, high = self.temperature_range
        difference = high - low
        return (difference / 4) + difference
