

class GameModeManager
{
    constructor()
    {
        this.modeInfo= {
            local: "2 Players - Local\nCreates a local game for 2 players, both play on 1 keyboard\nPlayer controls: Left - W/S Right - Arrow Up/Down",
            pvp: "2 Players - Remote\nEnters matchmaking for a remote pvp game.\nPlayer controls: Left - W/S Right - Arrow Up/Down",
            tournament: "3-12 Players - Remote\nEnters matchmaking for a remote tournament game.\nPlayer controls: Left - W/S Right - Arrow Up/Down",
        }

    }

    setInfo(mode)
    {
        var infoText = document.getElementById("game-mode-info-text")

        infoText.innerText = this.modeInfo[mode]
    }

    selectMode(mode)
    {
        if (mode == "local")
        {
            viewManager.queueView("local-game-select", null,false)
            return
        }
        //if (mode == "pvp")
        {
            viewManager.queueView("matchmaking-select", { type: mode }, false)
            return
        }
    }

    async runMatchMaking(matchType)
    {
        var data = await api.post(`/api/pong/matchmaking/register/`,{ "type": matchType });
        ft_log(data);
        return data.success
    }

    async getActiveLobby()
    {
        var data = await api.get(`/api/pong/matchmaking/register/`);
        //ft_log(data)
        return data.success
    }

    async startGame(type)
    {
        const alertPlaceholder = document.getElementById('matchmakingAlertPlaceholder')
        const appendAlert = (message, type) => {
        const wrapper = document.createElement('div')
            wrapper.innerHTML = [
                `<div class="alert alert-${type} alert-dismissible" role="alert">`,
                `   <div>${message}</div>`,
                '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
                '</div>'
            ].join('')

            alertPlaceholder.innerHTML = ""
            alertPlaceholder.append(wrapper)
        }
        if (!await this.runMatchMaking(type))
        {
            appendAlert("Matchmaking failed!", "danger")
            return
        }
        if (!await gameObject.initLobby())
        {
            appendAlert("Cant connect to lobby!", "danger")
            return
        }
        gameManager.loadActiveView()
    }
}

window.gameModeManager = new GameModeManager()
