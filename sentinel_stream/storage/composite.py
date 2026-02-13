from __future__ import annotations

from dataclasses import dataclass

from ..model import Detection, Event
from .base import Storage


@dataclass(slots=True)
class CompositeStorage:
    """Write to multiple storages (best-effort fan-out)."""

    storages: tuple[Storage, ...]

    def setup(self) -> None:
        for s in self.storages:
            s.setup()

    def write_event(self, event: Event) -> None:
        for s in self.storages:
            s.write_event(event)

    def write_detection(self, detection: Detection) -> None:
        for s in self.storages:
            s.write_detection(detection)
