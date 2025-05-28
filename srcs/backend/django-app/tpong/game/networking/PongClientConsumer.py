from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async, async_to_sync
from .lobby import PongLobbyManager
from autobahn.exception import Disconnected
from threading import Lock
import logging

logger = logging.getLogger(__name__)

class PongClientConsumer(AsyncJsonWebsocketConsumer):
	def __init__(self) -> None:
		super().__init__()
		self.registerd = False
		self.lobby = None
		self.sendLock = Lock()
		self.connected = False

	def validate(self):
		if self.registerd:
			return True
		self.lobby = PongLobbyManager.lobbyManagerInstance.registerConnection(self)
		if self.lobby != None:
			return True
		return False

	async def connect(self):
		self.connected = True
		self.user = self.scope['user']
		if not self.user.id:
			self.connected = False
			return await self.close()
		await self.accept("pong")
		if not await sync_to_async(self.validate)():
			logger.warning(f'Denying user: {self.user} { self.user.id }')
			await self.send_json({'success': False, 'message': 'Cant register'})
			return await self.close()
		self.registerd = True
		await self.send_json({
			'success': True,
			'type': 'lobbyinfo',
			'data': self.lobby.serialize(), 
			'msg': 'Sucessfull registered in lobby!'
		})
		logger.warning(f'Connected user: {self.user}')

	async def disconnect(self, close_code):
		self.connected = False
		logger.warning(f"Disconnecting player {self.user}")
		await sync_to_async(PongLobbyManager.lobbyManagerInstance.unregisterConnection)(self)

	async def receive_json(self, content):
		if not self.registerd:
			return await self.close()
		await sync_to_async(self.lobby.handleClientData)(self, content)

	async def pong_send(self, event):
		await self.send_json(event["data"])

	def ssafe_send_json(self, data):
		if not self.connected:
			return
		self.sendLock.acquire()
		try:
			async_to_sync(self.send_json)(data)
		except Disconnected:
			logger.warning("Tried sending on closed connection!")
		self.sendLock.release()
