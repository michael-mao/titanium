'use strict';

var services = angular.module('titaniumServices', []);

services
  .factory('UserService', function($rootScope, $http) {
    var service = {};

    service.login = function login(email, password) {
      var data = {
        email: email,
        password: password
      };
      return $http.post('/api/authenticate', data);
    };

    service.logout = function logout() {
      $rootScope.currentUser = null;
    };

    service.createUser = function createUser(email, password, thermostatId) {
      var data = {
        email: email,
        password: password,
        thermostat_id: thermostatId
      };
      return $http.post('/api/user', data);
    };

    service.getUser = function getUser(email) {
      var query = '?email=' + encodeURIComponent(email);
      return $http.get('/api/user' + query);
    };

    return service;
  });

services
  .factory('ControlService', function($rootScope, $q, Pubnub) {
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
        channel: $rootScope.currentUser.thermostat_id,
        message: service.parseMessage,
        connect: deferred.resolve,
        error: deferred.reject
      });

      return deferred.promise;
    };

    service.disconnect = function disconnect() {
      Pubnub.unsubscribe({
        channel: $rootScope.currentUser.thermostat_id
      });
    };

    service.thermostatOnline = function thermostatOnline() {
      var deferred = $q.defer();
      Pubnub.here_now({
        channel: $rootScope.currentUser.thermostat_id,
        callback: function(m) {
          deferred.resolve(m.uuids.indexOf($rootScope.currentUser.thermostat_id) !== -1);
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
        channel: $rootScope.currentUser.thermostat_id,
        message: data
      });
    };

    return service;
  });
