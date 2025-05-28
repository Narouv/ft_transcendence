from tpong.models import PongMatch
from tpong.game.networking.NetworkedPongGame import NetworkedPongGame
import math
import logging

logger = logging.getLogger(__name__)

class PongTournament():
    def __init__(self, lobby) -> None:
        self.tournamentLobby = lobby
        self.lobbyMatch = PongMatch(type="tournament")
        self.lobbyMatch.save()
        self.activeGames : NetworkedPongGame = []
        self.toggleReady = 0
        self.round = 0
        self.players = None
        self.dummy = None
        self.subMatchMaxScore = 3

    def startTournament(self):
        logger.warning("Starting tournament")
        self.players = list(self.tournamentLobby.playerConnections)
        self.tournamentMatchmaking()
        self.lobbyMatch.maxScore = (len(self.tournamentLobby.playerConnections) - 1) * self.subMatchMaxScore
        self.lobbyMatch.status = "running"
        self.lobbyMatch.save()

    def tournamentMatchmaking(self):
        logger.warning(f"Matchmaking begin with {len(self.players)} players {len(self.players) % 2}")
        for player in self.players:
            logger.warning(f"Player in match: {player.user}")
        if len(self.players) % 2:
            logger.warning("Player count un-even")
            for game in range(1, len(self.players) // 2 + 1):
                logger.warning(f"1gameIdx = {game}")
                logger.warning(f'{self.players[game - 1].user.username} vs {self.players[-game - 1].user.username}')
                self.createTournamentMatch(self.players[game - 1], self.players[-game - 1])
            self.players.insert(0, self.players.pop())
        else:
            logger.warning("Player count even")
            self.dummy = self.players.pop()
            for game in range(1, (len(self.players) // 2) + 1):
                logger.warning(f"2gameIdx = {game}")
                logger.warning(f'{self.players[game - 1].user.username} vs {self.players[-game - 1].user.username}')
                self.createTournamentMatch(self.players[game - 1], self.players[-game - 1])
            logger.warning(f'{self.players[- 1].user.username} vs {self.dummy.user.username}')
            self.createTournamentMatch(self.players[-1], self.dummy)
            self.players.insert(0, self.players.pop())
            self.players.append(self.dummy)
        logger.warning(f"Matchmaking end with {len(self.players)} players")
        for player in self.players:
            logger.warning(f"Player in match: {player.user}")

    def createTournamentMatch(self, player1, player2):
        logger.warning("Creating tournament sub-match")
        match = PongMatch(type="tournamentMatch", maxScore=self.subMatchMaxScore)
        match.save()
        match.addPlayer(player1.user)
        match.addPlayer(player2.user)
        game = NetworkedPongGame(self.tournamentLobby, match)
        game.connectPlayer(player1)
        game.connectPlayer(player2)
        self.activeGames.append(game)
        game.startGame()

    def checkRoundState(self):
        if not len(self.activeGames):
            self.tournamentLobby.onTournamentStateChange("roundover")

    def checkTournamentstate(self):
        if len(self.players) % 2:
            rnum = len(self.players)
        else:
            rnum = len(self.players) - 1
        if self.round == rnum:
            self.lobbyMatch.status = "finished"
            self.lobbyMatch.save()
            self.tournamentLobby.onTournamentStateChange("tournamentover")
        else:
            self.tournamentMatchmaking()

    def playerDisconnect(self, connection):
        logger.warning("Player disconnected from tournament")

    def onGameTick(self, delta):
        for game in self.activeGames:
            game.gameTick(delta)

    def onClientData(self, connection, data):
        if data['type'] == 'input':
            for game in self.activeGames:
                if not game.isPlayerConnected(connection.user):
                    continue
                game.handleRemoteInput(data['inputInfo'], connection.user)
                return

    async def onSyncClients(self):
        for game in self.activeGames:
            await game.syncClients()

