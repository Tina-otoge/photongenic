import subprocess
import time
from datetime import datetime
from pathlib import Path

import photon

VALID_EXTENSIONS = [".mp4", ".mkv", ".webm", ".mov", ".avi"]


class File:
    DIR = Path(photon.config.output_local)

    def __init__(self, path: Path):
        self.path = path
        self.relative = path.relative_to(File.DIR)
        # self.date = path.stat().st_mtime
        self.date = datetime.fromtimestamp(path.stat().st_mtime)
        self.group = path.parent.name
        self.thumb_path = path.with_suffix(".jpg")
        self.thumb_lock_path = path.with_suffix(".thumb.lock")
        if self.thumb_path.exists():
            self.thumb = self.thumb_path
            self.thumb_relative = self.thumb_path.relative_to(File.DIR)
        else:
            self.thumb = None
            self.thumb_relative = None

    def generate_thumbnail(self):
        if self.thumb_path.exists() or self.thumb_lock_path.exists():
            return
        self.thumb_lock_path.touch()
        print(f"Generating thumbnail {self.thumb_path}")
        subprocess.run(
            "ffmpeg -sseof -60".split()
            + ["-i", str(self.path)]
            + "-vframes 1 -y -update true".split()
            + [str(self.thumb_path)]
        )
        self.thumb_lock_path.unlink()


def get_files(group=None):
    files = []
    # print(f"Searching for files in {File.DIR}")
    # print(File.DIR.resolve())
    for p in File.DIR.rglob("*"):
        # print(p)
        if p.is_file() and p.suffix in VALID_EXTENSIONS:
            file = File(p)
            if group is not None and file.group != group:
                continue
            files.append(file)
    return sorted(files, key=lambda f: f.date, reverse=True)


def generate_thumbnails():
    WAIT_TIME = 1
    while True:
        for file in get_files():
            file.generate_thumbnail()
        # print(f"Sleeping for {WAIT_TIME}s")
        time.sleep(WAIT_TIME)


if __name__ == "__main__":
    generate_thumbnails()
