'use strict';

var services = angular.module('titaniumServices', []);

services
  .factory('LoginService', function($q) {
    var service = {};

    service.authenticate = function authenticate(email, password) {
      // TODO
      return $q.when();
    };

    return service;
  });
