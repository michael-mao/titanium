# -*- coding: utf-8 -*-

import platform
import os
import logging
import json


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
