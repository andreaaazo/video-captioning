import shutil
import tempfile
from typing import Optional


class TempFileManager:
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or tempfile.gettempdir()
        self.temp_dirs = []

    def create_temp_dir(self, prefix: str = "tmp") -> str:
        temp_dir = tempfile.mkdtemp(prefix=prefix, dir=self.base_dir)
        self.temp_dirs.append(temp_dir)
        return temp_dir

    def clean_up(self):
        for temp_dir in self.temp_dirs:
            shutil.rmtree(temp_dir, ignore_errors=True)
        self.temp_dirs = []

    def __del__(self):
        self.clean_up()
