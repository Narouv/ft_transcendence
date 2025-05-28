from .gameObjects.Paddle import Paddle
from .gameObjects.PongBall import PongBall
from .gameObjects.MapBorder import MapBorder
from .CollisionManager import CollisionManager
import logging

logger = logging.getLogger(__name__)

class PongGameEngine():
	def __init__(self, lobby) -> None:
		self.collisionManager = CollisionManager()
		self.pongBall = PongBall()
		self.paddles = {
			'left': Paddle('left'),
			'right': Paddle('right')
		}
		self.mapBorder = MapBorder()
		self.collisionManager.addObject(self.pongBall)
		self.collisionManager.addObject(self.mapBorder)
		self.collisionManager.addObject(self.paddles['left'])
		self.collisionManager.addObject(self.paddles['right'])
		self.owningLobby = lobby

	def simulate(self, delta):
		self.pongBall.simulate(delta)
		self.paddles['left'].simulate(delta)
		self.paddles['right'].simulate(delta)
		self.collisionManager.runCollision()
	
	def serializeState(self):
		return [self.pongBall.serializeState(), self.paddles['left'].serializeState(), self.paddles['right'].serializeState()]

	def resetOjects(self):
		self.pongBall.reset()
		self.paddles['left'].reset()
		self.paddles['right'].reset()
	