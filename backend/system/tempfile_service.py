import os
import shutil
from pathlib import Path
import threading



class RWLock:
    def __init__(self):
        self._read_ready = threading.Condition(threading.Lock())
        self._readers = 0

    def acquire_read(self):
        with self._read_ready:
            self._readers += 1

    def release_read(self):
        with self._read_ready:
            self._readers -= 1
            if self._readers == 0:
                self._read_ready.notify_all()

    def acquire_write(self):
        self._read_ready.acquire()
        while self._readers > 0:
            self._read_ready.wait()

    def release_write(self):
        self._read_ready.release()


class TempFileService:
    TEMP_DIR = Path(__file__).parent.parent.resolve() / "temp"
    TEMP_RWLOCK = RWLock()
    IGNORED_FILES = ["lib"]

    @staticmethod
    def clear_temp_files():
        TempFileService.TEMP_RWLOCK.acquire_write()
        print("Removing temp files")
        for filename in os.listdir(TempFileService.TEMP_DIR):
            file_path = os.path.join(TempFileService.TEMP_DIR, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path) and filename not in TempFileService.IGNORED_FILES:
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        TempFileService.TEMP_RWLOCK.release_write()