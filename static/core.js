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

galton.filter('onlyIncluded', function() {
    return function(tasks) {
        var onlyIncluded = [];

        for (var i in tasks) {
            var task = tasks[i];

            if (task.include) {
                onlyIncluded.push(task);
            }
        }

        return onlyIncluded;
    };
});

galton.controller('mainController',
    function ($scope, $http, $location) {
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

        $scope.createProject = function() {
            //console.log('create project: ' + $scope.formData);
            $http.post('/api/project/create', $scope.formData)
                .success(function(id) {
                    console.log('create success ' + id);

                    if (id > 0) {
                        $location.path("/edit/" + id);
                    }
                });
        };

        $scope.copyProject = function (projectId) {

            $http.get('/api/project/copy/' + projectId)
                .success(function (id) {

                    if (id > 0) {
                        $location.path("/edit/" + id);
                    }
                })
                .error(function (data) {
                    console.log('Error: ' + data);
                });
        };
    });

galton.controller('reportController',
    function ($scope, $http, $routeParams, $location) {

        var title;
        var units;
        
        $scope.getProject = function() {
            $http.get('/api/project/' + $routeParams.projectId)
                .success(function(data) {
                    if (data.length == 1) {
                        $scope.project = data[0];

                        // convert ints to booleans for angular
                        $scope.project.publish = !!$scope.project.publish;

                        // chart config
                        title = $scope.project.description;
                        units = $scope.project.units;

                        $scope.status = "";
                    }
                })
                .error(function(data) {
                    console.log('Error: ' + data);
                });
        };

        $scope.getTasks = function() {
            $http.get('/api/tasks/' + $routeParams.projectId)
                .success(function(data) {
                    $scope.tasks = data;

                    // convert ints to booleans for angular
                    for (var i in $scope.tasks) {
                        var task = $scope.tasks[i];
                        task.include = !!task.include;
                        console.log(task);
                    };

                    //console.log('tasks...');
                    //console.log(data);

                    $scope.newtask = { description: 'new task', count: 1, estimate: 1, risk: 'medium', include: false };
                })
                .error(function(data) {
                    console.log('Error: ' + data);
                });
        };

        $scope.runSimulation = function() {
            $http.get('/api/results/' + $routeParams.projectId)
                .success(function(data) {
                    $scope.results = data;

                    console.log('results...');
                    console.log(data);

                    if (data.schedule) {
                        drawSchedule(title, data.schedule);
                    } else {
                        drawChart(title, units, data.cumprob);
                    }
                })
                .error(function(data) {
                    console.log('Error: ' + data);
                });
        };

        $scope.resetProject = function() {
            $scope.getProject();
            $scope.getTasks();
            $scope.runSimulation();
        };

        // Run project, tasks and run the simulation on entry
        $scope.resetProject();

        $scope.projectChanged = function() {
            $scope.status = "changes pending";
        };

        $scope.saveProject = function () {

            $scope.status = "saving project...";
            
            var saveTasks = [];

            for (var i in $scope.tasks) {
                var task = $scope.tasks[i];

                if (!task.remove) {
                    saveTasks.push(task);
                }
            }
            
            if ($scope.newtask.include) {
                saveTasks.push($scope.newtask);
            }
            
            $http.post('/api/project/save', { project: $scope.project, tasks: saveTasks })
                .success(function (data) {
                    $scope.resetProject();
                })
                .error(function (data) {
                    console.log('Error: ' + data);
                    $scope.status = 'Error: ' + data;
                });
        };

        $scope.copyProject = function () {

            var projectId = $scope.project.id;

            $http.get('/api/project/copy/' + projectId)
                .success(function (id) {

                    if (id > 0) {
                        $location.path("/edit/" + id);
                    }
                })
                .error(function (data) {
                    console.log('Error: ' + data);
                });

        };

        $scope.deleteProject = function () {

            var projectId = $scope.project.id;
            var description = $scope.project.description;

            if (!confirm('Delete project "' + description + '" irreversibly?')) {
                return;
            }

            $http.get('/api/project/delete/' + projectId)
                .success(function (id) {

                    if (id == projectId) {
                        $location.path("/");
                    }
                })
                .error(function (data) {
                    console.log('Error: ' + data);
                });

        };

        $scope.runProject = function () {

            $http.post('/api/simulate/project', { project: $scope.project, tasks: $scope.tasks })
                .success(function (data) {
                    $scope.results = data;

                    console.log('results...');
                    console.log(data);

                    if (data.schedule) {
                        drawSchedule(title, data.schedule);
                    } else {
                        drawChart(title, units, data.cumprob);
                    }
                })
                .error(function (data) {
                    console.log('Error: ' + data);
                    $scope.status = 'Error: ' + data;
                });
        };

        $scope.runTask = function(task) {
            console.log('runTask ' + task);

            $http.post('/api/simulate/task', { project: $scope.project, tasks: [task] })
                .success(function (data) {
                    $scope.results = data;

                    console.log('results...');
                    console.log(data);

                    var chartTitle = 'task: ' + task.description;

                    if (data.schedule) {
                        drawSchedule(chartTitle, data.schedule);
                    } else {
                        drawChart(chartTitle, units, data.cumprob);
                    }
                })
                .error(function (data) {
                    console.log('Error: ' + data);
                    $scope.status = 'Error: ' + data;
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