from tpong.game.engine.Vec2 import Vec2
from .Collidable import Collidable
import logging

logger = logging.getLogger(__name__)

class Paddle(Collidable):
	def __init__(self, side) -> None:
		super().__init__('rect')
		self.size = Vec2(0.03, 0.2)
		self.heightNormal = 0.5
		self.side = side
		self.maxVelocity = 0.7
		self.collosionCallback = None
		self.keystate = {
			"up": False,
			"down": False,
		}

	def simulate(self, delta):
		self.radiusNormal = 0.01
		self.heightNormal += self.velocity.y * delta
		self.heightNormal = max(min(self.heightNormal, 1), 0)
		self.updatePosition()
		self.stateChanged = abs(self.velocity.y) > 0.01 

	def updatePosition(self):
		x = 0
		if self.side == 'right':
			x = 1 - self.size.x
		self.position.x = x
		self.position.y = self.heightNormal * (1 - self.size.y)

	def replicate(self, replicationInfo):
		self.heightNormal = replicationInfo['paddleHeight']
		self.velocity.y = replicationInfo['paddleVelocity']

	def serializeState(self):
		return {
			'objName': 'paddle',
			'paddleHeight': self.heightNormal,
			'paddleVelocity': self.velocity.y,
			'paddleSide': self.side,
			'paddleSize': {
				'x': self.size.x,
				'y': self.size.y
			}
		}
	
	def onCollision(self, collision, collidedWith):
		if callable(self.collisionCallback):
			func = self.collisionCallback
			func(collision, self.side)

	def processInput(self):
		newVel = 0
		if self.keystate["up"]:
			newVel -= self.maxVelocity
		if self.keystate["down"]:
			newVel += self.maxVelocity
		self.velocity.y = newVel
		self.stateChanged = True
		
	def processRemoteInput(self, remoteInput):
		self.keystate[remoteInput['dir']] = remoteInput['keyDown']
		self.processInput()


	def reset(self):
		self.heightNormal = 0.5
		self.velocity.y = 0