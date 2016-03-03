'use strict';

var app = angular.module('titanium', [
  'ngRoute',

  'pubnub.angular.service',

  'titaniumControllers',
  'titaniumServices'
]);

app
  .constant('config', {
    MIN_TEMPERATURE: 0,
    MAX_TEMPERATURE: 35,

    PUBLISH_KEY: 'pub-c-5d83a3da-ce33-4b35-889e-85d5f3e1be17',
    SUBSCRIBE_KEY: 'sub-c-470a1dd4-e027-11e5-bd77-02ee2ddab7fe',
    CHANNEL_NAME: 'control',
    THERMOSTAT_ID: 'thermostat'
  })
  .config(['$routeProvider', '$locationProvider',
    function($routeProvider, $locationProvider) {
      $routeProvider
        .when('/login', {
          templateUrl: 'views/login.html',
          controller: 'LoginController'
        })
        .when('/dashboard', {
          templateUrl: 'views/dashboard.html',
          controller: 'DashboardController'
        })
        .otherwise({
          redirectTo: '/dashboard'
        });

      $locationProvider.html5Mode(true);
    }
  ])
  .run(['$rootScope', '$location', '$http', 'config', 'Pubnub',
    function($rootScope, $location, $http, config, Pubnub) {
      $http.defaults.headers.common = {
        'Content-Type': 'application/json'
      };

      Pubnub.init({
        publish_key: config.PUBLISH_KEY,
        subscribe_key: config.SUBSCRIBE_KEY
      });

      $rootScope.$on('$routeChangeStart', function(event, next, current) {
        if(!$rootScope.currentUser) {
          if(next.templateUrl !== 'views/login.html') {
            //$location.path('/login');
          }
        }
      });
    }
  ]);
