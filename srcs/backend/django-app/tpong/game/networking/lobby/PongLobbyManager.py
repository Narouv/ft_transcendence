from .LocalLobby import LocalLobby
from .PvPLobby import PvPLobby
from .PongLobby import LobbyState
from .TournamentLobby import TournamentLobby
from asgiref.sync import async_to_sync,sync_to_async
import threading
import logging
import time

logger = logging.getLogger(__name__)

class PongLobbyManager():
	def __init__(self) -> None:
		self.lobbys = []
		self.runEventThread = True
		self.gameThread = threading.Thread(target=self.gameThreadLoop, args=(), kwargs={})
		self.eventThread = threading.Thread(target=self.eventThreadLoop, args=(), kwargs={})
		self.gameThread.setDaemon(True)
		self.eventThread.setDaemon(True)
		self.gameThread.start()
		self.eventThread.start()
		
		logger.warning("Created PongLobbyManager - Started thread")

		self.lobbyTypes = [LocalLobby, PvPLobby, TournamentLobby]

	async def destroy(self):
		self.runEventThread = False

	def createLobby(self, lobbyType):
		lobby = None
		for availType in self.lobbyTypes:
			if availType.TYPE == lobbyType:
				lobby = availType()
		if lobby is None:
			return False
		self.lobbys.append(lobby)
		logger.warning(f"Created lobby type { lobby.type }")
		return lobby

	def destroyLobby(self, lobby):
		lobby.onDestruct()
		self.lobbys.remove(lobby)

	def registerConnection(self, userConnection):
		for lobby in self.lobbys:
			if userConnection.user in lobby.registeredUser:
				lobby.connectPlayer(userConnection)
				return lobby
		return None

	def unregisterConnection(self, userConnection):
		for lobby in self.lobbys:
			if userConnection in lobby.playerConnections:
				lobby.disconnectPlayer(userConnection)
				if not len(lobby.playerConnections):
					self.destroyLobby(lobby)
				return True
		logger.warning(f"No associated lobby for disconnecting client found")
		return False

	def registerUserToLobby(self, lobby, user):
		for alobby in self.lobbys:
			if user in alobby.registeredUser:
				return False
		lobby.registeredUser.append(user)
		return True
	
	def userLobbyLeave(self, user):
		lobby = self.getLobbyFromUser(user, None)
		if not lobby:
			return False
		lobby.registeredUser.remove(user)
		lobby.onUserLeave(user)
		return True

	def getLobbyFromUser(self, user, type):
		for alobby in self.lobbys:
			if type is not None and type != alobby.type:
				continue
			if user in alobby.registeredUser:
				return alobby
		return False
	
	def gameThreadLoop(self):
		lastTickTime = time.time()

		while self.runEventThread:
			delta = time.time() - lastTickTime
			lastTickTime = time.time()
			for lobby in self.lobbys:
				lobby.gameTick(delta)
			time.sleep(0.013)


	def eventThreadLoop(self):
		self.lastSyncTime = time.time()

		while self.runEventThread:
			self.syncGameLobbys()
			time.sleep(0.07)

	def syncGameLobbys(self):
		if time.time() - self.lastSyncTime < 0.05:
			return
		self.lastSyncTime = time.time()
		for lobby in self.lobbys:
			async_to_sync(lobby.syncClients)()

	def enterUserMatchmaking(self, user, lobbyType):
		for lobby in self.lobbys:
			if lobby.type != lobbyType:
				continue
			if lobby.lobbyState != LobbyState.WAITING_CONNECT:
				continue
			if not self.registerUserToLobby(lobby, user):
				return False
			return lobby
		lobby = self.createLobby(lobbyType)
		if not lobby:
			return False
		if not self.registerUserToLobby(lobby, user):
			self.destroyLobby(lobby)
			return False
		return lobby
	

lobbyManagerInstance = PongLobbyManager()

