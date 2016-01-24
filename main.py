# -*- coding: utf-8 -*-

import logging

from thermostat.thermostat import Thermostat
from thermostat import errors


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


def main():
    logger = init_logging()

    t = Thermostat()

    # get and set current temperature
    current_temperature = int(input('Enter current temperature: '))
    try:
        t.current_temperature = current_temperature
    except errors.ValidationErrorBase as e:
        logger.error(e)

    # get and set user user temperature range
    temp_low = int(input('Enter lower bound: '))
    temp_high = int(input('Enter higher bound: '))
    try:
        t.temperature_range = (temp_low, temp_high)
    except errors.TemperatureValidationError as e:
        logger.error(e)
    else:
        t.run()


if __name__ == "__main__":
    main()
