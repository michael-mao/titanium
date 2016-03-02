'use strict';

var services = angular.module('titaniumServices', []);

services
  .factory('UserService', function($q) {
    var service = {};

    service.login = function login(email, password) {
      // TODO
      return $q.when()
    };

    service.logout = function logout() {
      // TODO
    };

    return service;
  });

services
  .factory('ControlService', function($q, config, Pubnub) {
    var service = {};

    service.temperatures = {
      'current_temperature': 0,
      'temperature_low': 0,
      'temperature_high': 0
    };
    service.settings = {};

    service.parseMessage = function parseMessage(message) {
      if(message.action == 'temperature_data') {
        // only initialize range
        if(!service.temperatures['temperature_low'] && !service.temperatures['temperature_high']) {
          angular.extend(service.temperatures, message.data);
        } else {
          service.temperatures['current_temperature'] = message.data['current_temperature'];
        }
      } else if(message.action == 'settings_data') {
        service.extend(service.settings, message.data);
      } else {
        // unexpected message type
        console.log(message);
      }
    };

    service.connect = function connect() {
      var deferred = $q.defer();
      Pubnub.subscribe({
        channel: config.CHANNEL_NAME,
        message: service.parseMessage,
        connect: deferred.resolve,
        error: deferred.reject
      });

      return deferred.promise;
    };

    service.disconnect = function disconnect() {
      Pubnub.unsubscribe({
        channel: config.CHANNEL_NAME
      });
    };

    service.thermostatOnline = function thermostatOnline() {
      var deferred = $q.defer();
      Pubnub.here_now({
        channel: config.CHANNEL_NAME,
        callback: function(m) {
          deferred.resolve(m.uuids.indexOf(config.THERMOSTAT_ID) > -1);
        },
        error: deferred.reject
      });

      return deferred.promise;
    };

    service.requestTemperatures = function requestTemperatures() {
      var data = {
        action: 'request_temperatures'
      };
      Pubnub.publish({
        channel: config.CHANNEL_NAME,
        message: data
      });
    };

    return service;
  });
