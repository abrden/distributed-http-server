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

    def create_lock(self, path):  # PRIVATE. Do not use on its own (Doesnt release mutex)
        self.mutex.acquire()
        if self.has_lock(path):
            self.mutex.release()
            raise RuntimeError  # TODO create specific error
        self.file_locks[path] = ReadWriteLock()

    def create_and_acquire_read_lock(self, path):
        self.create_lock(path)
        self.file_locks[path].acquire_read()
        self.mutex.release()

    def create_and_acquire_write_lock(self, path):
        self.create_lock(path)
        self.file_locks[path].acquire_write()
        self.mutex.release()

    def delete_lock(self):
        # TODO
        return


class FileHandler:
    locks = FileSystemLock()

    @staticmethod
    def ensure_dir(file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def fetch_file(path):
        path = '.' + path
        if not os.path.isfile(path):  # Check if file exists
            raise IOError('File does not exist')
        if FileHandler.locks.has_lock(path):
            FileHandler.locks.aquire_read(path)
        else:
            FileHandler.locks.create_and_acquire_read_lock(path)
        file = open(path, 'r')
        content = file.read()
        file.close()
        FileHandler.locks.release_read(path)
        return content

    @staticmethod
    def create_file(path, content):
        path = '.' + path
        if os.path.isfile(path):  # Check if file exists
            raise RuntimeError('File already exists')
        FileHandler.locks.create_and_acquire_write_lock(path)  # If file does not exist, create a lock for it and the file itself
        FileHandler.ensure_dir(path)
        file = open(path, 'w+')
        file.write(content)
        file.close()
        FileHandler.locks.release_write(path)
