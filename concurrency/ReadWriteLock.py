from threading import Condition, Lock


class ReadWriteLock:

    def __init__(self):
        self.read_ready = Condition(Lock())
        self.readers = 0

    def acquire_read(self):
        self.read_ready.acquire()
        try:
            self.readers += 1
        finally:
            self.read_ready.release()

    def release_read(self):
        self.read_ready.acquire()
        try:
            self.readers -= 1
            if not self.readers:
                self.read_ready.notifyAll()
        finally:
            self.read_ready.release()

    def acquire_write(self):
        self.read_ready.acquire()
        while self.readers > 0:
            self.read_ready.wait()

    def release_write(self):
        self.read_ready.release()
