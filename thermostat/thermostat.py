# -*- coding: utf-8 -*-

from logging import getLogger
from enum import Enum, unique
from . import errors, utils


@unique
class State(Enum):
    OFF = 0
    HEAT = 1
    COOL = 2


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Thermostat(metaclass=Singleton):
    MIN_TEMPERATURE = 0
    MAX_TEMPERATURE = 35

    def __init__(self):
        self._current_temperature = 0.0
        self._temperature_range = (0.0, 0.0)
        self._on_rpi = utils.on_rpi()
        self.state = State.OFF
        self.logger = getLogger('app.thermostat')

    def run(self):
        while True:
            self.update_state()

    def update_state(self):
        low, high = self.temperature_range
        if self.current_temperature < low:
            self.logger.debug('Thermostat is heating.')
            self.state = State.HEAT
        elif self.current_temperature > high:
            self.logger.debug('Thermostat is cooling.')
            self.state = State.COOL
        else:
            self.logger.debug('Thermostat is inactive.')
            self.state = State.OFF

    @classmethod
    def validate_temperature(cls, value):
        if value < cls.MIN_TEMPERATURE:
            raise errors.TemperatureValidationError('Temperature cannot be below {}'.format(cls.MIN_TEMPERATURE))
        if value > cls.MAX_TEMPERATURE:
            raise errors.TemperatureValidationError('Temperature cannot be above {}'.format(cls.MAX_TEMPERATURE))

    @property
    def is_active(self):
        return self.state != State.OFF

    @property
    def current_temperature(self):
        return self._current_temperature

    @current_temperature.setter
    def current_temperature(self, value):
        self.validate_temperature(value)
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
