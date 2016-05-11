
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
            $("#edit_root").css("display", "block");
            $("#edit_data").html(json["page"]);
            console.log(json.page);
            $("#edited_voivodeship_name").html("Edytuje " + json["edit_data"]);
            $("#close_button").on("click", function (event) {
                $("#edit_root").css("display", "none");
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