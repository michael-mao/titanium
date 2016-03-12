'use strict';

var app = angular.module('titanium', [
  'ngRoute',
  'ngMessages',
  'ngAnimate',

  'LocalStorageModule',
  'pubnub.angular.service',

  'titaniumControllers',
  'titaniumServices'
]);

app
  .constant('config', {
    MIN_TEMPERATURE: 0,
    MAX_TEMPERATURE: 35,

    PUBLISH_KEY: 'pub-c-5d83a3da-ce33-4b35-889e-85d5f3e1be17',
    SUBSCRIBE_KEY: 'sub-c-470a1dd4-e027-11e5-bd77-02ee2ddab7fe'
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
        .when('/profile', {
          templateUrl: 'views/profile.html',
          controller: 'ProfileController'
        })
        .when('/analytics', {
          templateUrl: 'views/analytics.html',
          controller: 'AnalyticsController'
        })
        .when('/help', {
          templateUrl: 'views/help.html',
          controller: 'HelpController'
        })
        .otherwise({
          redirectTo: '/dashboard'
        });

      $locationProvider.html5Mode(true);
    }
  ])
  .run(['$rootScope', '$location', '$http', '$templateCache', 'config', 'Pubnub', 'localStorageService',
    function($rootScope, $location, $http, $templateCache, config, Pubnub, localStorageService) {
      $http.defaults.headers.common = {
        'Content-Type': 'application/json'
      };
      $http.get('views/errorMessages.html')
        .then(function(data) {
          $templateCache.put('errorMessages', data.data);
        });

      Pubnub.init({
        publish_key: config.PUBLISH_KEY,
        subscribe_key: config.SUBSCRIBE_KEY
      });

      $rootScope.thermostatOnline = false;
      $rootScope.currentUser = localStorageService.get('user');
      $rootScope.$on('$routeChangeStart', function(event, next, current) {
        if(!$rootScope.currentUser) {
          if(next.templateUrl !== 'views/login.html') {
            $location.path('/login');
          }
        }
      });
    }
  ]);


app.directive("compare", function() {
  return {
    require: "ngModel",
    scope: {
      otherModelValue: "=compare"
    },
    link: function(scope, element, attributes, ngModel) {
      ngModel.$validators.compare = function(modelValue) {
        return modelValue == scope.otherModelValue;
      };

      scope.$watch("otherModelValue", function() {
        ngModel.$validate();
      });
    }
  };
});



