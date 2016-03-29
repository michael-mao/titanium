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
        if($rootScope.thermostatOnline) {
          ControlService.requestTemperatures();
        }
      }, 30000); // 30s;
      var onlinePoll = $interval(function() {
        ControlService.thermostatOnline()
          .then(function success(isOnline) {
            $rootScope.thermostatOnline = isOnline;
          });
      }, 60000); // 1min
      var updateRangeTimeout = null;
      var updateRangeDelay = 5000; // 5s
      var changeableSettings = {
        'City': true
      };

      $scope.options.showNav = true;
      $scope.forms = {};
      $scope.temperatures = ControlService.temperatures;
      $scope.status = ControlService.status;
      $scope.settings = ControlService.settings;
      // TODO: disable knobs when offline, make readonly
      $scope.ctKnobOptions = {
        size: 200,
        unit: '',
        barWidth: 40,
        trackWidth: 40,
        trackColor: 'rgba(0,0,0,.1)',
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
        trackColor: 'rgba(255,0,0,.1)',
        prevBarColor: 'rgba(0,0,0,.2)',
        max: config.MAX_TEMPERATURE,
        displayPrevious: true,
        dynamicOptions: true
      };

      $scope.resetUpdateTimeout = function resetUpdateTimeout() {
        $timeout.cancel(updateRangeTimeout);
        updateRangeTimeout = $timeout(function() {
          if($rootScope.thermostatOnline) {
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
        if(!$rootScope.thermostatOnline || !changeableSettings[setting.name]) {
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
          $rootScope.thermostatOnline = isOnline;
          if($rootScope.thermostatOnline) {
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
  .controller('AnalyticsController', ['$scope', '$timeout', 'ControlService',
    function($scope, $timeout, ControlService) {
      $scope.options.showNav = true;

      var margin = { top: 50, right: 0, bottom: 100, left: 30 },
          width = 960 - margin.left - margin.right,
          height = 430 - margin.top - margin.bottom,
          gridSize = Math.floor(width / 24),
          colors = ["#4575b4","#74add1","#abd9e9","#e0f3f8","#fee090","#fdae61","#f46d43","#d73027"],
          days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
          times = [
            "1am", "2am", "3am", "4am", "5am", "6am", "7am", "8am", "9am", "10am", "11am", "12am",
            "1pm", "2pm", "3pm", "4pm", "5pm", "6pm", "7pm", "8pm", "9pm", "10pm", "11pm", "12pm"
          ];

      var svg = d3.select("#history_chart").append("svg")
          .attr("width", width + margin.left + margin.right)
          .attr("height", height + margin.top + margin.bottom)
          .append("g")
          .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

      var dayLabels = svg.selectAll(".dayLabel")
          .data(days)
          .enter().append("text")
            .text(function (d) { return d; })
            .attr("x", 0)
            .attr("y", function (d, i) { return i * gridSize; })
            .style("text-anchor", "end")
            .attr("transform", "translate(-6," + gridSize / 1.5 + ")")
            .attr("class", function (d, i) { return ((i >= 0 && i <= 4) ? "dayLabel mono axis axis-workweek" : "dayLabel mono axis"); });

      var timeLabels = svg.selectAll(".timeLabel")
          .data(times)
          .enter().append("text")
            .text(function(d) { return d; })
            .attr("x", function(d, i) { return i * gridSize; })
            .attr("y", 0)
            .style("text-anchor", "middle")
            .attr("transform", "translate(" + gridSize / 2 + ", -6)")
            .attr("class", function(d, i) { return ((i >= 7 && i <= 16) ? "timeLabel mono axis axis-worktime" : "timeLabel mono axis"); });

      function drawHistory(data) {
          var colorScale = d3.scale.ordinal()
            .domain(['c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8'])
            .range(colors);

          var cards = svg.selectAll(".hour")
            .data(data, function (d) {
              return d.day + ':' + d.hour;
            });

          var tooltip = d3.select("body").append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);

          cards.append("title");

          cards.enter().append("rect")
            .attr("x", function (d) {
              return (d.hour - 1) * gridSize;
            })
            .attr("y", function (d) {
              return (d.day - 1) * gridSize;
            })
            .attr("rx", 4)
            .attr("ry", 4)
            .attr("class", "hour bordered")
            .attr("width", gridSize)
            .attr("height", gridSize)
            .style("fill", colors[0])
            // TODO: improve tooltip
            .on("mouseover", function(d) {
              tooltip.transition()
                .duration(200)
                .style("opacity", .9);
              tooltip.html('Temp: ' + d.value)
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 28) + "px");
              })
            .on("mouseout", function(d) {
              tooltip.transition()
                .duration(500)
                .style("opacity", 0);
            });

          cards.transition().duration(1000)
            .style("fill", function (d) {
              return colorScale(d.color);
            });

          cards.select("title").text(function (d) {
            return d.value;
          });

          cards.exit().remove();
      }

      // TOTAL HACK
      ControlService.requestHistory();
      $timeout(function() {
        angular.forEach(ControlService.history, function(d) {
          var t = parseInt(d.value);
          if(t < 17) {
            d.color = 'c1'
          } else if(t == 17) {
            d.color = 'c2'
          } else if(t == 18) {
            d.color = 'c3'
          } else if(t == 19) {
            d.color = 'c4'
          } else if(t == 20) {
            d.color = 'c5'
          } else if(t == 21) {
            d.color = 'c6'
          } else if(t == 22) {
            d.color = 'c7'
          } else if(t > 23) {
            d.color = 'c8'
          }
        });
        drawHistory(ControlService.history);
      }, 3000);
    }
  ]);

controllers
  .controller('HelpController', ['$scope',
    function($scope) {
      $scope.options.showNav = true;
    }
  ]);
