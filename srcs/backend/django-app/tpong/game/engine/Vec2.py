import math

class Vec2():
	def __init__(self, x=0, y=0) -> None:
		self.x, self.y = x, y
	
	def __sub__(self, other):
		if isinstance(other, int) or isinstance(other, float):
			return Vec2(self.x - other, self.y - other)
		else:
			return Vec2(self.x - other.x, self.y - other.y)

	def __add__(self, other):
		if isinstance(other, int) or isinstance(other, float):
			return Vec2(self.x + other, self.y + other)
		else:
			return Vec2(self.x + other.x, self.y + other.y)

	def __mul__(self, other):
		if isinstance(other, int) or isinstance(other, float):
			return Vec2(self.x * other, self.y * other)
		else:
			return Vec2(self.x * other.x, self.y * other.y)

	def __truediv__(self, other):
		if isinstance(other, int) or isinstance(other, float):
			return Vec2(self.x / other, self.y / other)
		else:
			return Vec2(self.x / other.x, self.y / other.y)

	def __abs__(self):
		return math.sqrt(self.x**2 + self.y**2)
	
	def __str__(self) -> str:
		return f"{self.x},{self.y}"

	def fromOtherInstance(self, instance):
		self.x = instance.x
		self.y = instance.y

	def copy(self):
		return Vec2(self.x, self.y)

	def distTo(self, other):
		return abs(self - other)
	
	def length(self):
		return abs(self)

	def clamp(self, high, low):
		self.x = max(min(self.x, high), low)
		self.y = max(min(self.y, high), low)

	def rotate(self, angle):
		angle = math.radians(angle)
		x = self.x
		y = self.y
		cos = math.cos(angle)
		sin = math.sin(angle)
		self.x = (x * cos) - (y * sin)
		self.y = (x * sin) + (y * cos)