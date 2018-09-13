import unittest
import sys, os
sys.path.append(os.path.abspath(os.path.join('..')))

from cache.LRUCache import LRUCache


class TestLRUCacheMethods(unittest.TestCase):

	def testHasEntryWithoutLoad(self):
		c = LRUCache(5)
		self.assertFalse(c.hasEntry('hello'))

	def testHasEntryWithLoad(self):
		c = LRUCache(5)
		c.loadEntry('hello', 'world')
		self.assertTrue(c.hasEntry('hello'))

	def testHasEntryWithLoadAndSizeZero(self):
		c = LRUCache(0)
		c.loadEntry('hello', 'world')
		self.assertFalse(c.hasEntry('hello'))

	def testHasEntryWithLoadAndSizeOne(self):
		c = LRUCache(1)
		c.loadEntry('hello', 'world')
		self.assertTrue(c.hasEntry('hello'))
		c.loadEntry('yellow', 'duck')
		self.assertTrue(c.hasEntry('yellow'))
		self.assertFalse(c.hasEntry('hello'))

	def testEvictionWithoutLookup(self):
		c = LRUCache(3)
		c.loadEntry('hello', 'world')
		c.loadEntry('yellow', 'duck')
		c.loadEntry('blue', 'sky')
		c.loadEntry('brown', 'bear')

		self.assertFalse(c.hasEntry('hello'))
		self.assertTrue(c.hasEntry('yellow'))
		self.assertTrue(c.hasEntry('blue'))
		self.assertTrue(c.hasEntry('brown'))

	def testEvictionWithLookup(self):
		c = LRUCache(3)
		c.loadEntry('hello', 'world')
		c.loadEntry('yellow', 'duck')
		c.loadEntry('blue', 'sky')
		c.getEntry('hello')
		c.loadEntry('brown', 'bear')

		self.assertTrue(c.hasEntry('hello'))
		self.assertFalse(c.hasEntry('yellow'))
		self.assertTrue(c.hasEntry('blue'))
		self.assertTrue(c.hasEntry('brown'))


if __name__ == '__main__':
	unittest.main()
