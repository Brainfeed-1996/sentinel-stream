from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..audit import append_detection, verify_chain
from ..model import Detection, Event


@dataclass(slots=True)
class AuditJsonlStorage:
    """Append-only, tamper-evident detection log (hash chain)."""

    path: Path
    _prev_hash: str | None = field(default=None, init=False, repr=False)

    def setup(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # On startup, verify chain and recover last hash (best-effort).
        if self.path.exists() and verify_chain(self.path):
            last: str | None = None
            for rec in self.path.read_text(encoding="utf-8", errors="replace").splitlines()[-200:]:
                if '"hash"' in rec:
                    last = rec
            if last:
                import json

                try:
                    self._prev_hash = json.loads(last).get("hash")
                except Exception:
                    self._prev_hash = None

    def write_event(self, event: Event) -> None:
        # audit log stores detections only
        return

    def write_detection(self, detection: Detection) -> None:
        self._prev_hash = append_detection(self.path, detection, self._prev_hash)
