'use strict';

var controllers = angular.module('titaniumControllers', [
  'ui.bootstrap',
  'ui.knob'
]);

controllers
  .controller('MainController', ['$scope', '$location', 'ControlService', 'UserService',
    function($scope, $location, ControlService, UserService) {
      $scope.options = {};
      $scope.options.showNav = false;

      $scope.isActive = function isActive(view) {
        return view === $location.path();
      };

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

controllers
  .controller('LoginController', ['$scope', '$rootScope', '$location', '$uibModal', 'localStorageService', 'UserService',
    function($scope, $rootScope, $location, $uibModal, localStorageService, UserService) {
      // check if already logged in
      if($rootScope.currentUser) {
        $location.path('/dashboard');
      }

      $scope.options.showNav = false;
      $scope.forms = {};
      $scope.registerFormError = null;
      $scope.loginFormError = null;

      $scope.openModal = function openModal(modal) {
        if(modal == 'register') {
          $scope.registerModal = $uibModal.open({
            templateUrl: 'views/registerModal.html',
            scope: $scope
          });
        } else if(modal == 'reset') {
          $scope.resetPasswordModal = $uibModal.open({
            templateUrl: 'views/resetPasswordModal.html',
            scope: $scope
          });
        }
      };

      $scope.closeModal = function closeModal(modal) {
        if(modal == 'register') {
          $scope.registerFormError = null;
          $scope.registerModal.close();
        } else if(modal == 'reset') {
          $scope.resetPasswordModal.close();
        }
      };

      $scope.login = function login(user) {
        if(!user || !user.email || !user.password || $scope.forms.login.$invalid) {
          $scope.loginFormError = 'Invalid email and/or password';
          return;
        }
        UserService.login(user.email, user.password)
          .then(function success() {
            console.log('login successful');

            $location.path('/dashboard');
          }, function error(data) {
            $scope.forms.login.$setValidity(false);
            $scope.loginFormError = data.data.message;
          });
      };

      $scope.register = function register(newUser) {
        UserService.createUser(newUser.email, newUser.password, newUser.thermostat_id)
          .then(function success() {
            $scope.closeModal('register');
            $location.path('/dashboard');
          }, function error(data) {
            $scope.forms.register.$setUntouched();
            $scope.registerFormError = data.data.message;
          });
      };

    }
  ]);

controllers
  .controller('DashboardController', ['$scope', '$rootScope', '$location', '$interval', '$timeout', '$uibModal', 'localStorageService', 'config', 'UserService', 'ControlService',
    function($scope, $rootScope, $location, $interval, $timeout, $uibModal, localStorageService, config, UserService, ControlService) {
      var temperaturePoll = $interval(function() {
        if($scope.thermostatOnline) {
          ControlService.requestTemperatures();
        }
      }, 30000); // 30s;
      var onlinePoll = $interval(function() {
        ControlService.thermostatOnline()
          .then(function success(isOnline) {
            $scope.thermostatOnline = isOnline;
          });
      }, 60000); // 1min
      var updateRangeTimeout = null;
      var updateRangeDelay = 5000; // 5s

      $scope.options.showNav = true;
      $scope.forms = {};
      $scope.thermostatOnline = false;
      $scope.temperatures = ControlService.temperatures;
      $scope.status = ControlService.status;
      $scope.settings = ControlService.settings;
      // TODO: disable knobs when offline, make readonly
      $scope.ctKnobOptions = {
        size: 200,
        unit: '',
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
        unit: '',
        barWidth: 40,
        trackWidth: 25,
        trackColor: 'rgba(0,0,0,.1)',
        prevBarColor: 'rgba(0,0,0,.2)',
        max: config.MAX_TEMPERATURE,
        displayPrevious: true,
        dynamicOptions: true
      };

      $scope.resetUpdateTimeout = function resetUpdateTimeout() {
        $timeout.cancel(updateRangeTimeout);
        updateRangeTimeout = $timeout(function() {
          if($scope.thermostatOnline) {
            ControlService.updateTemperatureRange($scope.temperatures['temperature_low'], $scope.temperatures['temperature_high']);
          }
        }, updateRangeDelay);
      };

      $scope.$on('$destroy', function() {
        $interval.cancel(temperaturePoll);
        $interval.cancel(onlinePoll);
        $timeout.cancel(updateRangeTimeout);
      });

      $scope.$watch('temperatures.temperature_low', function(value) {
        if(value > $scope.temperatures['temperature_high']) {
          $scope.temperatures['temperature_low'] = $scope.temperatures['temperature_high'];
        }
        $scope.resetUpdateTimeout();
      });

      $scope.$watch('temperatures.temperature_high', function(value) {
        if(value < $scope.temperatures['temperature_low']) {
          $scope.temperatures['temperature_high'] = $scope.temperatures['temperature_low'];
        }
        $scope.resetUpdateTimeout();
      });

      $scope.openModal = function openModal(setting) {
        if(!$scope.thermostatOnline) {
          return;
        }
        $scope.modalSetting = setting;
        $scope.settingModal = $uibModal.open({
          templateUrl: 'views/settingModal.html',
          scope: $scope,
          size: 'sm'
        });
      };

      $scope.closeModal = function closeModal() {
        $scope.modalSetting = {};
        $scope.settingModal.close();
      };

      $scope.setMode = function setMode(mode) {
        ControlService.updateMode(mode);
        $scope.status.mode = mode;
      };

      $scope.updateSetting = function updateSetting(setting) {
        if(!setting || !setting.name || !setting) {
          return;
        }
        // TODO: confirm success
        ControlService.updateSetting(setting.name, setting.value);
        $scope.settings[setting.name] = setting.value;
        $scope.closeModal();
      };

      $scope.isEmpty = function isEmpty(obj) {
        return obj === {};
      };

      // dashboard initialization
      ControlService.connect($rootScope.currentUser.thermostat_id)
        .then(ControlService.thermostatOnline)
        .then(function success(isOnline) {
          $scope.thermostatOnline = isOnline;
          if($scope.thermostatOnline) {
            ControlService.requestTemperatures(true);
            ControlService.requestMode();
            ControlService.requestSettings();

            // HACK to display results quickly
            $timeout(function() {
              $scope.$digest();
            }, 2000);
          }
        });
    }
  ]);

controllers
  .controller('ProfileController', ['$scope',
    function($scope) {
      $scope.options.showNav = true;
    }
  ]);

controllers
  .controller('HelpController', ['$scope',
    function($scope) {
      $scope.options.showNav = true;
    }
  ]);
