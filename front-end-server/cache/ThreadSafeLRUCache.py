from threading import Lock

from .LRUCache import LRUCache

class ThreadSafeLRUCache(LRUCache):
	def __init__(self, size):
		super(ThreadSafeLRUCache, self).__init__(size)
		self.mutex = Lock()
		
	def getEntry(self, key):
		self.mutex.acquire()
		value = super(ThreadSafeLRUCache, self).getEntry(key)
		self.mutex.release()
		return value
		
	def loadEntry(self, key, value):
		self.mutex.acquire()
		super(ThreadSafeLRUCache, self).loadEntry(key, value)
		self.mutex.release()
		
	def writeEntry(self, key, value, writeToLowerMemory):
		self.mutex.acquire()
		super(ThreadSafeLRUCache, self).writeEntry(key, value, writeToLowerMemory)
		self.mutex.release()
		
	def deleteEntry(self, key, deleteFromLowerMemory):
		self.mutex.acquire()
		super(ThreadSafeLRUCache, self).deleteEntry(key, value, deleteFromLowerMemory)
		self.mutex.release()
