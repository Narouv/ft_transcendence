from .Vec2 import Vec2
import logging

logger = logging.getLogger(__name__)

class CollisionManager():
	def __init__(self) -> None:
		self.collidables = []

	def addObject(self, collidableObject):
		self.collidables.append(collidableObject)
	
	def removeObject(self, collidableObject):
		self.collidables.remove(collidableObject)

	def hasCollidedAlready(self, collisionsHappened, collidable, collidableToCheck):
		for collision in collisionsHappened:
			if collision['a'] == collidable or collision['a'] == collidableToCheck:
				if collision['b'] == collidable or collision['b'] == collidableToCheck:
					return True
		return False
	
	def checkCollisionCircleRect(self, circle, rect):
		closestPoint = circle.position.copy()
		collisionSide = Vec2()
		if circle.position.x < rect.position.x:
			collisionSide.x = 1#'right'
			closestPoint.x = rect.position.x
		elif circle.position.x > rect.position.x + rect.size.x:
			collisionSide.x = -1#'left'
			closestPoint.x = rect.position.x + rect.size.x
		if circle.position.y < rect.position.y:
			collisionSide.y = -1#'bottom'
			closestPoint.y = rect.position.y
		elif circle.position.y > rect.position.y + rect.size.y:
			collisionSide.y = 1#'top'
			closestPoint.y = rect.position.y + rect.size.y
		if circle.position.distTo(closestPoint) > circle.radius:
			return {'collision': False }
		clipPos = Vec2()
		if collisionSide.y < 0.9:
			if rect.side == "right":
				collisionSide.x = 1#'right'
			elif rect.side == "left":
				collisionSide.x = -1#'left'
		if circle.position.x < rect.position.x + (rect.size.x / 2):
			clipPos.x = rect.position.x - circle.radius
		elif circle.position.x >= rect.position.x + (rect.size.x / 2):
			clipPos.x = rect.position.x + rect.size.x + circle.radius
		if circle.position.y < rect.position.y + (rect.size.y / 2):
			clipPos.y = rect.position.y - (circle.radius )
		elif circle.position.y >= rect.position.y + (rect.size.y / 2):
			clipPos.y = rect.position.y + rect.size.y + circle.radius
		if collisionSide.y == 1 or collisionSide.y == -1:
			clipPos.x = 0
		else:
			clipPos.y = 0
		return {
			'collision': collisionSide.length(),
			'side': collisionSide,
			'clipPos': clipPos
		}

	def checkCollisionCircleBorder(self, circle, border):
		collisionSide = Vec2()
		if circle.position.x - circle.radius <= border.position.x:
			collisionSide.x = -1
		if circle.position.x + circle.radius >= border.position.x + border.size.x:
			collisionSide.x = 1
		if circle.position.y - circle.radius <= border.position.y:
			collisionSide.y = 1
		if circle.position.y + circle.radius >= border.position.y + border.size.y:
			collisionSide.y = -1
		return {
			'collision': collisionSide.length() != 0,
			'side': collisionSide,
			'clipPos': Vec2()
		}
	
	def checkCollision(self, objA, objB):
		if objA.type == 'circle' and objB.type == 'rect':
			return self.checkCollisionCircleRect(objA, objB)
		if objB.type == 'circle' and objA.type == 'rect':
			return self.checkCollisionCircleRect(objB, objA)

		if objA.type == 'circle' and objB.type == 'border':
			return self.checkCollisionCircleBorder(objA, objB)
		if objB.type == 'circle' and objA.type == 'border':
			return self.checkCollisionCircleBorder(objB, objA)
		return {'collision': False}

	def runCollision(self):
		collisionsHappened = []
		for collidable in self.collidables:
			if collidable.type == "border":
					continue
			for collidableToCheck in self.collidables:
				if collidable == collidableToCheck:
					continue
				if collidableToCheck.type == "border":
					continue
				if self.hasCollidedAlready(collisionsHappened, collidable, collidableToCheck):
					continue
				collision = self.checkCollision(collidable, collidableToCheck)
				if not collision['collision']:
					continue
				collisionsHappened.append({
					'a': collidable,
					'b': collidableToCheck
				})
				collidable.onCollision(collision, collidableToCheck)
				collidableToCheck.onCollision(collision, collidable)
				return
		for collidable in self.collidables:
			if collidable.type != "border":
				continue
			for collidableToCheck in self.collidables:
				if collidable == collidableToCheck:
					continue
				if self.hasCollidedAlready(collisionsHappened, collidable, collidableToCheck):
					continue
				collision = self.checkCollision(collidable, collidableToCheck)
				if not collision['collision']:
					continue
				collisionsHappened.append({
					'a': collidable,
					'b': collidableToCheck
				})
				collidable.onCollision(collision, collidableToCheck)
				collidableToCheck.onCollision(collision, collidable)
				return
		
