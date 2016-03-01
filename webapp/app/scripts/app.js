'use strict';

var app = angular.module('titanium', [
  'ngRoute',

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
  .run(function($rootScope, $location) {
    $rootScope.$on('$routeChangeStart', function(event, next, current) {
      if(!$rootScope.currentUser) {
        if(next.templateUrl !== 'views/login.html') {
          $location.path('/login');
        }
      }
    });
  });
