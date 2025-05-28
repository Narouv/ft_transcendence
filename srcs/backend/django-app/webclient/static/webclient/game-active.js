
class GameManger
{
    constructor()
    {
        this.scoreData = null;
    }

    async onViewLoad()
    {
        ft_log("onViewLoad-----")
        await gameObject.startEngine()
        this.updateScore(this.scoreData)
    }

    async nonReloadPageLoad(view)
    {
        if (view == "game-active")
        {
            if (viewManager.currentView() == view ||
                viewManager.currentViewLoading == view)
                return
        }
        ft_log("Loading view: '" + view + "' Current: '" + viewManager.currentView()  + "' Loading: '" + viewManager.currentViewLoading + "'")
        return await viewManager.queueView(view, null, false)
    }

    async loadActiveView()
    {
        ft_log("loadActiveView")
        if (!gameObject.replication.connected)
        {
            if (!await gameObject.initLobby())
                return
        }
        var lobbyInfo = gameObject.replication.lobbyInfo
        var matchInfo = gameObject.replication.matchInfo
        if (lobbyInfo.type != "tournament")
        {
            await this.nonReloadPageLoad("game-active", null, false)
            this.updateScore(this.scoreData)
            return
        }
        if (lobbyInfo.state != "WAITING_CONNECT")
        {
            if (matchInfo && matchInfo.type)
                await this.nonReloadPageLoad("game-active", null, false)
            else
                await this.nonReloadPageLoad("tournament-mid-match", null, false)
        }
        else
            await this.nonReloadPageLoad("tournament-lobby", null, false)
        this.updateScore(this.scoreData)
    }

    updateScore(scoreData)
    {
        if (!scoreData)
            return;
        this.scoreData = scoreData;
        for (var score of scoreData)
        {
            var sideName = score.side[0].toUpperCase() + score.side.slice(1)
            var scoreElement = document.getElementById("playerScore" + sideName)
            var nameElement = document.getElementById("playerName" + sideName)
            if (scoreElement)
                scoreElement.innerText = score.score
            if (nameElement)
                nameElement.innerText = score.playerName
        }
    }

    updatePing(ping)
    {
        var obj = document.getElementById("pingTxt")
        if (obj)
            obj.innerText = "Ping: "  + ping
    }

    async leaveLobby()
    {
        await api.request("DELETE", "/api/pong/matchmaking/register/", {})
        gameObject.disconnect()
        viewManager.queueView("gameselection", null, false)
    }

    onGameEnd()
    {
        var matchId = gameObject.replication.lastMatchInfo.id;

        if (gameObject.replication.lastLobbyInfo.type == "tournament")
        {
            matchId = gameObject.replication.lastLobbyInfo.tournamentInfo.id;
            viewManager.queueView("match-result", { matchId: matchId}, false)
            return
        }

        ft_log("onGameEnd")
        setTimeout(()=>{ ft_log("onGameEnd callback"); viewManager.queueView("match-result", { matchId: matchId}, false) }, 3000)
    }

    //async loadMatchResult()
    //{
    //    var result = await api.get(`/api/pong/match/?id=${gameObject.replication.matchInfo.id}`)
    //    if (!result.success)
    //        return
    //    var matchInfo = result.data
    //    var winnerStats = null
    //    for (var stats of matchInfo.stats)
    //    {
    //        if (stats.score == matchInfo.maxScore)
    //        {
    //            winnerStats = stats
    //            break
    //        }
    //    }
    //    var winnerName = document.getElementById("resultNameWinner")
    //    winnerName.parentElement.classList.add(`side-${ winnerStats.side.toLowerCase() }`)
    //    if (matchInfo.type != "local")
    //    {
    //        if (winnerStats.playerName)
    //            winnerName.innerText = winnerStats.playerName
    //        else
    //            winnerName.innerText = winnerStats.user.username
    //    }
    //    else
    //        winnerName.innerText = winnerStats.side == "left" ? "Left" : "Right"
    //}
};

window.gameManager = new GameManger(); 
