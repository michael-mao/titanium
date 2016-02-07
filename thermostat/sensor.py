# -*- coding: utf-8 -*-

import os
import glob

from logging import getLogger


logger = getLogger('app.sensor')


# TODO: catch exceptions/errors
def init_sensor():
    os.system('sudo modprobe w1-gpio')
    os.system('sudo modprobe w1-therm')
    logger.info("DS18B20 sensor ready")


def read_temperature():
    device_dir = glob.glob('/sys/bus/w1/devices/28-0315909d1dff')
    device = device_dir[0] + '/w1_slave'

    with open(device, 'r') as f:
        sensor = f.readlines()

    # parse results from the file
    crc = sensor[0].split()[-1]
    temperature = float(sensor[1].split()[-1].strip('t='))
    temperature = (temperature/1000)

    # TODO: what is this
    if 'YES' in crc:
        logger.debug('sensor reading is {0}C'.format(temperature))
        return temperature
    else:
        logger.error('sensor CRC check failed')
