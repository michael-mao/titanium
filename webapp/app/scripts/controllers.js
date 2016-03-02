'use strict';

var controllers = angular.module('titaniumControllers', [
  'ui.bootstrap',
  'ui.knob'
]);

controllers
  .controller('LoginController', ['$scope', '$rootScope', '$location', 'UserService',
    function($scope, $rootScope, $location, UserService) {
      // check if already logged in
      if($rootScope.currentUser) {
        $location.path('/dashboard');
      }

      $scope.submit = function submit(user) {
        UserService.login(user.email, user.password)
          .then(function success() {
            console.log('login successful');
            $rootScope.currentUser = angular.copy($scope.user);
            $location.path('/dashboard');
          }, function error() {
            console.log('login failed');
          });
      }
    }
  ]);

controllers
  .controller('DashboardController', ['$scope', '$location', 'UserService', 'ControlService',
    function($scope, $location, UserService, ControlService) {
      $scope.currentTemperature = 22;
      $scope.temperatureLow = 18;
      $scope.temperatureHigh = 24;
      $scope.ctKnobOptions = {
        size: 200,
        unit: 'C',
        barWidth: 40,
        trackColor: 'rgba(255,0,0,.1)',
        max: 35,
        readOnly: true,
        dynamicOptions: true
      };
      $scope.trKnobOptions = {
        scale: {
          enabled: true,
          type: 'dots',
          color: 'rgba(255,0,0,.2)',
          width: 2,
          quantity: 35,
          spaceWidth: 10
        },
        unit: 'C',
        barWidth: 40,
        trackWidth: 25,
        trackColor: 'rgba(0,0,0,.1)',
        prevBarColor: 'rgba(0,0,0,.2)',
        max: 35,
        displayPrevious: true,
        dynamicOptions: true
      };

      $scope.$watch('temperatureLow', function(value) {
        if(value > $scope.temperatureHigh) {
          $scope.temperatureLow = $scope.temperatureHigh;
        }
      });

      $scope.$watch('temperatureHigh', function(value) {
        if(value < $scope.temperatureLow) {
          $scope.temperatureHigh = $scope.temperatureLow;
        }
      });

      ControlService.connect()
        .then(ControlService.thermostatOnline)
        .then(function success(isOnline) {
          $scope.thermostatOnline = isOnline;
        });

      $scope.logout = function logout() {
        ControlService.disconnect();
        UserService.logout();
        $location.path('/login');
      };
    }
  ]);
