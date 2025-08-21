import os
import shutil
from pathlib import Path
from threading import Lock

class TempFileService:
    TEMP_DIR = Path(__file__).parent.parent.resolve() / "temp"
    TEMP_MUTEX = Lock()
    IGNORED_FILES = ["lib"]

    @staticmethod
    def clear_temp_files():
        with TempFileService.TEMP_MUTEX:
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