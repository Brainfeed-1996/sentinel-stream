from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable, Optional

from .model import AuditRecord, Detection


def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def append_detection(out_file: Path, detection: Detection, prev_hash: Optional[str]) -> str:
    payload = {
        "kind": "detection",
        "detection": detection.model_dump(),
        "prev_hash": prev_hash,
    }
    line = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    h = _sha256_hex(line)
    rec = AuditRecord(kind="detection", detection=detection, prev_hash=prev_hash, hash=h)

    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec.model_dump(), ensure_ascii=False) + "\n")
    return h


def iter_records(file: Path) -> Iterable[dict]:
    if not file.exists():
        return
    with file.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def verify_chain(file: Path) -> bool:
    prev = None
    for rec in iter_records(file):
        if rec.get("kind") != "detection":
            continue
        expected_prev = rec.get("prev_hash")
        if expected_prev != prev:
            return False

        # recompute hash
        payload = {
            "kind": "detection",
            "detection": rec.get("detection"),
            "prev_hash": rec.get("prev_hash"),
        }
        line = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        h = _sha256_hex(line)
        if h != rec.get("hash"):
            return False
        prev = rec.get("hash")
    return True
