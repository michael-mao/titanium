# -*- coding: utf-8 -*-

import platform


def on_rpi():
    return platform.system() == 'Linux' and platform.node() == 'raspberrypi'
