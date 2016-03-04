'use strict';

var Datastore = require('nedb');
var config = require('../config');


var dbInterface = {};
var db = {};
db.users = new Datastore({
  filename: config.DB_USERS_FILE,
  autoload: true
});
db.thermostats = new Datastore({
  filename: config.DB_THERMOSTATS_FILE,
  autoload: true
});

dbInterface.insertUser = function insertUser(email, password, thermostatId) {
  var doc = {
    email: email,
    password: password,
    thermostatId: thermostatId
  };
  return function(callback) {
    db.users.insert(doc, callback);
  }
};

dbInterface.getUser = function getUser(email) {
  return function(callback) {
    db.users.findOne({ email: email }, callback);
  };
};

dbInterface.insertThermostat = function insertThermostat(id) {
  var doc = {
    id: id,
    registered: false
  };
  return function(callback) {
    db.thermostats.insert(doc, callback);
  }
};

dbInterface.getThermostat = function getThermostat(id) {
  return function(callback) {
    db.thermostats.findOne({ id: id }, callback);
  };
};

dbInterface.registerThermostat = function registerThermostat(id) {
  return function(callback) {
    db.thermostats.update({ id: id }, { $set: { registered: true } }, {}, callback);
  };
};


module.exports = dbInterface;
