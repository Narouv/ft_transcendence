
class UserHandler
{
    constructor()
    {

    }

    async makeLogin()
    {
        var username = document.getElementById("floatingInputUsername")
        var password = document.getElementById("floatingInputPassword")
        var twoFA = document.getElementById("floating2FA")
        var feedback = document.getElementById("login-user-feedback")

        feedback.innerHTML = ""
        twoFA.parentElement.classList.remove("is-valid")
        twoFA.parentElement.classList.remove("is-invalid")
        username.classList.remove("is-invalid")
        password.classList.remove("is-invalid")
        feedback.classList.remove("valid-feedback")
        feedback.classList.remove("invalid-feedback")
        var data = await api.login(username.value, password.value, twoFA.value)
        if (!data.success)
        {
            twoFA.parentElement.classList.add("is-invalid")
            feedback.classList.add("invalid-feedback")
            if (data.error)
                feedback.innerHTML = data.error
            else
                feedback.innerHTML = "Error logging in"
        }
    }

    async makeRegister(form)
    {
        var username = document.getElementById("floatingInputUsername");
        var email = document.getElementById("floatingInputEmail");
        var password = document.getElementById("floatingInputPassword");
        var passwordCheck = document.getElementById("floatingInputPasswordRepeat");
        var feedback = document.getElementById("register-user-feedback");

        feedback.innerHTML = "";
        passwordCheck.parentElement.classList.remove("is-valid");
        passwordCheck.parentElement.classList.remove("is-invalid");
        username.classList.remove("is-invalid");
        password.classList.remove("is-invalid");
        feedback.classList.remove("valid-feedback");
        feedback.classList.remove("invalid-feedback");
        var result = null;
        if (password.value != passwordCheck.value)
            result = {success: false, error: "Passwords dont match"};
        if (!result)
            result = await api.post("/api/user/",{ username: username.value, email: email.value, password: password.value });
        if (!result.success)
        {
            passwordCheck.parentElement.classList.add("is-invalid");
            feedback.classList.add("invalid-feedback");
            if (result.error)
                feedback.innerHTML = result.error;
            else
                feedback.innerHTML = "Error registering";
        }
        else
        {
            passwordCheck.parentElement.classList.add("is-valid");
            feedback.classList.add("valid-feedback");
            feedback.innerHTML = "Registered successfully";
            viewManager.queueView("login", {}, true);
        }
    }

}

window.userHandler = new UserHandler()

