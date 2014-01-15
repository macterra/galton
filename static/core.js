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
            templateUrl: 'report.html',
            controller: 'reportController'
        });
    });

galton.controller('mainController',
    function($scope, $http)
    {
        $scope.formData = {};

        // when landing on the page, get all todos and show them
        $http.get('/api/projects')
            .success(function (data)
            {
                $scope.projects = data;
                console.log(data);
            })
            .error(function (data)
            {
                console.log('Error: ' + data);
            });
    });



