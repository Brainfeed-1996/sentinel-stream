from __future__ import annotations

import asyncio
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import List

from structlog import BoundLogger

from ..model import Detection, Event
from ..rules import Rule, rule_matches
from ..storage.base import Storage
from .middleware import AsyncPipeline, PipelineMiddleware


@dataclass
class RunResult:
    events: int
    detections: int


async def run_pipeline_async(
    *,
    host: str,
    events: Iterable[Event],
    rules: Sequence[Rule],
    storage: Storage,
    log: BoundLogger,
    middlewares: List[PipelineMiddleware] = None
) -> RunResult:
    """Run the end-to-end rule evaluation pipeline asynchronously with middleware support."""

    ev_count = 0
    det_count = 0
    pipeline = AsyncPipeline(middlewares or [])

    async def final_handler(ev: Event):
        nonlocal det_count
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

    for ev in events:
        ev_count += 1
        await pipeline.execute(ev, final_handler)

    return RunResult(events=ev_count, detections=det_count)

def run_pipeline(*args, **kwargs) -> RunResult:
    """Synchronous wrapper for backward compatibility."""
    return asyncio.run(run_pipeline_async(*args, **kwargs))
