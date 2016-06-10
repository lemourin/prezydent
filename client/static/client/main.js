"use strict";

var app = angular.module('app', ['LocalStorageModule']);

app.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

function send_login(http, scope, localstorage) {
    var username = $("#username");
    var password = $("#password");
    var login_form = $("#login_form");
    $.ajax({
        url : "/login_form",
        type : "POST",
        data : {
            username : username.val(),
            password : password.val()
        },
        success : function(json) {
            if ("error" in json)
                login_form.html(json["error"]);
            else if ("ok" in json) {
                login_form.html(json["ok"]);
                scope.user_authenticated = true;
            }
            location.reload();
        }
    });
}

function send_logout(http, scope, localstorage) {
    var logut_form = $("#logout_form");
    $.ajax({
        url : "/logout_form",
        type : "POST",
        success : function(json) {
            scope.user_authenticated = false;
            location.reload();
        }
    });
}

app.controller('controller', function ($http, $scope, localStorageService) {
    $scope.create_edit_form = create_edit_form;
    $scope.send_login = function() { return send_login($http, $scope, localStorageService)};
    $scope.send_logout = function() { return send_logout($http, $scope, localStorageService)};
    function set_data(scope, http, json, localstorage) {
        narysuj(json["colors"]);
        scope.citizen_count = json["citizen_count"];
        scope.area = json["area"];
        scope.population_density = json["population_density"];
        scope.authorized_citizen_count = json["authorized_citizen_count"];
        scope.form_count = json["form_count"];
        scope.all_vote_count = json["all_vote_count"];
        scope.vote_count = json["vote_count"];

        scope.candidate1_percentages = json["candidate1_percentages"];
        scope.candidate1_colors = json["candidate1_colors"];
        scope.candidate2_percentages = json["candidate2_percentages"];
        scope.candidate2_colors = json["candidate2_colors"];

        scope.candidate1 = json["candidate1"];
        scope.candidate2 = json["candidate2"];

        scope.result_candidate1 = json["result_candidate1"];
        scope.result_candidate1_percentage = json["result_candidate1_percentage"];

        scope.result_candidate2 = json["result_candidate2"];
        scope.result_candidate2_percentage = json["result_candidate2_percentage"];

        scope.user_authenticated = json["user_authenticated"];
        scope.user_name = json["user_name"];

        function aggregate(json) {
            var candidate1 = 0, candidate2 = 0;
            json.forEach(function(city) {
                candidate1 += city["candidate1"];
                candidate2 += city["candidate2"];
            });
            var sum = candidate1 + candidate2;
            return {
                "vote_candidate1" : candidate1,
                "vote_candidate2" : candidate2,
                "vote_count" : sum,
                "vote_candidate1_percentage" : (100 * candidate1 / sum).toFixed(2),
                "vote_candidate2_percentage" : (100 * candidate2 / sum).toFixed(2)
            }
        }

        scope.results_by_voivodeship = {};
        json["voivodeships"].forEach(function(name) {
            scope.results_by_voivodeship[name] = localstorage.get('results_by_voivodeship_' + name);
            http.get("/city/list/voivodeship/" + name).then(function(response) {
                scope.results_by_voivodeship[name] = aggregate(response.data["data"]);
                localstorage.set('results_by_voivodeship_' + name, aggregate(response.data["data"]));
            });
        });
        scope.results_by_town_type = {};
        json["town_types"].forEach(function(name) {
            scope.results_by_town_type[name] = localstorage.get('results_by_town_type_' + name);
            http.get("/city/list/towntype/" + name).then(function(response) {
                scope.results_by_town_type[name] = aggregate(response.data["data"]);
                localstorage.set('results_by_town_type_' + name, aggregate(response.data["data"]));
            });
        });

        var population_splits = [
            500,
            1000,
            2000,
            3000,
            5000,
            10000,
            20000,
            50000,
            100000
        ];
        scope.results_by_population = {};
        scope.results_by_population["statki i zagranica"] = localstorage.get('statki_i_zagranica');
        http.get("/city/list/boats_and_abroad").then(function(response) {
            var json = response.data["data"];
            scope.results_by_population["statki i zagranica"] = aggregate(json);
            localstorage.set('statki_i_zagranica', aggregate(json));
        });

        function get_id(i, a, b) {
            var id = "";
            if (i != 0)
                id += "od " + a + (i != population_splits.length ? " " : "");
            if (i != population_splits.length)
                id += "do " + b;
            return id;
        }

        function create_func(i, a, b, localstorage) {
            return function(response) {
                var json = response.data["data"];

                var result = aggregate(json);
                if (result["vote_count"] != 0) {
                    scope.results_by_population[get_id(i, a, b)] = result;
                    localstorage.set('results_by_population_' + get_id(i, a, b), result);
                }
            }
        }
        for (var i = 0; i <= population_splits.length; i++) {
            var a = i == 0 ? 0 : population_splits[i - 1];
            var b = i == population_splits.length ? 1e9 : population_splits[i];

            var t = localstorage.get('results_by_population_' + get_id(i, a, b));
            if (t != null && t["vote_count"] != 0)
                scope.results_by_population[get_id(i, a, b)] = t;
            http.get("/city/list/population/" + a + "-" + b).then(create_func(i, a, b, localstorage));
        }
        localstorage.set("data", json);
    }

    if (localStorageService.get("data") != null)
        set_data($scope, $http, localStorageService.get("data"), localStorageService);
    $http.get("/summary").then(function(response) {
        var json = response.data;
        set_data($scope, $http, json, localStorageService);
    });
});

