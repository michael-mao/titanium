# -*- coding: utf-8 -*-

from decimal import Decimal

from thermostat.thermostat import Thermostat
from thermostat.gui import GUI
from thermostat import errors, utils


def main():
    logger = utils.init_logging()
    utils.init_context()

    gui = None
    t = Thermostat()

    # get and set current temperature
    current_temperature = Decimal(input('Enter current temperature: '))
    try:
        t.current_temperature = current_temperature
    except errors.ValidationErrorBase as e:
        logger.error(e)

    # get and set user user temperature range
    temp_low = Decimal(input('Enter lower bound: '))
    temp_high = Decimal(input('Enter higher bound: '))
    try:
        t.temperature_range = (temp_low, temp_high)
    except errors.TemperatureValidationError as e:
        logger.error(e)
    else:
        try:
            gui = GUI(t)
        finally:
            if gui:
                gui.stop()


if __name__ == "__main__":
    main()
