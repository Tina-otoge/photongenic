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
        self.thumb_path = path.with_suffix(".png")
        if self.thumb_path.exists():
            self.thumb = self.thumb_path
            self.thumb_relative = self.thumb_path.relative_to(File.DIR)
        else:
            self.thumb = None
            self.thumb_relative = None

    def generate_thumbnail(self):
        if self.thumb_path.exists():
            return
        with self.thumb_path.open("w") as f:
            f.write("")
        subprocess.run(
            "ffmpeg -sseof -60".split()
            + ["-i", str(self.path)]
            + "-vf thumbnail -y -update true".split()
            + [str(self.thumb_path)]
        )


def get_files():
    files = []
    for p in File.DIR.rglob("*"):
        if p.is_file() and p.suffix in VALID_EXTENSIONS:
            file = File(p)
            files.append(file)
    return sorted(files, key=lambda f: f.date, reverse=True)


def generate_thumbnails():
    while True:
        files = get_files()
        for file in files:
            file.generate_thumbnail()
        time.sleep(1)


if __name__ == "__main__":
    generate_thumbnails()
