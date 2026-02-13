from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from structlog import BoundLogger

from ..model import Detection, Event
from ..rules import Rule, rule_matches
from ..storage.base import Storage


@dataclass
class RunResult:
    events: int
    detections: int


def run_pipeline(
    *,
    host: str,
    events: Iterable[Event],
    rules: Sequence[Rule],
    storage: Storage,
    log: BoundLogger,
) -> RunResult:
    """Run the end-to-end rule evaluation pipeline.

    Collector -> pipeline -> storage.
    """

    ev_count = 0
    det_count = 0

    for ev in events:
        ev_count += 1
        storage.write_event(ev)

        evd = ev.model_dump()
        for r in rules:
            if rule_matches(r, evd):
                det = Detection(
                    ts=ev.ts,
                    host=host,
                    rule_id=r.id,
                    rule_name=r.name,
                    severity=r.severity,
                    event=ev,
                )
                storage.write_detection(det)
                det_count += 1
                log.info(
                    "detection",
                    rule_id=r.id,
                    rule_name=r.name,
                    severity=r.severity,
                    source=ev.source,
                    event_type=ev.type,
                )

    return RunResult(events=ev_count, detections=det_count)
