import os
import pyhash

from concurrency.ReadWriteLock import ReadWriteLock


class FileSystemLock:

    def __init__(self, locks_pool_size):
        self.hasher = pyhash.super_fast_hash()
        self.file_locks_len = locks_pool_size
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
    def __init__(self, locks_pool_size):
        self.locks = FileSystemLock(locks_pool_size)

    def _ensure_dir(self, file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

    def fetch_file(self, path):
        path = '.' + path

        if not os.path.isfile(path):
            raise IOError('File does not exist')

        self.locks.acquire_read(path)
        file = open(path, 'r')
        content = file.read()
        file.close()
        self.locks.release_read(path)
        return content

    def create_file(self, path, content):
        path = '.' + path
        if os.path.isfile(path):
            raise RuntimeError('File already exists')
        self.locks.acquire_write(path)
        self._ensure_dir(path)
        file = open(path, 'w+')
        file.write(content)
        file.close()
        self.locks.release_write(path)

    def update_file(self, path, content):
        path = '.' + path
        if not os.path.isfile(path):
            raise IOError('File does not exist')
        self.locks.acquire_write(path)
        file = open(path, 'w+')
        file.write(content)
        file.close()
        self.locks.release_write(path)

    def delete_file(self, path):
        path = '.' + path
        if not os.path.isfile(path):
            raise IOError('File does not exist')
        self.locks.acquire_write(path)
        os.remove(path)
        self.locks.release_write(path)
