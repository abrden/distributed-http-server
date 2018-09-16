import os
from threading import Lock

from .concurrency.ReadWriteLock import ReadWriteLock


class FileSystemLock:

    def __init__(self):
        self.mutex = Lock()
        self.file_locks = {}

    def aquire_read(self, path):
        self.file_locks[path].acquire_read()

    def aquire_write(self, path):
        self.file_locks[path].acquire_write()

    def release_read(self, path):
        self.file_locks[path].release_read()

    def release_write(self, path):
        self.file_locks[path].release_write()

    def has_lock(self, path):
        return path in self.file_locks

    def create_and_acquire_write_lock(self, path):
        self.mutex.acquire()
        if self.has_lock(path):
            self.mutex.release()
            raise RuntimeError  # TODO create specific error
        lock = ReadWriteLock()
        lock.acquire_write()
        self.file_locks[path] = lock
        self.mutex.release()

    def delete_lock(self):
        # TODO
        return


class FileHandler:
    locks = FileSystemLock()

    def ensure_dir(self, file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

    def fetch_file(self, path):
        path = '.' + path
        FileHandler.locks.aquire_read(path)
        file = open(path, 'r')
        content = file.read()
        file.close()
        FileHandler.locks.release_read(path)
        return content

    def create_file(self, path, content):
        path = './' + path
        FileHandler.locks.create_and_acquire_write_lock(path)
        self.ensure_dir(path)
        file = open(path, 'w+')
        file.write(content)
        file.close()
        FileHandler.locks.release_write(path)