
class ProfileSettings
{
    constructor()
    {

    }

    async setPlayerName()
    {
        var obj = document.getElementById("floatingInputPlayerName")
        var feedback = document.getElementById("invalidPlayerNameFeedback")

        obj.classList.remove("is-invalid")
        obj.classList.remove("is-valid")
        obj.parentNode.classList.remove("is-invalid")
        obj.parentNode.classList.remove("is-valid")
        var data = await api.request("PATCH","api/user/", {playerName: obj.value})

        if (!data.success)
        {
            var error = data.error ? data.error : "Error setting Player Name!"
            obj.classList.add("is-invalid")
            obj.parentNode.classList.add("is-invalid")
            feedback.innerText = error
            return;
        }
        obj.classList.add("is-valid")
        obj.parentNode.classList.add("is-valid")
        setTimeout(()=>{
            obj.classList.remove("is-valid")
            obj.parentNode.classList.remove("is-valid")
        }, 1000)
    }

    async setPlayerAvatar()
    {
        var obj = document.getElementById("avatarImgUpload")
        var file = obj.files[0]

        var data = { success: true};
        if (obj.files.length == 0)
            data = { success: false, error: "Select a file!"};
        obj.classList.remove("is-invalid")
        obj.classList.remove("is-valid")
        if (data.success)
            data = await api.upload("api/user/avatar/", file)
        if (!data.success)
        {
            obj.classList.add("is-invalid")
            document.getElementById("invalidFileFeedback").innerText = data.error ? data.error : "Error uploading file!"
            return;
        }
        obj.classList.add("is-valid")
        setTimeout(()=>{viewManager.queueView('settings', null, false)}, 500)
    }

    async resetPassword()
    {
        var passObj = document.getElementById("floatingInputPassword")
        var verifyObj = document.getElementById("floatingInputPasswordRepeat")
        var feedback = document.getElementById("resetPasswordFeedback")

        var data = { success: true};
        if (passObj.value != verifyObj.value)
            data = { success: false, error: "Passwords not match!"};

        feedback.innerText = ""
        feedback.classList.remove("valid-feedback", "invalid-feedback")
        verifyObj.parentNode.classList.remove("is-invalid", "is-valid")
        verifyObj.classList.remove("is-invalid", "is-valid")
        passObj.classList.remove("is-invalid", "is-valid")
        if (data.success)
            data = await api.post("api/user/password", { password: passObj.value })
        ft_log(data)
        if (!data.success)
        {
            verifyObj.classList.add("is-invalid")
            passObj.classList.add("is-invalid")
            verifyObj.parentNode.classList.add("is-invalid")
            feedback.classList.add("invalid-feedback")
            feedback.innerText = data.error ? data.error : "Error resetting password!"
            return;
        }
        feedback.classList.add("valid-feedback")
        feedback.innerText = "Password reset!"
        verifyObj.parentNode.classList.add("is-valid")
    }

    async toggle2FA(status)
    {
        if (status)
        {
            var data = await api.request("DELETE", "api/auth/2FA/", {});
            if (data.success)
                viewManager.queueView("settings", null, false);
            return;
        }
        viewManager.queueView("setup-2FA")
    }

    async start2faSetup()
    {
        var data = await api.get("api/auth/2FA/")
        
        if (!data.success)
            return;
        ft_log(data)

        var obj = document.getElementById("2fa-qr")
        var qrcode = new QRCode(obj);
        qrcode.makeCode(data.data);
    }

    async verify2FA()
    {
        var obj = document.getElementById("floating2FA")
        var feedback = document.getElementById("2fa-setup-feedback")

        var data = { success: true};
        if (obj.value.length < 4)
            data = { success: false, error: "Please enter a correct code!"};
        feedback.innerHTML = ""
        feedback.classList.remove("valid-feedback","invalid-feedback")
        obj.classList.remove("is-invalid", "is-valid")
        obj.parentElement.classList.remove("is-invalid", "is-valid")
        if (data.success)
            data = await api.post("api/auth/2FA/", { code: obj.value })
        if (!data.success)
        {
            obj.classList.add("is-invalid")
            obj.parentElement.classList.add("is-invalid")
            feedback.classList.add("invalid-feedback")
            feedback.innerText = data.error ? data.error : "Error uploading file!"
            return;
        }
        obj.classList.add("is-valid")
        obj.parentElement.classList.add("is-valid")
        setTimeout(()=>{
            history.back()
            viewManager.queueView("settings")
        }, 1000)
    }
};


window.profileSettings = new ProfileSettings()