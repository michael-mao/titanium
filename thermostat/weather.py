# -*- coding: utf-8 -*-

import threading
import time

import pyowm

from logging import getLogger
from . import utils, config, errors


class WeatherAPI(threading.Thread, metaclass=utils.Singleton):
    """
    Class to fetch weather data in background as a daemon thread. Uses Open Weather Map API.
    Saves current weather data in the instance. Forecast data is discarded after initial fetch.
    """

    def __init__(self, unit, city, country_code):
        super().__init__()
        self._data = {
            'temperature': 0.0,
            'temperature_high': 0.0,
            'temperature_low': 0.0,
            'humidity': 0,
        }
        self._location = {
            'city': city,
            'country_code': country_code
        }
        self._unit = unit  # 'celsius' or 'fahrenheit'
        self.daemon = True
        self.logger = getLogger('app.weather')
        self.fetch_interval = 1800  # 30min
        self.owm = pyowm.OWM(config.OWM_API_KEY)  # open weather map client

    def run(self):
        while True:
            self.get_current_weather()
            time.sleep(self.fetch_interval)

    def get_current_weather(self):
        """
        Fetch current weather and updates stored data.

        :return: Tuple of current weather (temperature, humidity)
        """
        self.logger.debug('fetching current weather')
        observation = self.owm.weather_at_place(self.location)
        weather = observation.get_weather()

        t = weather.get_temperature(self.unit)
        self._data['temperature'] = t['temp']
        self._data['temperature_high'] = t['temp_max']
        self._data['temperature_low'] = t['temp_min']
        self._data['humidity'] = weather.get_humidity()

        self.logger.debug('current weather for {0}: {1}'.format(self.location, self._data))
        return self.temperature, self.humidity

    def get_short_forecast(self):
        """
        Fetch 3 hour forecasts for next 5 days. Data not saved.

        :return: List of tuples (ISO datetime, temperature)
        """
        self.logger.debug('fetching short forecast')
        observation = self.owm.three_hours_forecast(self.location)
        forecast = observation.get_forecast()

        temperature_forecast = [(w.get_reference_time('iso'), w.get_temperature(self.unit)['temp']) for w in forecast]
        self.logger.debug('short forecast for {0}: {1}'.format(self.location, temperature_forecast))
        return temperature_forecast

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, u):
        if u != 'celsius' and u != 'fahrenheit':
            raise errors.UnitValidationError()
        self._unit = u

    @property
    def location(self):
        return self._location['city'] + ',' + self._location['country_code']

    @location.setter
    def location(self, l):
        # TODO: validation
        self._location['city'], self._location['country_code'] = l

    @property
    def temperature(self):
        return self._data['temperature']

    @property
    def humidity(self):
        return self._data['humidity']
