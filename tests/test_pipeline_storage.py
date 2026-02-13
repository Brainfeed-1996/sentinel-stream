from __future__ import annotations

from pathlib import Path

import pytest

from sentinel_stream.audit import iter_records, verify_chain
from sentinel_stream.logging import configure_logging, get_logger
from sentinel_stream.model import Event
from sentinel_stream.pipeline import run_pipeline
from sentinel_stream.rules import load_rules
from sentinel_stream.storage import AuditJsonlStorage, CompositeStorage, SQLiteStorage


def test_pipeline_writes_sqlite_and_audit(tmp_path: Path) -> None:
    configure_logging(level="INFO", fmt="json")
    log = get_logger("test")

    rules_file = tmp_path / "rules.yml"
    rules_file.write_text(
        """
rules:
  - id: R1
    name: secret-path
    severity: high
    match:
      type: fs.scan
      where:
        any_of:
          - field: data.path
            contains: secret
""".lstrip(),
        encoding="utf-8",
    )

    rules = load_rules(str(rules_file))

    sqlite_path = tmp_path / "db.sqlite"
    audit_path = tmp_path / "audit.jsonl"

    storage = CompositeStorage((SQLiteStorage(sqlite_path), AuditJsonlStorage(audit_path)))
    storage.setup()

    events = [
        Event(host="host1", source="fs_scan", type="fs.scan", data={"path": "C:/tmp/secret.txt"}),
        Event(host="host1", source="fs_scan", type="fs.scan", data={"path": "C:/tmp/normal.txt"}),
    ]

    res = run_pipeline(host="host1", events=events, rules=rules, storage=storage, log=log)
    assert res.events == 2
    assert res.detections == 1

    # SQLite should have the detection
    db = SQLiteStorage(sqlite_path)
    dets = db.get_detections(limit=10)
    assert len(dets) == 1
    assert dets[0]["rule_id"] == "R1"

    # Audit log should be valid and contain 1 record
    assert verify_chain(audit_path) is True
    assert len(list(iter_records(audit_path))) == 1


def test_api_optional_import() -> None:
    """API is an optional extra; tests should not require it."""

    pytest.importorskip("fastapi")

    from sentinel_stream.api.app import create_app
    from sentinel_stream.config import Settings

    app = create_app(Settings())
    assert app.title == "sentinel-stream"
