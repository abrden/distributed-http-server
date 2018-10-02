from threading import Lock

from .LRUCache import LRUCache


class ThreadSafeLRUCache:
    def __init__(self, size):
        self.cache = LRUCache(size)
        self.mutex = Lock()

    def has_entry(self, key):
        return self.cache.has_entry(key)

    def get_entry(self, key):
        self.mutex.acquire()
        value = self.cache.get_entry(key)
        self.mutex.release()
        return value

    def load_entry(self, key, value):
        self.mutex.acquire()
        self.cache.load_entry(key, value)
        self.mutex.release()

    def delete_entry(self, key):
        self.mutex.acquire()
        self.cache.delete_entry(key)
        self.mutex.release()
