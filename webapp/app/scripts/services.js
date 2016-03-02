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

    service.connect = function connect() {
      Pubnub.subscribe({
        channel: channel_name,
        message: function(m) {
          console.log(m);
        },
        error: function(e) {
          console.log(e)
        }
      });
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

    return service;
  });
