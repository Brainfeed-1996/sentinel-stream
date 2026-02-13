from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..model import Detection, Event


@dataclass(slots=True)
class SQLiteStorage:
    path: Path

    def setup(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    host TEXT NOT NULL,
                    source TEXT NOT NULL,
                    type TEXT NOT NULL,
                    data_json TEXT NOT NULL
                );
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    host TEXT NOT NULL,
                    rule_id TEXT NOT NULL,
                    rule_name TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    event_json TEXT NOT NULL
                );
                """
            )

    def write_event(self, event: Event) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "INSERT INTO events(ts, host, source, type, data_json) VALUES (?, ?, ?, ?, ?)",
                (
                    event.ts,
                    event.host,
                    event.source,
                    event.type,
                    json.dumps(event.data, ensure_ascii=False),
                ),
            )

    def write_detection(self, detection: Detection) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                (
                    "INSERT INTO detections(ts, host, rule_id, rule_name, severity, event_json) "
                    "VALUES (?, ?, ?, ?, ?, ?)"
                ),
                (
                    detection.ts,
                    detection.host,
                    detection.rule_id,
                    detection.rule_name,
                    detection.severity,
                    json.dumps(detection.event.model_dump(), ensure_ascii=False),
                ),
            )

    def get_detections(self, *, limit: int = 100) -> list[dict[str, Any]]:
        with sqlite3.connect(self.path) as conn:
            cur = conn.execute(
                (
                    "SELECT ts, host, rule_id, rule_name, severity, event_json "
                    "FROM detections ORDER BY id DESC LIMIT ?"
                ),
                (limit,),
            )
            rows = cur.fetchall()
        out: list[dict[str, Any]] = []
        for ts, host, rule_id, rule_name, severity, event_json in rows:
            out.append(
                {
                    "ts": ts,
                    "host": host,
                    "rule_id": rule_id,
                    "rule_name": rule_name,
                    "severity": severity,
                    "event": json.loads(event_json),
                }
            )
        return out
