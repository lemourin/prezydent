
function create_login_form() {
    var username = $("#username");
    var password = $("#password")
    var login_form = $("#login_form");
    $.ajax({
        url : "/login_form", // the endpoint
        type : "POST", // http method
        data : {
            username : username.val(),
            password : password.val()
        },

        success : function(json) {
            console.log(json);
            if ("error" in json)
                login_form.html(json["error"]);
            else if ("ok" in json) {
                login_form.html(json["ok"]);
            }
            //login_form.css("display", "none");
        },

        error : function(xhr, errmsg, err) {
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
            $("#close_button").on("click", function (event) {
                edit_root.css("display", "none");
            });
            $("[id^=result_modify_button_]").on("click", function (event) {
                var town_id = this.id.replace("result_modify_button_", "");
                var value = this.value;
                var c1 = $("#result_modify_town_candidate1_" + town_id);
                var c2 = $("#result_modify_town_candidate2_" + town_id);
                c1.attr("readonly", value != "modyfikuj");
                c2.attr("readonly", value != "modyfikuj");
                if (value == "modyfikuj") {
                    this.value = "zatwierdz";
                    c1.css("background-color", "red");
                    c2.css("background-color", "red");
                } else {
                    this.value = "modyfikuj";
                    c1.css("background-color", "white");
                    c2.css("background-color", "white");
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
    $("[id^=result_by_]").on("click", function (event) {
        event.preventDefault();
        create_edit_form(this.id);
    });
});