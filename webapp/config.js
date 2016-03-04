'use strict';

var path = require('path');


var config = {};

config.PORT = 3000;
config.DB_USERS_FILE = path.join(__dirname, '/users.db');
config.DB_THERMOSTATS_FILE = path.join(__dirname, 'thermostats.db');
config.SEND_OPTIONS = {
  root: path.join(__dirname, '/app')
};

module.exports = config;
