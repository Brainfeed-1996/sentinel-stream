from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import numpy as np

from .model import Event


@dataclass(frozen=True)
class SimConfig:
    n: int = 2000
    drift_at: int = 1200
    seed: int = 1337


def synthetic_stream(cfg: SimConfig, host: str) -> Iterator[Event]:
    """Generate a synthetic telemetry stream suitable for demo/testing.

    - connections, bytes, entropy
    - drift after cfg.drift_at
    - sparse anomalies

    Produces Event(type='telemetry.metric') with numeric fields in data.
    """

    rng = np.random.default_rng(cfg.seed)
    now = datetime.now(timezone.utc)

    connections = rng.poisson(lam=10, size=cfg.n).astype(float)
    bytes_ = np.clip(rng.normal(120_000, 35_000, size=cfg.n), 1000, None)
    entropy = np.clip(rng.normal(3.6, 0.5, size=cfg.n), 0.0, 8.0)

    # drift
    if cfg.drift_at < cfg.n:
        connections[cfg.drift_at :] += rng.poisson(lam=3, size=cfg.n - cfg.drift_at)
        bytes_[cfg.drift_at :] *= rng.normal(1.15, 0.05, size=cfg.n - cfg.drift_at)
        entropy[cfg.drift_at :] += rng.normal(0.15, 0.05, size=cfg.n - cfg.drift_at)

    # sparse anomalies
    y = np.zeros(cfg.n, dtype=int)
    # only if stream is long enough
    if cfg.n > 220:
        anom_idx = rng.choice(
            np.arange(200, cfg.n),
            size=max(5, cfg.n // 200),
            replace=False,
        )
        y[anom_idx] = 1
        connections[anom_idx] += rng.integers(80, 200, size=len(anom_idx))
        bytes_[anom_idx] *= rng.uniform(2.0, 6.0, size=len(anom_idx))
        entropy[anom_idx] = np.clip(
            entropy[anom_idx] + rng.uniform(1.5, 3.0, size=len(anom_idx)), 0, 8
        )

    for i in range(cfg.n):
        ts = now + timedelta(seconds=i)
        yield Event(
            ts=ts.isoformat(),
            host=host,
            source="simulate",
            type="telemetry.metric",
            data={
                "connections": float(connections[i]),
                "bytes": float(bytes_[i]),
                "entropy": float(entropy[i]),
                "is_anom": int(y[i]),
                "t": int(i),
            },
        )
