class Rect():
	def __init__(self, x, y, w, h):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
	
	@property
	def min(self):
		return (self.x, self.y)
	
	@property
	def max(self):
		return (self.x + self.w, self.y + self.h)
	
	@property
	def center(self):
		return (self.x + int(self.w / 2), self.y + int(self.h / 2))

	def expand(self, x, y):
		self.x -= x
		self.y -= y
		self.w += 2 * x
		self.h += 2 * y

	def __str__(self):
		return f"{{x: {self.x}, y: {self.y}, w: {self.w}, h: {self.h}}}"