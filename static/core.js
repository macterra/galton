// public/core.js
var scotchTodo = angular.module('scotchTodo', []);

function mainController($scope, $http) {
    $scope.formData = {};

    // when landing on the page, get all todos and show them
    $http.get('/api/todos')
		.success(function (data) {
		    $scope.todos = data;
		    console.log(data);
		})
		.error(function (data) {
		    console.log('Error: ' + data);
		});

    // when submitting the add form, send the text to the node API
    $scope.createTodo = function () {
        $http.post('/api/todos/', $scope.formData)
			.success(function (data) {
			    $scope.formData = {}; // clear the form so our user is ready to enter another
			    $scope.todos = data;
			    console.log(data);
			})
			.error(function (data) {
			    console.log('Error: ' + data);
			});
    };

    // update a todo done state
    $scope.updateTodo = function (id, done) {
        //console.log('client updateTodo ' + id + ' = ' + done);

        $http.post('/api/todos/' + id, { done: done })
			.success(function (data) {
			    $scope.todos = data;
			    console.log(data);
			})
			.error(function (data) {
			    console.log('Error: ' + data);
			});
    };

    // delete a todo after checking it
    $scope.deleteTodo = function (id) {
        $http.delete('/api/todos/' + id)
			.success(function (data) {
			    $scope.todos = data;
			    console.log(data);
			})
			.error(function (data) {
			    console.log('Error: ' + data);
			});
    };

    // remove completed todos
    $scope.removeCompleted = function () {
        $http.get('/api/todos/cleanup')
			.success(function (data) {
			    $scope.todos = data;
			    console.log(data);
			})
			.error(function (data) {
			    console.log('Error: ' + data);
			});
    };
}
