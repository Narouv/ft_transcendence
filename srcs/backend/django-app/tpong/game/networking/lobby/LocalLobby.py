from .PongLobby import PongLobby, LobbyState
from tpong.game.networking.NetworkedPongGame import NetworkedPongGame
from tpong.models import PongMatch

import logging

logger = logging.getLogger(__name__)

class LocalLobby(PongLobby):
    TYPE="local"
    def __init__(self) -> None:
        super().__init__(1, LocalLobby.TYPE)
        match = PongMatch(type=LocalLobby.TYPE, maxScore=3)
        match.save()
        self.gameInstance = NetworkedPongGame(self, match)

    def onConnect(self, connection):
        self.gameInstance.currentMatch.addPlayer(self.registeredUser[0])
        self.gameInstance.connectPlayer(connection)
    
    def onDisconnect(self, connection):
        self.gameInstance.disconnectPlayer(connection)

    def onLobbyReady(self):
        self.lobbyState = LobbyState.RUNNING
        self.gameInstance.startGame()

    def onGameStateChange(self, game : NetworkedPongGame, state):
        if state == "gameover":
           self.broadcastLobbyEvent({ 'event': 'lobby-closing' })
            #PongLobbyManager.lobbyManagerInstance.destroyLobby()

    def onGameTick(self, delta):
        self.gameInstance.gameTick(delta)

    def onClientData(self, connection, data):
        if data['type'] == 'input':
            self.gameInstance.handleRemoteInput(data['inputInfo'], connection.user)

    async def onSyncClients(self):
        await self.gameInstance.syncClients()

    def onLobbyDestruct(self):
        pass

    def onUserLeave(self, user):
        pass