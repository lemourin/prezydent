"use strict";

function create_login_form() {
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
            }
            location.reload()
        },

        error : function(xhr, errmsg, err) {
        }
    });
}

function create_logout_form() {
    var logut_form = $("#logout_form");
    $.ajax({
        url : "/logout_form",
        type : "POST",
        success : function(json) {
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
                $("#result_modify_error_" + town_id).css("display", "none");
                $("#result_modify_button_" + town_id).css("display", "inline");
            });
            $("[id^=result_modify_confirm_button_]").on("click", function(event) {
                var town_id = this.id.replace("result_modify_confirm_button_", "");
                var c1 = $("#result_modify_town_candidate1_" + town_id);
                var c2 = $("#result_modify_town_candidate2_" + town_id);

                function on_failed_modify() {
                    c1.prop("value", c1.attr("value"));
                    c2.prop("value", c2.attr("value"));
                }

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
                                on_failed_modify();
                            } else {
                                $("#result_modify_button_" + town_id).css("display", "inline");
                                c1.attr("value", c1.prop("value"));
                                c2.attr("value", c2.prop("value"));
                            }
                        }
                    });
                } else {
                    $("#result_modify_button_" + town_id).css("display", "inline");
                    on_failed_modify();
                }
            });
        },

        error : function(xhr, errmsg, err) {
        }
    });
}

$(document).ready(function() {
    $("#login_form").on('submit', function(event) {
        event.preventDefault();
        create_login_form();
    });
    $("#logout_form").on('submit', function(event) {
        event.preventDefault();
        create_logout_form();
    });
    $("[id^=result_by_]").on("click", function(event) {
        event.preventDefault();
        create_edit_form(this.id);
    });
});