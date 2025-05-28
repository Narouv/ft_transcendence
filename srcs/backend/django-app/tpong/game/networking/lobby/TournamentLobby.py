from tpong.game.structure.PongTournament import PongTournament
from .PongLobby import PongLobby, LobbyState
from tpong.models import PongMatch
from web3db.web3Score.web3Score import Web3TournamentScore
from web3 import Web3
import datetime
import logging

logger = logging.getLogger(__name__)

class TournamentLobby(PongLobby):
    TYPE="tournament"
    def __init__(self) -> None:
        super().__init__(12, TournamentLobby.TYPE)
        self.tournament = PongTournament(self)
        self.votedForStart = []

    def onConnect(self, connection):
        self.tournament.lobbyMatch.addPlayer(connection.user)

    def onDisconnect(self, connection):
        if connection.user in self.votedForStart:
            self.votedForStart.remove(connection.user)
        self.tournament.playerDisconnect(connection)

    def onLobbyReady(self):
        self.lobbyState = LobbyState.RUNNING
        self.broadcastLobby({
                'type': 'lobbyinfo',
                'data': self.serialize(),
            })
        logger.warning("Lobby ready")
        self.tournament.startTournament()
        self.broadcastLobbyEvent({ 'event': 'tournament-start' })

    def onGameStateChange(self, game, state):
        if state == "gameover":
            for stat in game.currentMatch.stats.all():
                tstat = self.tournament.lobbyMatch.stats.get(user=stat.user)
                tstat.score += stat.score
                tstat.save()
            self.tournament.activeGames.remove(game)
            self.tournament.checkRoundState()

    def onTournamentStateChange(self, state):
        if state == "roundover":
            self.tournament.round += 1
            self.tournament.checkTournamentstate()
        if state == "tournamentover":
            self.registeredUser = []
            self.broadcastLobbyEvent({ 'event': 'lobby-closing' })

    def recieveStartVote(self, connection, data):
        if (connection.user in self.votedForStart or
            self.lobbyState != LobbyState.WAITING_CONNECT):
            return
        self.votedForStart.append(connection.user)
        votedCount = len(self.votedForStart)
        if votedCount >= 3 and votedCount == len(self.playerConnections):
            self.onLobbyReady()
        else:
            self.broadcastLobbyEvent({ 'event': 'player-connect' })

    def activePlayers(self):
        activePlayers = []
        for game in self.tournament.activeGames:
            for player in game.playerConnections:
                activePlayers.append(player)
        return activePlayers

    def waitingPlayers(self):
        activePlayers = self.activePlayers()
        return [player for player in self.playerConnections if player not in activePlayers]

    def onGameTick(self, delta):
        self.tournament.onGameTick(delta)

    def onClientData(self, connection, data):
        if data["type"] == "vote-start":
           self.recieveStartVote(connection, data)
        self.tournament.onClientData(connection, data)

    async def onSyncClients(self):
        await self.tournament.onSyncClients()

    def onLobbyDestruct(self):
        if self.lobbyState == LobbyState.WAITING_CONNECT:
            self.tournament.lobbyMatch.delete()
        else:
            tournamentId = "tournament_" + str(self.tournament.lobbyMatch.id)
            statData = []
            for rank, stat in enumerate(self.tournament.lobbyMatch.stats.all().order_by("-score")):
                statData.append({"userId": stat.user.id, "score": stat.score, "rank": rank})
            try:
                Web3TournamentScore.getInstance().setTournamentScore(tournamentId, {
                    "stats": statData,
                    "playedAt": str(int(self.tournament.lobbyMatch.created_at.timestamp()))
                })
            except ValueError as exception:
                logger.warning(f"Error saving score to blockchain: { exception }")

    def onUserLeave(self, user):
        pass

    def serialize(self):
        obj = super().serialize()
        obj["tournamentInfo"] = {
            "id": self.tournament.lobbyMatch.id,
            "state": str(self.lobbyState),

        }
        return obj