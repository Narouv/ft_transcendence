from tpong.game.structure.PongGame import PongGame
from tpong.models import PongMatch, PongStats
from tpong.serializers import PongMatchSerializer, StatsSerializer
from channels.layers import get_channel_layer

from asgiref.sync import async_to_sync

import logging

logger = logging.getLogger(__name__)

class PongPlayer():
	def __init__(self, connection) -> None:
		self.connection = connection
		self.user = connection.user
		self.side = None

class NetworkedPongGame(PongGame):
	def __init__(self, lobby, currentMatch) -> None:
		super().__init__(lobby, currentMatch)
		self.player = []
		self.clGroupName = f"{str(lobby.uuid)}__{currentMatch.id}" 

	def connectPlayer(self, connection):
		logger.warning("Connected player to NetworkedPongGame")
		self.player.append(PongPlayer(connection))
		if self.currentMatch.type == "local":
			stats = PongStats(side="both")
		else:
			stats = self.currentMatch.getPlayerStatsFromUser(connection.user)
		matchInfo =	PongMatchSerializer(self.currentMatch).data
		matchInfo["controllingSide"] = stats.side
		connection.ssafe_send_json({
			'success': True,
			'type': 'matchinfo',
			'data': matchInfo
		})
		async_to_sync(get_channel_layer().group_add)(self.clGroupName, connection.channel_name)
		self.broadcastEvent({
			"event": "score-change",
			"score": StatsSerializer(self.currentMatch.stats.all(), many=True).data
		})
	
	def isPlayerConnected(self, user):
		return len([player for player in self.player if player.user == user]) != 0

	def disconnectPlayer(self, connection):
		async_to_sync(get_channel_layer().group_discard)(self.clGroupName, connection.channel_name)
		for player in self.player:
			if player.connection == connection:
				self.player.remove(player)
				return

	def handleRemoteInput(self, inputData, user):
		if self.currentMatch.type != "local":
			stat = self.currentMatch.getPlayerStatsFromUser(user)
			if inputData['side'] == "left" != stat.side:
				return
			if inputData['side'] == "right" != stat.side:
				return
		self.paddles[inputData['side']].processRemoteInput(inputData)

	async def syncClients(self):
		data = {
			'type': 'replicate',
			'data': self.serializeState()
		}
		await get_channel_layer().group_send(self.clGroupName, { "type": "pong.send", "data": data})

		#for connectedPlayer in self.player:
		#	try:
		#		connectedPlayer.connection.sendLock.acquire()
		#		await connectedPlayer.connection.send_json(data)
		#		connectedPlayer.connection.sendLock.release()
		#	except:
		#		logger.error(f"Error syncing client { connectedPlayer.user }")
		#		logger.error(f"Player { self.player }")
		#		connectedPlayer.connection.sendLock.release()
		#		await connectedPlayer.connection.close()

	def broadcastEvent(self, event):
		data = {
			'type': 'game-event',
			'data': event
		}
		self.broadcast(data)

	def broadcast(self, data):
		async_to_sync(get_channel_layer().group_send)(self.clGroupName, { "type": "pong.send", "data": data})
		#for connectedPlayer in self.player:
		#	connectedPlayer.connection.ssafe_send_json(data)

		#try:
		#except:
		#	logger.error("Error broadcasting event")