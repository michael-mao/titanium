'use strict';

var Datastore = require('nedb');
var config = require('../config');


var dbInterface = {};
var db = new Datastore({
  filename: config.dbFile,
  autoload: true
});

dbInterface.insertUser = function insertUser(email, password) {
  var doc = {
    email: email,
    password: password
  };
  return function(callback) {
    db.insert(doc, callback);
  }
};

dbInterface.getUser = function getUser(email) {
  return function(callback) {
    db.findOne({ email: email }, callback);
  };
};


module.exports = dbInterface;
