from threading import Lock

from .LRUCache import LRUCache


class ThreadSafeLRUCache(LRUCache):
    def __init__(self, size):
        super(ThreadSafeLRUCache, self).__init__(size)
        self.mutex = Lock()

    def get_entry(self, key):
        self.mutex.acquire()
        value = super(ThreadSafeLRUCache, self).get_entry(key)
        self.mutex.release()
        return value

    def load_entry(self, key, value):
        self.mutex.acquire()
        super(ThreadSafeLRUCache, self).load_entry(key, value)
        self.mutex.release()

    def delete_entry(self, key):
        self.mutex.acquire()
        super(ThreadSafeLRUCache, self).delete_entry(key)
        self.mutex.release()
