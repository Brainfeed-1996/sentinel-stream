from __future__ import annotations

from typing import Protocol

from ..model import Detection, Event


class Storage(Protocol):
    def setup(self) -> None:
        """Initialize storage resources (tables, directories, etc.)."""

    def write_event(self, event: Event) -> None:
        """Persist a raw event."""

    def write_detection(self, detection: Detection) -> None:
        """Persist a detection."""
