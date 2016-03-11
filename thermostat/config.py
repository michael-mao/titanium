# -*- coding: utf-8 -*-

import os

from decimal import Decimal


##############################
# API
##############################

# Open Weather Map
OWM_API_KEY = 'bf301adce702f7ed7a91b92a0861a56e'

# Pubnub
SUBSCRIBE_KEY = 'sub-c-470a1dd4-e027-11e5-bd77-02ee2ddab7fe'
PUBLISH_KEY = 'pub-c-5d83a3da-ce33-4b35-889e-85d5f3e1be17'
# must be globally unique
THERMOSTAT_ID = 'thermostat'


##############################
# Thermostat parameters
##############################

# timing, in seconds
UPDATE_INTERVAL = 5
OSCILLATION_DELAY = 300

# bounds for input range
MIN_TEMPERATURE = 0
MAX_TEMPERATURE = 35

# decision matrix thresholds, within range(-1, 1)
# -1              COOL_THRESHOLD      HEAT_THRESHOLD          1
# --------COOL--------|--------OFF--------|--------HEAT--------
DM_HEAT_THRESHOLD = Decimal('0.5')
DM_COOL_THRESHOLD = Decimal('-0.5')

# decision matrix parameters and their weighting, weightings must sum to 1
DM_WEIGHTINGS = {
    'internal_temperature': Decimal('0.4'),
    'external_temperature': Decimal('0.2'),
    'history_temperature': Decimal('0.2'),
    'energy_cost': Decimal('0.2'),
}


##############################
# Files and Directories
##############################

# thermostat root dir
BASE_DIR = os.path.dirname(__file__)

ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

DEFAULT_SETTINGS_FILENAME = 'default_settings.json'
SETTINGS_FILENAME = 'settings.json'
DEFAULT_HISTORY_FILENAME = 'default_history.json'
HISTORY_FILENAME = 'history.json'
