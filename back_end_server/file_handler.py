import os
from threading import Lock
import pyhash
import logging

from .concurrency.ReadWriteLock import ReadWriteLock


class FileSystemLock:

    def __init__(self):
        self.hasher = pyhash.super_fast_hash()
        self.file_locks_len = 30  # TODO make customizable
        self.mutex = Lock()
        self.file_locks = []
        for i in range(self.file_locks_len):
            self.file_locks.append(ReadWriteLock())

    def lock_num(self, path):
        return self.hasher(path) % self.file_locks_len

    def acquire_read(self, path):
        lock_num = self.lock_num(path)
        self.file_locks[lock_num].acquire_read()

    def acquire_write(self, path):
        lock_num = self.lock_num(path)
        self.file_locks[lock_num].acquire_write()

    def release_read(self, path):
        lock_num = self.lock_num(path)
        self.file_locks[lock_num].release_read()

    def release_write(self, path):
        lock_num = self.lock_num(path)
        self.file_locks[lock_num].release_write()


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

        if not os.path.isfile(path):
            raise IOError('File does not exist')

        FileHandler.locks.acquire_read(path)
        file = open(path, 'r')
        content = file.read()
        file.close()
        FileHandler.locks.release_read(path)
        return content

    @staticmethod
    def create_file(path, content):
        path = '.' + path
        if os.path.isfile(path):
            raise RuntimeError('File already exists')
        FileHandler.locks.acquire_write(path)
        FileHandler.ensure_dir(path)
        file = open(path, 'w+')
        file.write(content)
        file.close()
        FileHandler.locks.release_write(path)

    @staticmethod
    def update_file(path, content):
        path = '.' + path
        if not os.path.isfile(path):
            raise IOError('File does not exist')
        FileHandler.locks.acquire_write(path)
        file = open(path, 'w+')
        file.write(content)
        file.close()
        FileHandler.locks.release_write(path)
