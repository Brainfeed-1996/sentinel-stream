from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


class Event(BaseModel):
    ts: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    host: str
    source: str
    type: str
    data: dict[str, Any] = Field(default_factory=dict)


class Detection(BaseModel):
    ts: str
    host: str
    rule_id: str
    rule_name: str
    severity: Literal["low", "medium", "high", "critical"]
    event: Event


class AuditRecord(BaseModel):
    kind: Literal["detection"]
    detection: Detection
    prev_hash: str | None = None
    hash: str
