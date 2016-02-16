# -*- coding: utf-8 -*-

import platform
import os
import logging
import json
import socket
import datetime
import decimal


# project root dir
BASE_DIR = os.path.dirname(__file__)
DEFAULT_SETTINGS_FILENAME = 'default_settings.json'
SETTINGS_FILENAME = 'settings.json'
DEFAULT_HISTORY_FILENAME = 'default_history.json'
HISTORY_FILENAME = 'history.json'


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
    default_filepath = os.path.abspath(os.path.join(BASE_DIR, '..', DEFAULT_SETTINGS_FILENAME))
    filepath = os.path.abspath(os.path.join(BASE_DIR, '..', SETTINGS_FILENAME))

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
    default_filepath = os.path.abspath(os.path.join(BASE_DIR, '..', DEFAULT_HISTORY_FILENAME))
    filepath = os.path.abspath(os.path.join(BASE_DIR, '..', HISTORY_FILENAME))

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

    filepath = os.path.abspath(os.path.join(BASE_DIR, '..', filename))

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
