// public/core.js
var galton = angular.module('galton', []);

// configure our routes
galton.config(function ($routeProvider)
    {
        $routeProvider

        // route for the projects page
        .when('/', {
            templateUrl: '/static/projects.html',
            controller: 'mainController'
        })

        // route for the projects page
        .when('/report/:projectId', {
            templateUrl: '/static/report.html',
            controller: 'reportController'
        });
    });

galton.controller('mainController',
    function ($scope, $http) {
        $scope.formData = {};

        // when landing on the page, get all todos and show them
        $http.get('/api/projects')
            .success(function (data) {
                $scope.projects = data;
                console.log(data);
            })
            .error(function (data) {
                console.log('Error: ' + data);
            });
    });

galton.controller('reportController',
    function ($scope, $http, $routeParams) {

        $http.get('/api/project/' + $routeParams.projectId)
            .success(function (data) {
                if (data.length == 1) {
                    $scope.project = data[0];
                    console.log(data[0]);
                }
            })
            .error(function (data) {
                console.log('Error: ' + data);
            });
    });



