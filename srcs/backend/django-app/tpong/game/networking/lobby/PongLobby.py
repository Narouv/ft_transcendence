from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from threading import Lock
from enum import Enum
import uuid

import logging

logger = logging.getLogger(__name__)

class LobbyState(Enum):
	WAITING_CONNECT = "WAITING_CONNECT"
	RUNNING = "RUNNING"
	FINISHED = "FINISHED"
	IDLE = "IDLE"

	def __str__(self):
		return str(self.value)

class PongLobby():
	def __init__(self, lobbySize, type) -> None:
		self.uuid = uuid.uuid1()
		self.playerLock = Lock()
		self.registeredUser = []
		self.playerConnections = []
		self.playersDisconnected = []
		self.maxConnection = lobbySize
		self.lobbyState = LobbyState.WAITING_CONNECT
		self.type = type

	def connectPlayer(self, connection):
		if (connection.user not in self.registeredUser or
			(self.lobbyState is not LobbyState.WAITING_CONNECT and
			connection.user not in self.playersDisconnected)):
			return False
		activeUserConnections = [activeConnection for activeConnection in self.playerConnections if activeConnection.user == connection.user]
		if len(activeUserConnections):
			for activeConnection in activeUserConnections:
				async_to_sync(activeConnection.close)()
		self.broadcastLobbyEvent({ 'event': 'player-connect' })
		self.onConnect(connection)
		self.playerLock.acquire()
		self.playerConnections.append(connection)
		async_to_sync(get_channel_layer().group_add)(str(self.uuid), connection.channel_name)
		self.playerLock.release()
		if len(self.playerConnections) is self.maxConnection and self.lobbyState is LobbyState.WAITING_CONNECT:
			self.onLobbyReady()

	def disconnectPlayer(self, connection):
		self.playerLock.acquire()
		self.playersDisconnected.append(connection.user)
		self.playerConnections.remove(connection)
		async_to_sync(get_channel_layer().group_discard)(str(self.uuid), connection.channel_name)
		self.playerLock.release()
		self.onDisconnect(connection)
		self.broadcastLobbyEvent({ 'event': 'player-disconnect' })

	def gameTick(self, delta):
		self.onGameTick(delta)

	async def syncClients(self):
		await self.onSyncClients()

	def handleClientData(self, connection, data):
		if data['type'] == "ping":
			async_to_sync(connection.send_json)({
				"type": "pong",
				"data": data['timestamp']
			})
			return
		self.onClientData(connection, data)
		async_to_sync(self.syncClients)

	def broadcastLobbyEvent(self, event):
		self.broadcastLobby({
			'type': 'lobby-event',
			'data': event
		})

	def broadcastLobby(self, data):
		logger.warning(f"Sending data to {len(self.playerConnections)} connections")
		self.playerLock.acquire()
		async_to_sync(get_channel_layer().group_send)(str(self.uuid), { "type": "pong.send", "data": data})
		self.playerLock.release()
		#self.playerLock.acquire()
		#arrLen = len(self.playerConnections)
		#self.playerLock.release()
		#index = 0
		#while index < arrLen:
		#	self.playerLock.acquire()
		#	arrLen = len(self.playerConnections)
		#	if index >= arrLen:
		#		self.playerLock.release()
		#		break
		#	logger.warning(f"Sending {data} to {self.playerConnections[index].user}")
		#	async_to_sync(self.playerConnections[index].send_json)(data)
		#	self.playerLock.release()
		#	index += 1
	
		#self.playerLock.acquire()
		#for connectedPlayer in self.playerConnections:
		#	logger.warning(f"Sending {data} to {connectedPlayer.user}")
		#	connectedPlayer.ssafe_send_json(data)
		#self.playerLock.release()

	def serialize(self):
		return {
			"uuid": str(self.uuid),
			"type": self.type,
			"state": str(self.lobbyState),
		}
	
	def onDestruct(self):
		self.onLobbyDestruct()