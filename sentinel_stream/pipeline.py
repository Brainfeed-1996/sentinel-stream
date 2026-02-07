from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

from .audit import append_detection, verify_chain
from .model import Detection, Event
from .rules import Rule, rule_matches


@dataclass
class RunResult:
    events: int
    detections: int
    audit_ok: bool


def run_pipeline(host: str, events: Iterable[Event], rules: List[Rule], out_file: Path) -> RunResult:
    prev_hash: Optional[str] = None
    # find last hash if file exists
    if out_file.exists():
        # verify and also recover last hash
        if verify_chain(out_file):
            # read tail
            last = None
            for rec in out_file.read_text(encoding="utf-8", errors="replace").splitlines()[-200:]:
                if '"hash"' in rec:
                    last = rec
            if last:
                import json

                try:
                    prev_hash = json.loads(last).get("hash")
                except Exception:
                    prev_hash = None

    ev_count = 0
    det_count = 0
    for ev in events:
        ev_count += 1
        evd = ev.model_dump()
        for r in rules:
            if rule_matches(r, evd):
                det = Detection(
                    ts=ev.ts,
                    host=ev.host,
                    rule_id=r.id,
                    rule_name=r.name,
                    severity=r.severity,
                    event=ev,
                )
                prev_hash = append_detection(out_file, det, prev_hash)
                det_count += 1

    return RunResult(events=ev_count, detections=det_count, audit_ok=verify_chain(out_file))
