import subprocess
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
        self.thumb = self.path.with_suffix(".png")
        self.thumb_relative = self.thumb.relative_to(File.DIR)
        self.ensure_thumbnail()

    def ensure_thumbnail(self):
        if self.thumb and self.thumb.exists():
            return
        subprocess.run(
            "ffmpeg -sseof -60".split()
            + ["-i", str(self.path)]
            + "-vf thumbnail -y -frames:v 1".split()
            + [str(self.thumb)]
        )
        if not self.thumb.exists():
            self.thumb = None


def get_files():
    files = []
    for p in File.DIR.rglob("*"):
        if p.is_file() and p.suffix in VALID_EXTENSIONS:
            file = File(p)
            files.append(file)
    return sorted(files, key=lambda f: f.date, reverse=True)
