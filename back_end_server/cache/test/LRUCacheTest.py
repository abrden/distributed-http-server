import unittest
import sys, os
sys.path.append(os.path.abspath(os.path.join('..')))

from cache.LRUCache import LRUCache


class TestLRUCacheMethods(unittest.TestCase):

	def testHasEntryWithoutLoad(self):
		c = LRUCache(5)
		self.assertFalse(c.has_entry('hello'))

	def testHasEntryWithLoad(self):
		c = LRUCache(5)
		c.load_entry('hello', 'world')
		self.assertTrue(c.has_entry('hello'))

	def testHasEntryWithLoadAndSizeZero(self):
		c = LRUCache(0)
		c.load_entry('hello', 'world')
		self.assertFalse(c.has_entry('hello'))

	def testHasEntryWithLoadAndSizeOne(self):
		c = LRUCache(1)
		c.load_entry('hello', 'world')
		self.assertTrue(c.has_entry('hello'))
		c.load_entry('yellow', 'duck')
		self.assertTrue(c.has_entry('yellow'))
		self.assertFalse(c.has_entry('hello'))
		c.load_entry('blue', 'sky')
		self.assertTrue(c.has_entry('blue'))
		self.assertFalse(c.has_entry('yellow'))
		self.assertFalse(c.has_entry('hello'))
		c.load_entry('brown', 'bear')
		self.assertTrue(c.has_entry('brown'))
		self.assertFalse(c.has_entry('blue'))
		self.assertFalse(c.has_entry('yellow'))
		self.assertFalse(c.has_entry('hello'))

	def testEvictionWithoutLookup(self):
		c = LRUCache(3)
		c.load_entry('hello', 'world')
		c.load_entry('yellow', 'duck')
		c.load_entry('blue', 'sky')
		c.load_entry('brown', 'bear')

		self.assertFalse(c.has_entry('hello'))
		self.assertTrue(c.has_entry('yellow'))
		self.assertTrue(c.has_entry('blue'))
		self.assertTrue(c.has_entry('brown'))

	def testEvictionWithLookup(self):
		c = LRUCache(3)
		c.load_entry('hello', 'world')
		c.load_entry('yellow', 'duck')
		c.load_entry('blue', 'sky')
		c.get_entry('hello')
		c.load_entry('brown', 'bear')

		self.assertTrue(c.has_entry('hello'))
		self.assertFalse(c.has_entry('yellow'))
		self.assertTrue(c.has_entry('blue'))
		self.assertTrue(c.has_entry('brown'))


if __name__ == '__main__':
	unittest.main()
