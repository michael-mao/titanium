'use strict';

var controllers = angular.module('titaniumControllers', [
  'ui.bootstrap',
  'ui.knob'
]);

controllers
  .controller('LoginController', ['$scope', '$rootScope', '$location', '$uibModal', 'UserService',
    function($scope, $rootScope, $location, $uibModal, UserService) {
      // check if already logged in
      if($rootScope.currentUser) {
        $location.path('/dashboard');
      }

      $scope.openModal = function openModal() {
        $scope.registerModal = $uibModal.open({
          templateUrl: 'views/registerModal.html',
          scope: $scope
        });
      };

      $scope.closeModal = function closeModal() {
        $scope.registerModal.close()
      };

      $scope.login = function login(user) {
        UserService.login(user.email, user.password)
          .then(function success(data) {
            console.log('login successful');
            $rootScope.currentUser = angular.copy(data.data);
            $location.path('/dashboard');
          }, function error() {
            console.log('login failed');
          });
      };

      $scope.register = function register(newUser) {
        if(newUser.password !== newUser.confirm) {
          console.log('passwords do not match');
        } else {
          UserService.createUser(newUser.email, newUser.password, newUser.thermostat_id)
            .then(function success() {
              $scope.closeModal();
              $location.path('/dashboard');
            }, function error() {
              console.log('user with email exists');
            });
        }
      };

    }
  ]);

controllers
  .controller('DashboardController', ['$scope', '$rootScope', '$location', '$interval', 'config', 'UserService', 'ControlService',
    function($scope, $rootScope, $location, $interval, config, UserService, ControlService) {
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
        max: config.MAX_TEMPERATURE,
        readOnly: true,
        dynamicOptions: true
      };
      $scope.trKnobOptions = {
        scale: {
          enabled: true,
          type: 'dots',
          color: 'rgba(255,0,0,.2)',
          width: 2,
          quantity: config.MAX_TEMPERATURE,
          spaceWidth: 10
        },
        unit: 'C',
        barWidth: 40,
        trackWidth: 25,
        trackColor: 'rgba(0,0,0,.1)',
        prevBarColor: 'rgba(0,0,0,.2)',
        max: config.MAX_TEMPERATURE,
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

      ControlService.connect($rootScope.currentUser.thermostat_id)
        .then(ControlService.thermostatOnline)
        .then(function success(isOnline) {
          $scope.thermostatOnline = isOnline;
          ControlService.requestTemperatures();
        });

      $scope.logout = function logout() {
        try {
          ControlService.disconnect();
        } finally {
          UserService.logout();
          $location.path('/login');
        }
      };
    }
  ]);
