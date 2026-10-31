
class API_API
{
    constructor()
    {
        this.backendConnection = null;
        this.#connectBackend()
    }

    async createWebsocket(wsPath)
    {
        if (!await this.verifyAuthenticated())
            return false
        var authData = this.#getToken()
        if (!authData)
            return false;
        var socket = null
        var protocol = window.location.protocol == "https:" ? 'wss': 'ws'
        try {
            socket = new WebSocket(protocol + '://' + window.location.host + wsPath,["pong", "Bearer____" + authData.access])
        } catch (error) {
            console.error(error)
            return false
        }
        return socket
    }

    async #connectBackend()
    {
        this.backendConnection = await this.createWebsocket('/ws/user/')
    }

    #saveToken(token)
    {
        localStorage.setItem("JWTAuth", JSON.stringify(token));
    }

    #getToken()
    {
        var token = localStorage.getItem('JWTAuth');
        if (!token)
            return null
        return JSON.parse(token)
    }

    async #refreshToken(authData)
    {
        var data = await this.post('/api/auth/token/refresh/', { refresh: authData.refresh }, { noauth: true });

        if (!data.success)
        {
            ft_log("Error refreshing token: " + JSON.stringify(data))
            localStorage.removeItem("JWTAuth");
            return false;
        }
        this.#saveToken(data.data);
        ft_log("Token refreshed")
        return data.data
    }

    async #addAuthorization(header)
    {
        if (!await this.verifyAuthenticated())
            return
        var authData = this.#getToken()
        if (!authData)
            return;
        header["Authorization"] = "Bearer " + authData.access;
    }

    async get(url, options = { type:"json", noauth: false } )
    {
        return await this.request("GET", url, null, { noauth: options.noauth, type: options.type ? options.type : "json" })
    }
    
    async post(url, data, options = { noauth: false , type:"json"})
    {
        return await this.request("POST", url, data, { noauth: options.noauth, type: options.type ? options.type : "json" })
    }

    async request(method = "GET", url, data = null, options = { noauth: false, type:"json"  })
    {
        var header = {}

        if (method != "GET")
            header["Content-Type"] = "application/json"

        if (!options.noauth)
            await this.#addAuthorization(header)
        try {
            var res = await fetch(url,{
                method: method,
                headers: header,
                body: data ? JSON.stringify(data): null,
                credentials: "same-origin"
            }).then((response) => {
                if (response.status >= 400 && response.status < 600) {
                    if (response.status == 401)
                       localStorage.removeItem("JWTAuth");
                    throw new Error("Bad response from server");
                }
                return response;
            }).then((returnedResponse) => {
                return returnedResponse
            }).catch((error) => {
                throw error;
            });
        } catch (error) {
            return { success: false, error: error };
        }
        return await res[options.type]()
    }

    async upload(url, data)
    {
        var header = {}

        header["Content-Disposition"] = "attachment; filename=" + data.name
        await this.#addAuthorization(header)
        try {
            var res = await fetch(url,{
                method: "PUT",
                headers: header,
                body: data,
            }).then((response) => {
                if (response.status >= 400 && response.status < 600) {
                    if (response.status == 401)
                       localStorage.removeItem("JWTAuth");
                    throw new Error("Bad response from server");
                }
                return response;
            }).then((returnedResponse) => {
                return returnedResponse
            }).catch((error) => {
                throw error;
            });
        } catch (error) {
            return { success: false, error: error };
        }
        return await res["json"]()
    }

    async login(username, password, twoFaCode = null)
    {
        var data = await this.post('/api/auth/token/', { username: username, password: password, code: twoFaCode }, { noauth: true });

        if (!data.success)
        {
            ft_log("Error loging in: " + data.error)
            if (!data.error)
            {
                return { success: false, error: "Error sending request!"};
            }
            return data;
        }
        this.#saveToken(data.data)
        if (!this.backendConnection)
            this.#connectBackend()
        window.document.dispatchEvent(new Event("DOMContentLoaded", {
            bubbles: true,
            cancelable: true
        }));
        return { success: true };
    }

    async logout()
    {
        var authData = this.#getToken();
        if (authData == null)
            return;

        var data = await this.post('/api/auth/logout/', { refresh: authData.refresh }, { noauth: false });

        localStorage.removeItem("JWTAuth");
        if (window.gameClient)
            gameClient.disconnect()
        if (this.backendConnection)
        {
            this.backendConnection.close()
            this.backendConnection = null;
        }
        window.document.dispatchEvent(new Event("DOMContentLoaded", {
            bubbles: true,
            cancelable: true
        }));
        return data.success;
    }

    async verifyAuthenticated()
    {
        var authData = this.#getToken();
        if (authData == null)
            return false;
        var timeLeft = authData.expiry - Math.floor(Date.now() / 1000)
        if (timeLeft < 2)
            authData = await this.#refreshToken(authData)
        return !!authData
    }

    async oauthLogin()
    {
        var url = await this.post("/api/auth/oauth",null, { type:"json", noauth: true});
        if (url.success != false)
            window.location = url.data;
        else
            ft_log(url.error);
    }
};

let api =  new API_API()

export {
    api
}