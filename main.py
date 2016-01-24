# -*- coding: utf-8 -*-

from thermostat.thermostat import Thermostat
from thermostat import errors


def main():
    t = Thermostat()

    # get and set current temperature
    current_temperature = int(input('Enter current temperature: '))
    try:
        t.current_temperature = current_temperature
    except errors.ValidationErrorBase as e:
        print(e)

    # get and set user user temperature range
    temp_low = int(input('Enter lower bound: '))
    temp_high = int(input('Enter higher bound: '))
    try:
        t.temperature_range = (temp_low, temp_high)
    except errors.TemperatureValidationError as e:
        print(e)
    else:
        t.run()


if __name__ == "__main__":
    main()
