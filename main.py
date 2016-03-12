# -*- coding: utf-8 -*-

from decimal import Decimal

from thermostat.thermostat import Thermostat
from thermostat.gui import GUI
from thermostat import errors, utils


def main():
    logger = utils.init_logging()
    utils.init_context()

    t = Thermostat()

    if utils.on_rpi():
        t.temperature_range = (Decimal(20), Decimal(22))
    else:
        # get temperatures from input
        current_temperature = Decimal(input('Enter current temperature: '))
        temp_low = Decimal(input('Enter lower bound: '))
        temp_high = Decimal(input('Enter higher bound: '))
        try:
            t.current_temperature = current_temperature
            t.temperature_range = (temp_low, temp_high)
        except errors.TemperatureValidationError as e:
            logger.error(e)

    gui = GUI(t)
    try:
        gui.run()
    except Exception as e:
        logger.error(e)
    finally:
        gui.stop()


if __name__ == "__main__":
    main()
