class DoublyLinkedList:
	
	def __init__(self):
		self.first = None
		self.last = None

	def addToFront(self, e):
		e.right = self.first
		e.left = None
		
		if self.first is not None:
			self.first.left = e
		self.first = e
		
		if self.last is None:
			self.last = self.first
	
	def moveToFront(self, e):
		if e == self.first:
			return		
		self.remove(e)
		self.addToFront(e)
	
	def remove(self, e):
		if e.right is not None:
			e.right.left = e.left
		else:  # The last is removed
			self.last = self.last.left
		if e.left is not None:
			e.left.right = e.right

	def getFirst(self):
		return self.first
	
	def getLast(self):
		return self.last

	def removeLast(self):
		self.remove(self.last)
