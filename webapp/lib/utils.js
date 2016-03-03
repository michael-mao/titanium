'use strict';

var crypto = require('crypto');


var utils = {};

utils.hashPassword = function hashPassword(password, salt) {
  return function(callback) {
    crypto.pbkdf2(password, salt, 10000, 512, 'sha512', function(err, key) {
      if(err) callback(err);
      callback(null, key.toString('base64'));
    });
  }
};

utils.generateSalt = function generateSalt() {
  return crypto.randomBytes(128).toString('base64');
};

utils.appendSalt = function appendSalt(hash, salt) {
  return hash + '::' + salt;
};

utils.extractSalt = function extractSalt(value) {
  return value.split('::')[1];
};

module.exports = utils;
