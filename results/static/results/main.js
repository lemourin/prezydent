
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
});