from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from ..model import Event


def scan_user_home(host: str, max_files: int = 2000) -> Iterable[Event]:
    home = Path.home()
    seen = 0
    for root, dirs, files in os.walk(home):
        # skip huge/noisy dirs
        parts = set(Path(root).parts)
        if any(p in parts for p in {".git", "node_modules", ".venv", "AppData", "Library"}):
            continue

        for fn in files:
            p = Path(root) / fn
            seen += 1
            yield Event(host=host, source="fs_scan", type="fs.scan", data={"path": str(p)})
            if seen >= max_files:
                return
