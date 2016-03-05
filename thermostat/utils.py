# -*- coding: utf-8 -*-

import platform
import os
import logging
import json
import socket
import datetime
import decimal
import urllib.request

from enum import Enum, unique

from . import config


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


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def on_rpi():
    return platform.system() == 'Linux' and platform.node() == 'raspberrypi'


def init_logging():
    """ Set up logging.

    Logs INFO level or higher to file and DEBUG level or higher to console.

    :return: logger instance
    """
    formatter = logging.Formatter('%(asctime)s[%(levelname)s][%(name)s.%(funcName)s] %(message)s')
    fh = logging.FileHandler('app.log')
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)

    logger = logging.getLogger('app')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def init_context():
    """ Context setup for modules.

    :return: None
    """
    # ensures all threads use same context
    decimal.DefaultContext.prec = 9
    decimal.DefaultContext.rounding = decimal.ROUND_HALF_UP  # >=0.5 rounds away from zero
    decimal.setcontext(decimal.DefaultContext)


def init_settings():
    """ Set up settings file.

    If no existing file found, create a new file using default settings.

    :return: dictionary of settings
    """
    logger = logging.getLogger('app.utils')
    default_filepath = os.path.abspath(os.path.join(config.BASE_DIR, '..', config.DEFAULT_SETTINGS_FILENAME))
    filepath = os.path.abspath(os.path.join(config.BASE_DIR, '..', config.SETTINGS_FILENAME))

    if os.path.isfile(filepath) is True:
        logger.debug('loading existing settings file')
        with open(filepath) as f:
            settings = json.load(f)
    else:
        logger.debug('creating new settings file')
        with open(default_filepath) as f:
            settings = json.load(f)
        with open(filepath, 'w') as f:
            json.dump(settings, f)

    logger.debug('settings: ' + json.dumps(settings))
    return settings


def init_history():
    """ Set up history file.

    History divided into 15min blocks for each day of the week.

    :return: dictionary of history
    """
    logger = logging.getLogger('app.utils')
    default_filepath = os.path.abspath(os.path.join(config.BASE_DIR, '..', config.DEFAULT_HISTORY_FILENAME))
    filepath = os.path.abspath(os.path.join(config.BASE_DIR, '..', config.HISTORY_FILENAME))

    if os.path.isfile(filepath) is True:
        logger.debug('loading existing history file')
        with open(filepath) as f:
            history = json.load(f)
    else:
        logger.debug('creating new history file')
        with open(default_filepath) as f:
            history = json.load(f)
        with open(filepath, 'w') as f:
            json.dump(history, f)

    logger.debug('history: ' + json.dumps(history))
    return history


def write_to_file(filename, data):
    """ Write history to file.

    :param data: dictionary
    :return: None
    """
    if not isinstance(filename, str) or not isinstance(data, dict):
        raise TypeError('filename must be string and data must be dict')

    filepath = os.path.abspath(os.path.join(config.BASE_DIR, '..', filename))

    # warning, overwrites existing file
    with open(filepath, 'w') as f:
        json.dump(data, f)


def connected_to_internet(host='8.8.8.8', port=53, timeout=1):
    """ Ping a host to determine if internet connection available.

    :param host: 8.8.8.8 (google-public-dns-a.google.com)
    :param port: 53/tcp
    :param timeout: in seconds
    :return: boolean
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM,).connect((host, port))
        return True
    except socket.error:
        pass
    return False


def round_time(dt, round_to=900):
    """ Round datetime to nearest multiple of round_to.

    Used by history feature.

    :param dt: datetime.datetime object
    :param round_to: in seconds, default 15 min
    :return: rounded datetime.datetime object
    """
    if not isinstance(dt, datetime.datetime):
        return None

    seconds = (dt - dt.min).seconds
    rounding = (seconds + round_to / 2) // round_to * round_to  # // is floor division
    return dt + datetime.timedelta(0, rounding-seconds, -dt.microsecond)


def get_geolocation():
    """ Get current geolocation based on ip address.

    :return: dictionary
    """
    IP_ENDPOINT = 'http://ip.42.pl/raw'
    GEOLOCATION_ENDPOINT = 'http://ip-api.com/json/{ip}?fields=country,countryCode,region,regionName,city,lat,lon,timezone,status'

    # get ip address
    with urllib.request.urlopen(IP_ENDPOINT) as response:
        ip_address = response.read().decode()
    # get geolocation
    with urllib.request.urlopen(GEOLOCATION_ENDPOINT.format(ip=ip_address)) as response:
        raw_data = response.read().decode()

    geolocation = json.loads(raw_data)
    return geolocation if geolocation['status'] == 'success' else None


def filter_settings(settings):
    """ Filter settings.

    :param settings: dictionary of raw settings
    :return: dictionary of filtered settings
    """
    return {name: value for name, value in settings.items() if not name.startswith('_')}


def prettify_settings(settings):
    """ Prettify settings for display.

    Flattens nested key, values. Only supports depth of 2 for nesting.
    Converts values to strings, maintains lists but converts elements.

    :param settings: dictionary of raw settings
    :return: dictionary of prettified settings
    """
    filtered = filter_settings(settings)
    pretty = {}
    for name, value in filtered.items():
        pretty_name = name.replace('_', ' ').title()
        if isinstance(value, dict):
            for subname, subvalue in value.items():
                combined_name = pretty_name + ' ' + subname.replace('_', ' ').title()
                pretty[combined_name] = subvalue
        else:
            pretty_value = [str(item) for item in value] if isinstance(value, list) else str(value)
            pretty[pretty_name] = pretty_value

    return pretty


# TODO: what the hell is this garbage, redo when it's not 2AM
def unprettify_setting_name(settings, pretty_name, newValue):
    raw_name = pretty_name.replace(' ', '_').lower()
    for name, value in settings.items():
        if name == raw_name:
            return (name, newValue)

        if name in raw_name:
            updatedValue = {}
            for subname, subvalue in value.items():
                if raw_name.endswith(subname):
                    updatedValue[subname] = newValue
                else:
                    updatedValue[subname] = value[subname]
            return (name, updatedValue)