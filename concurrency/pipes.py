from threading import Lock


class PipeWrite:

    def __init__(self, fd):
        self.mutex = Lock()
        self.fd = fd

    def send(self, data):
        self.mutex.acquire()
        self.fd.send(data)
        self.mutex.release()

    def close(self):
        self.fd.close()


class PipeRead:

    def __init__(self, fd):
        self.mutex = Lock()
        self.fd = fd

    def receive(self):
        self.mutex.acquire()
        data = self.fd.recv()
        self.mutex.release()
        return data

    def close(self):
        self.fd.close()
