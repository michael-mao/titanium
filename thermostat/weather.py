# -*- coding: utf-8 -*-

import threading
import time

from logging import getLogger
from . import utils


class WeatherAPI(threading.Thread, metaclass=utils.Singleton):

    # TODO: pass in location parameter
    def __init__(self):
        super().__init__()
        self._data = {
            'temperature': 0.0,
            'humidity': 0,
        }
        self.daemon = True
        self.logger = getLogger('app.weather')
        self.fetch_interval = 1800  # 30min

    def run(self):
        while True:
            self.get_data()
            time.sleep(self.fetch_interval)

    def get_data(self):
        # TODO
        self.logger.debug('fetching weather data')

    @property
    def temperature(self):
        return self._data['temperature']

    @temperature.setter
    def temperature(self, t):
        self._data['temperature'] = t

    @property
    def humidity(self):
        return self._data['humidity']

    @humidity.setter
    def humidity(self, h):
        self._data['humidity'] = h
