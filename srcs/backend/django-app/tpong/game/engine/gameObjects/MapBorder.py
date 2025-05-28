from tpong.game.engine.Vec2 import Vec2
from .Collidable import Collidable
import logging

logger = logging.getLogger(__name__)

class MapBorder(Collidable):
	
	def __init__(self) -> None:
		super().__init__('border')
		self.size = Vec2(1,1)
		self.collisionCallback = None

	def onCollision(self, collision, collidedWith):
		if callable(self.collisionCallback):
			func = self.collisionCallback
			func(collision)