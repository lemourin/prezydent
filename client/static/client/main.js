"use strict";

var app = angular.module('app', ['LocalStorageModule']);

app.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

app.controller('controller', function ($http, $scope, localStorageService) {
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

        if (json["user_authenticated"])
            $(".login_form").load("logged_in.html", function() {
                $("#logged_user_data").html("Zalogowano jako " + json["user_name"]);
            });
        else
            $(".login_form").load("logged_out.html");
        scope.results_by_voivodeship = {};

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

        json["voivodeships"].forEach(function(name) {
            http.get("/city/list/voivodeship/" + name).then(function(response) {
                scope.results_by_voivodeship[name] = aggregate(response.data["data"]);
                create_document(scope, localstorage)
            });
        });
        scope.results_by_town_type = {};
        json["town_types"].forEach(function(name) {
            http.get("/city/list/towntype/" + name).then(function(response) {
                scope.results_by_town_type[name] = aggregate(response.data["data"]);
                create_document(scope, localstorage)
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
        http.get("/city/list/boats_and_abroad").then(function(response) {
            var json = response.data["data"];
            scope.results_by_population["statki i zagranica"] = aggregate(json);
        });

        function create_func(i, a, b) {
            return function(response) {
                var json = response.data["data"];
                var id = "";
                if (i != 0)
                    id += "od " + a + (i != population_splits.length ? " " : "");
                if (i != population_splits.length)
                    id += "do " + b;
                var result = aggregate(json);
                if (result["vote_count"] != 0)
                    scope.results_by_population[id] = result;
                create_document(scope, localstorage)
            }
        }
        for (var i = 0; i <= population_splits.length; i++) {
            var a = i == 0 ? 0 : population_splits[i - 1];
            var b = i == population_splits.length ? 1e9 : population_splits[i];

            http.get("/city/list/population/" + a + "-" + b).then(create_func(i, a, b));
        }
        localstorage.set("data", json);
    }

    if (localStorageService.get("data") != null) {
        set_data($scope, $http, localStorageService.get("data"), localStorageService);
    } else
        $http.get("/summary").then(function(response) {
            var json = response.data;
            set_data($scope, $http, json, localStorageService);
        });
});

function create_login_form(scope, localstorage) {
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
            else if ("ok" in json)
                login_form.html(json["ok"]);
            localstorage.clearAll();
            location.reload()
        }
    });
}

function create_logout_form(scope, localstorage) {
    var logut_form = $("#logout_form");
    $.ajax({
        url : "/logout_form",
        type : "POST",
        success : function(json) {
            localstorage.clearAll();
            location.reload()
        }
    });
}

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

function create_document(scope, localstorage) {
    $("#login_form").on('submit', function(event) {
        event.preventDefault();
        create_login_form(scope, localstorage);
    });
    $("#logout_form").on('submit', function(event) {
        event.preventDefault();
        create_logout_form(scope, localstorage);
    });
    $("[id^=result_by_]").on("click", function(event) {
        event.preventDefault();
        create_edit_form(this.id);
    });
}
