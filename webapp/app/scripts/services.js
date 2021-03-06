'use strict';

var services = angular.module('titaniumServices', []);

services
  .factory('UserService', function($rootScope, $http, $q, localStorageService) {
    var service = {};

    service.login = function login(email, password) {
      var data = {
        email: email,
        password: password
      };
      return $http.post('/api/authenticate', data)
        .then(function success(data) {
          $rootScope.currentUser = angular.copy(data.data);
          // TODO: set expiration for login
          localStorageService.set('user', $rootScope.currentUser);
          return $q.when($rootScope.currentUser);
        });
    };

    service.logout = function logout() {
      $rootScope.currentUser = null;
      localStorageService.remove('user');
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
    service.status = {
      mode: null,
      status: null
    };
    service.settings = {};
    service.history = [];

    service.parseMessage = function parseMessage(message) {
      if(message.action == 'temperature_data') {
        if(message.data['current_temperature']) {
          service.temperatures['current_temperature'] = message.data['current_temperature'];
        }
        if(message.data['temperature_low']) {
          service.temperatures['temperature_low'] = message.data['temperature_low'];
        }
        if(message.data['temperature_high']) {
          service.temperatures['temperature_high'] = message.data['temperature_high'];
        }
      } else if(message.action == 'mode_data') {
        service.status.mode = message.data['mode'];
      } else if(message.action == 'state_data') {
        service.status.state = message.data['state'];
      } else if(message.action == 'settings_data') {
        angular.extend(service.settings, message.data);
      } else if(message.action == 'history_data') {
        service.history = message.data;
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

    service.requestTemperatures = function requestTemperatures(all) {
      var data = {
        action: 'request_temperatures',
        value: (all ? 'all' : 'current')
      };
      Pubnub.publish({
        channel: $rootScope.currentUser.thermostat_id,
        message: data
      });
    };

    service.requestMode = function requestMode() {
      var data = {
        action: 'request_mode'
      };
      Pubnub.publish({
        channel: $rootScope.currentUser.thermostat_id,
        message: data
      });
    };

    service.requestSettings = function requestSettings() {
      var data = {
        action: 'request_settings'
      };
      Pubnub.publish({
        channel: $rootScope.currentUser.thermostat_id,
        message: data
      });
    };

    service.requestHistory = function requestHistory() {
      var data = {
        action: 'request_history'
      };
      Pubnub.publish({
        channel: $rootScope.currentUser.thermostat_id,
        message: data
      });
    };

    service.updateSetting = function updateSetting(name, value) {
      var data = {
        action: 'update_setting',
        setting_name: name,
        setting_value: value
      };
      Pubnub.publish({
        channel: $rootScope.currentUser.thermostat_id,
        message: data
      });
    };

    service.updateMode = function updateMode(mode) {
      var data = {
        action: 'update_mode',
        mode: mode
      };
      Pubnub.publish({
        channel: $rootScope.currentUser.thermostat_id,
        message: data
      });
    };

    service.updateTemperatureRange = function updateTemperatureRange(low, high) {
      var data = {
        action: 'update_temperature_range',
        temperature_low: low,
        temperature_high: high
      };
      Pubnub.publish({
        channel: $rootScope.currentUser.thermostat_id,
        message: data
      });
    };

    return service;
  });
