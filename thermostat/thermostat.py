# -*- coding: utf-8 -*-

from . import errors


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Thermostat(metaclass=Singleton):
    MIN_TEMP = 0
    MAX_TEMP = 35

    def __init__(self):
        self._is_on = False
        self._current_temp = 0.0
        self._user_temp_range = (0.0, 0.0)

    def run(self):
        low, high = self.user_temp_range
        if self.current_temp < low:
            print('Thermostat is heating.')
        elif self.current_temp > high:
            print('Thermostat is cooling.')
        else:
            print('Thermostat is inactive.')

    @classmethod
    def validate_temp(cls, value):
        if value < cls.MIN_TEMP:
            raise errors.TemperatureValidationError('Temperature cannot be below {}'.format(cls.MIN_TEMP))
        if value > cls.MAX_TEMP:
            raise errors.TemperatureValidationError('Temperature cannot be above {}'.format(cls.MAX_TEMP))

    @property
    def is_on(self):
        return self._is_on

    @property
    def current_temp(self):
        return self._current_temp

    @current_temp.setter
    def current_temp(self, value):
        self.validate_temp(value)
        self._current_temp = value

    @property
    def user_temp_range(self):
        return self._user_temp_range

    @user_temp_range.setter
    def user_temp_range(self, temp_range):
        low, high = temp_range
        if high < low:
            raise errors.TemperatureValidationError('Invalid range.')
        self.validate_temp(low)
        self.validate_temp(high)
        self._user_temp_range = temp_range
