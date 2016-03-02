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
  .factory('ControlService', function($q, Pubnub) {
    var service = {};
    var channel_name = 'control';
    var thermostat_id = 'thermostat';

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
        channel: channel_name,
        message: service.parseMessage,
        connect: deferred.resolve,
        error: deferred.reject
      });

      return deferred.promise;
    };

    service.disconnect = function disconnect() {
      Pubnub.unsubscribe({
        channel: channel_name
      });
    };

    service.thermostatOnline = function thermostatOnline() {
      var deferred = $q.defer();
      Pubnub.here_now({
        channel: channel_name,
        callback: function(m) {
          deferred.resolve(m.uuids.indexOf(thermostat_id) > -1);
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
        channel: channel_name,
        message: data
      });
    };

    return service;
  });
