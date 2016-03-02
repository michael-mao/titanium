'use strict';

var app = angular.module('titanium', [
  'ngRoute',

  'pubnub.angular.service',

  'titaniumControllers',
  'titaniumServices'
]);

app
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
  .run(['$rootScope', '$location', 'Pubnub',
    function($rootScope, $location, Pubnub) {
      // TODO: put into config file
      Pubnub.init({
        publish_key: 'pub-c-5d83a3da-ce33-4b35-889e-85d5f3e1be17',
        subscribe_key: 'sub-c-470a1dd4-e027-11e5-bd77-02ee2ddab7fe'
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
