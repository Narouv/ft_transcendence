from .PongLobby import PongLobby, LobbyState
from tpong.game.networking.NetworkedPongGame import NetworkedPongGame
from tpong.models import PongMatch, PongStats
import logging

logger = logging.getLogger(__name__)

class PvPLobby(PongLobby):
    TYPE="pvp"
    def __init__(self) -> None:
        super().__init__(2, PvPLobby.TYPE)
        match = PongMatch(type=PvPLobby.TYPE, maxScore=3)
        match.save()
        self.gameInstance = NetworkedPongGame(self, match)

    def onConnect(self, connection):
        self.gameInstance.currentMatch.addPlayer(connection.user)
        self.gameInstance.connectPlayer(connection)
    
    def onDisconnect(self, connection):
        self.gameInstance.disconnectPlayer(connection)

    def onLobbyReady(self):
        self.lobbyState = LobbyState.RUNNING
        self.gameInstance.startGame()

    def onGameTick(self, delta):
        self.gameInstance.gameTick(delta)

    def onGameStateChange(self, game, state):
        if state == "gameover":
           self.registeredUser = []
           self.broadcastLobbyEvent({ 'event': 'lobby-closing' })

    def onClientData(self, connection, data):
        if data['type'] == 'input':
            self.gameInstance.handleRemoteInput(data['inputInfo'], connection.user)

    async def onSyncClients(self):
        await self.gameInstance.syncClients()
        
    def onLobbyDestruct(self):
        if self.lobbyState == LobbyState.WAITING_CONNECT:
            self.gameInstance.currentMatch.delete()
    
    def onUserLeave(self, user):
        playerLeft = self.gameInstance.currentMatch.stats.all().exclude(user=user)
        logger.warning(f"Player left {playerLeft}")
        if len(playerLeft) == 1:
            logger.warning(f"Setting score {self.gameInstance.currentMatch.maxScore}")
            playerLeft[0].score = self.gameInstance.currentMatch.maxScore
            playerLeft[0].save()
            self.gameInstance.onGameOver(playerLeft[0])
        