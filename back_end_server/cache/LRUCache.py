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

    def has_entry(self, key):
        return key in self.dict

    def get_entry(self, key):
        e = self.dict[key]
        self.list.move_to_front(e)
        return self.dict[key].value

    def load_entry(self, key, value):
        if self.has_entry(key):
            e = self.dict[key]
            e.value = value
            self.list.move_to_front(e)
        elif self.size > 0:
            if len(self.dict) == self.size:
                del self.dict[self.list.get_last().key]
                self.list.remove_last()
            e = LRUCacheEntry(key, value)
            self.dict[key] = e
            self.list.add_to_front(e)

    def delete_entry(self, key):
        if self.has_entry(key):
            e = self.dict[key]
            del self.dict[key]
            self.list.remove(e)

    def print_LRU(self):
        self.list.print()
