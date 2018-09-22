class DoublyLinkedList:

    def __init__(self):
        self.first = None
        self.last = None

    def add_to_front(self, e):
        e.right = self.first
        e.left = None

        if self.first is not None:
            self.first.left = e
        self.first = e

        if self.last is None:
            self.last = self.first

    def move_to_front(self, e):
        if e == self.first:
            return
        self.remove(e)
        self.add_to_front(e)

    def remove(self, e):
        if e.right is not None:
            e.right.left = e.left
        else:  # The last is removed
            self.last = self.last.left
        if e.left is not None:
            e.left.right = e.right
        else:  # The first is removed
            self.first = self.first.right

    def get_first(self):
        return self.first

    def get_last(self):
        return self.last

    def remove_last(self):
        self.remove(self.last)

    def print(self):
        print('From left to right')
        c = self.first
        while c is not None:
            print(c.key)
            c = c.right
        print('From right to left')
        c = self.last
        while c is not None:
            print(c.key)
            c = c.left
