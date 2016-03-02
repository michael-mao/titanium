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
  .controller('DashboardController', ['$scope', '$location', '$interval', 'UserService', 'ControlService',
    function($scope, $location, $interval, UserService, ControlService) {
      var temperaturePoll = $interval(function() {
        if($scope.thermostatOnline) {
          ControlService.requestTemperatures();
        }
      }, 30000); // 30s;
      $scope.thermostatOnline = false;
      $scope.temperatures = ControlService.temperatures;
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

      $scope.$on('$destroy', function() {
        $interval.cancel(temperaturePoll);
      });

      $scope.$watch('temperatures.temperature_low', function(value) {
        if(value > $scope.temperatures['temperature_high']) {
          $scope.temperatures['temperature_low'] = $scope.temperatures['temperature_high'];
        }
      });

      $scope.$watch('temperatures.temperature_high', function(value) {
        if(value < $scope.temperatures['temperature_low']) {
          $scope.temperatures['temperature_high'] = $scope.temperatures['temperature_low'];
        }
      });

      ControlService.connect()
        .then(ControlService.thermostatOnline)
        .then(function success(isOnline) {
          $scope.thermostatOnline = isOnline;
          ControlService.requestTemperatures();
        });

      $scope.logout = function logout() {
        ControlService.disconnect();
        UserService.logout();
        $location.path('/login');
      };
    }
  ]);
