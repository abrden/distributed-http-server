from threading import Lock

from .LRUCache import LRUCache


class ThreadSafeLRUCache:
    def __init__(self, size):
        self.cache = LRUCache(size)
        self.mutex = Lock()

    def has_entry(self, key):
        return self.cache.has_entry(key)

    def get_entry(self, key):
        with self.mutex:
            value = self.cache.get_entry(key)
        return value

    def load_entry(self, key, value):
        with self.mutex:
            self.cache.load_entry(key, value)

    def delete_entry(self, key):
        with self.mutex:
            self.cache.delete_entry(key)
