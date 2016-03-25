# -*- coding: utf-8 -*-

import threading
import time
import datetime

import pyowm

from decimal import Decimal
from logging import getLogger

from . import utils, config, errors


class WeatherAPI(threading.Thread, metaclass=utils.Singleton):
    """
    Class to fetch weather data in background as a daemon thread. Uses Open Weather Map API.
    Saves current weather data in the instance. Forecast data is discarded after initial fetch.

    See http://openweathermap.org/weather-conditions for possible weather conditions and icons.
    """
    DEFAULT_FETCH_INTERVAL = 1800  # 30 min

    def __init__(self, unit, city, country_code):
        super().__init__()
        self._data = {
            'temperature': Decimal(0),
            'temperature_high': Decimal(0),
            'temperature_low': Decimal(0),
            'humidity': 0,
            'status': 'N/A',
        }
        self._location = {
            'city': city,
            'country_code': country_code
        }
        self._unit = unit  # 'celsius' or 'fahrenheit'
        self._last_updated = datetime.datetime(datetime.MINYEAR, 1, 1)
        self.daemon = True
        self.logger = getLogger('app.weather')
        self.fetch_interval = self.DEFAULT_FETCH_INTERVAL
        self.owm = pyowm.OWM(config.OWM_API_KEY)  # open weather map client

    def run(self):
        while True:
            self.get_current_weather()
            time.sleep(self.fetch_interval)

    def get_current_weather(self):
        """
        Fetch current weather and updates stored data. Keeps track of most recent successful update with a timestamp.

        :return: Tuple of current weather (temperature, humidity)
        """
        self.logger.debug('fetching current weather')

        try:
            observation = self.owm.weather_at_place(self.location)
        except Exception as e:
            # reduce fetch interval if exception is connection related
            if not utils.connected_to_internet():
                self.logger.info('no internet connection')
                self.fetch_interval = 6000  # 10 min
            elif not self.owm.is_API_online():
                self.logger.info('owm api unavailable')
                self.fetch_interval = 6000  # 10 min
            else:
                raise e
        else:
            self.fetch_interval = self.DEFAULT_FETCH_INTERVAL
            weather = observation.get_weather()
            t = weather.get_temperature(self.unit)

            self._data['temperature'] = Decimal(str(t['temp']))  # convert to str first so precision is not messed up
            self._data['temperature_high'] = Decimal(str(t['temp_max']))
            self._data['temperature_low'] = Decimal(str(t['temp_min']))
            self._data['humidity'] = weather.get_humidity()
            self._data['status'] = weather.get_status()
            self._last_updated = datetime.datetime.now()
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
    def status(self):
        return self._data['status'].lower()

    @property
    def temperature(self):
        return self._data['temperature']

    @property
    def humidity(self):
        return self._data['humidity']

    @property
    def last_updated(self):
        return self._last_updated
