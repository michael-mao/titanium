'use strict';

var path = require('path');


var config = {};

config.PORT = 3000;
config.DB_FILE = path.join(__dirname, '/users.db');
config.SEND_OPTIONS = {
  root: path.join(__dirname, '/app')
};

module.exports = config;
