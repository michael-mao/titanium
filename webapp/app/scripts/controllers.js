'use strict';

var controllers = angular.module('titaniumControllers', [
  'ui.bootstrap'
]);

controllers
  .controller('LoginController', ['$scope', '$rootScope', '$location', 'LoginService',
    function($scope, $rootScope, $location, LoginService) {
      // check if already logged in
      if($rootScope.currentUser) {
        $location.path('/dashboard');
      }

      $scope.submit = function submit(user) {
        LoginService.authenticate(user.email, user.password)
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
  .controller('DashboardController', ['$scope', '$location',
    function($scope, $location) {

      $scope.logout = function logout() {
        $location.path('/login');
      };
    }
  ]);
