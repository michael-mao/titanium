# -*- coding: utf-8 -*-

import platform
import os
import logging
import json
import socket
import datetime


# project root dir
BASE_DIR = os.path.dirname(__file__)


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


def init_settings():
    """ Set up settings file.

    If no existing file found, create a new file using default settings.
    """
    logger = logging.getLogger('app.utils')
    default_filename = 'default_settings.json'
    default_filepath = os.path.abspath(os.path.join(BASE_DIR, '..', default_filename))
    filename = 'settings.json'
    filepath = os.path.abspath(os.path.join(BASE_DIR, '..', filename))

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
    """
    logger = logging.getLogger('app.utils')
    default_filename = 'default_history.json'
    default_filepath = os.path.abspath(os.path.join(BASE_DIR, '..', default_filename))
    filename = 'history.json'
    filepath = os.path.abspath(os.path.join(BASE_DIR, '..', filename))

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

    logger.debug('settings: ' + json.dumps(history))
    return history


def connected_to_internet(host='8.8.8.8', port=53, timeout=1):
    """ Ping a host to determine if internet connection available.

    :param host: 8.8.8.8 (google-public-dns-a.google.com)
    :param port: 53/tcp
    :param timeout: in seconds
    :return boolean
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
