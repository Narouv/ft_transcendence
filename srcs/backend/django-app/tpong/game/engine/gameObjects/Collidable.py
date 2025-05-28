from tpong.game.engine.Vec2 import Vec2
import logging

logger = logging.getLogger(__name__)

class Collidable():
	def __init__(self, type) -> None:
		self.type = type
		self.position = Vec2()
		self.velocity = Vec2()
		self.stateChanged = False
		