function create_edit_form(id) {
    $.ajax({
        url : "/edit_form",
        type : "POST",
        data : {
            filter: id
        },

        success : function(json) {
            var edit_root = $("#edit_root");
            edit_root.css("display", "block");
            edit_root.html(json["page"]);
            $("#close_button").on("click", function(event) {
                edit_root.css("display", "none");
            });
            $("[id^=result_modify_button_]").on("click", function(event) {
                var town_id = this.id.replace("result_modify_button_", "");
                var value = this.value;
                var c1 = $("#result_modify_town_candidate1_" + town_id);
                var c2 = $("#result_modify_town_candidate2_" + town_id);
                c1.attr("readonly", value != "modyfikuj");
                c2.attr("readonly", value != "modyfikuj");
                if (value == "modyfikuj") {
                    this.value = "zatwierdź";
                    c1.css("background-color", "red");
                    c2.css("background-color", "red");
                } else {
                    this.value = "modyfikuj";
                    c1.css("background-color", "white");
                    c2.css("background-color", "white");
                    this.style.display = "none";
                    $("#result_modify_confirm_" + town_id).css("display", "inline");
                    $.ajax({
                        url : "/edit_history",
                        type : "POST",
                        data : {
                            "town_id" : town_id
                        },
                        success : function(json) {
                            $("#result_modify_confirm_last_edit_author_" + town_id).html(json["last_edit_author"]);
                            $("#result_modify_confirm_last_edit_time_" + town_id).html(json["last_edit_time"]);
                        }
                    });
                }
            });
            $("[id^=result_modify_error_button_]").on("click", function(event) {
                var town_id = this.id.replace("result_modify_error_button_", "");
                var c1 = $("#result_modify_town_candidate1_" + town_id);
                var c2 = $("#result_modify_town_candidate2_" + town_id);
                $("#result_modify_error_" + town_id).css("display", "none");
                $("#result_modify_button_" + town_id).css("display", "inline");
                c1.prop("value", c1.attr("value"));
                c2.prop("value", c2.attr("value"));
            });
            $("[id^=result_modify_confirm_button_]").on("click", function(event) {
                var town_id = this.id.replace("result_modify_confirm_button_", "");
                var c1 = $("#result_modify_town_candidate1_" + town_id);
                var c2 = $("#result_modify_town_candidate2_" + town_id);
                
                $("#result_modify_confirm_" + town_id).css("display", "none");
                if (this.value == "Tak") {
                    $.ajax({
                        url : "/modify_entry",
                        type : "POST",
                        data : {
                            "town_id" : town_id,
                            "candidate1" : c1.prop("value"),
                            "candidate2" : c2.prop("value")
                        },
                        success : function(json) {
                            if ("error" in json) {
                                $("#result_modify_error_" + town_id).css("display", "inline");
                                $("#result_modify_error_description_" + town_id).html(json["error"]);
                            } else {
                                $("#result_modify_button_" + town_id).css("display", "inline");
                                c1.attr("value", c1.prop("value"));
                                c2.attr("value", c2.prop("value"));
                            }
                        }
                    });
                } else {
                    $("#result_modify_button_" + town_id).css("display", "inline");
                    c1.prop("value", c1.attr("value"));
                    c2.prop("value", c2.attr("value"));
                }
            });
        }
    });
}

function create_document(http, scope, localstorage) {
    $("#login_form").on('submit', function(event) {
        event.preventDefault();
        create_login_form(scope, localstorage);
    });
    $("#logout_form").on('submit', function(event) {
        event.preventDefault();
        create_logout_form(scope, localstorage);
    });
}
