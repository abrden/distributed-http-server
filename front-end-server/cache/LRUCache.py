from .DoublyLinkedList import DoublyLinkedList

class LRUCacheEntry:
	
	def __init__(self, key, value):
		self.key = key
		self.value = value
		self.left = None
		self.right = None

class LRUCache:

	def __init__(self, size):
		self.size = size
		self.dict = {}
		self.list = DoublyLinkedList()

	def hasEntry(self, key):
		return key in self.dict
		
	def getEntry(self, key):
		e = self.dict[key]
		self.list.moveToFront(e)
		return self.dict[key].value

	def loadEntry(self, key, value):
		if self.hasEntry(key):
			e = self.dict[key]
			e.value = value
			self.list.moveToFront(e)
		elif self.size > 0:
			if len(self.dict) == self.size:
				del self.dict[self.list.getLast().key]
				self.list.removeLast()
			e = LRUCacheEntry(key, value)
			self.dict[key] = e
			self.list.addToFront(e)
			
	def writeEntry(self, key, value, writeToLowerMemory):
		writeToLowerMemory(key, value)
		self.loadEntry(key, value)
		
	def deleteEntry(self, key, deleteFromLowerMemory):
		deleteFromLowerMemory(key)
		if self.hasEntry(key):
			e = self.dict[key]
			del self.dict[key]
			self.list.remove(e)
