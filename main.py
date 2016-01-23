# -*- coding: utf-8 -*-

from thermostat.thermostat import Thermostat
from thermostat import errors


def main():
    t = Thermostat()

    # get and set current temperature
    current_temp = int(input('Enter current temperature: '))
    try:
        t.current_temp = current_temp
    except errors.ValidationErrorBase as e:
        print(e)

    # get and set user user temperature range
    user_temp_low = int(input('Enter lower bound: '))
    user_temp_high = int(input('Enter higher bound: '))
    try:
        t.user_temp_range = (user_temp_low, user_temp_high)
    except errors.TemperatureValidationError as e:
        print(e)

    t.run()


if __name__ == "__main__":
    main()
