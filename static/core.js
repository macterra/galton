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

        // route for the project report
        .when('/report/:projectId', {
            templateUrl: '/static/report.html',
            controller: 'reportController'
        })

        // route for the project editor
        .when('/edit/:projectId', {
            templateUrl: '/static/editor.html',
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

        var title;
        var units;

        $http.get('/api/project/' + $routeParams.projectId)
            .success(function (data) {
                if (data.length == 1) {
                    $scope.project = data[0];

                    console.log('project...');
                    console.log(data[0]);

                    // chart config
                    title = $scope.project.description;
                    units = $scope.project.units;
                }
            })
            .error(function (data) {
                console.log('Error: ' + data);
            });

        $http.get('/api/tasks/' + $routeParams.projectId)
            .success(function (data) {
                $scope.tasks = data;

                //console.log('tasks...');
                //console.log(data);
            })
            .error(function (data) {
                console.log('Error: ' + data);
            });

        $http.get('/api/results/' + $routeParams.projectId)
            .success(function (data) {
                $scope.results = data;

                //console.log('results...');
                //console.log(data);

                drawChart(title, units, data.cumprob);
            })
            .error(function (data) {
                console.log('Error: ' + data);
            });

        $scope.saveProject = function () {
            console.log($scope.project);

            $http.post('/api/project/save', $scope.project)
                .success(function (data) {
                    if (data.length == 1) {
                        $scope.project = data[0];
                        
                        // chart config
                        title = $scope.project.description;
                        units = $scope.project.units;
                    }
                });
        };
    });


function drawChart(title, units, myData) {
    var myChart = new JSChart('graph', 'line');

    myChart.setSize(800, 600);
    myChart.setDataArray(myData);
    myChart.setLineSpeed(100);
    myChart.setLineColor('#8D9386');
    myChart.setLineWidth(4);
    myChart.setTitleColor('#7D7D7D');
    myChart.setAxisColor('#9F0505');
    myChart.setGridColor('#a4a4a4');
    myChart.setAxisValuesColor('#333639');
    myChart.setAxisNameColor('#333639');
    myChart.setTextPaddingLeft(0);
    myChart.setAxisNameX(sprintf("Effort (%s)", units));
    myChart.setAxisNameY("Confidence");
    myChart.setTitle(title);
    myChart.draw();
};

function drawSchedule(title, myData) {
    var myChart = new JSChart('graph', 'line');

    myChart.setSize(800, 600);
    myChart.setDataArray(myData);
    myChart.setLineSpeed(100);
    myChart.setLineColor('#8D9386');
    myChart.setLineWidth(4);
    myChart.setTitleColor('#7D7D7D');
    myChart.setAxisColor('#9F0505');
    myChart.setGridColor('#a4a4a4');
    myChart.setAxisValuesColor('#333639');
    myChart.setAxisNameColor('#333639');
    myChart.setTextPaddingLeft(0);
    myChart.setAxisPaddingBottom(80);
    myChart.setAxisNameX('Date');
    myChart.setAxisValuesAngle(45);
    myChart.setAxisNameY("Confidence");
    //myChart.setAxisValuesNumberX(10);
    //myChart.setShowXValues(false);
    myChart.setAxisValuesNumberY(11);
    myChart.setTitle(title);
    myChart.draw();
};