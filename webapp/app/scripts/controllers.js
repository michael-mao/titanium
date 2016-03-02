'use strict';

var controllers = angular.module('titaniumControllers', [
  'ui.bootstrap'
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
      ControlService.connect();
      ControlService.thermostatOnline()
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
