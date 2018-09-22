from threading import Lock


class PipeWrite:

    def __init__(self, fd):
        self.mutex = Lock()
        self.fd = fd

    def send(self, data):
        self.mutex.acquire()
        try:
            self.fd.send(data)
        except OSError:
            self.mutex.release()
            raise OSError
        self.mutex.release()

    def close(self):
        self.fd.close()


class PipeRead:

    def __init__(self, fd):
        self.mutex = Lock()
        self.fd = fd

    def receive(self):
        self.mutex.acquire()
        try:
            data = self.fd.recv()
        except OSError:
            self.mutex.release()
            return
        self.mutex.release()
        return data

    def close(self):
        self.fd.close()
