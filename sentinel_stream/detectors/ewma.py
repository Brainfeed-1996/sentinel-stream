from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EwmaConfig:
    lam: float = 0.05
    L: float = 3.0
    warmup: int = 500


def ewma_detect(values: list[float], cfg: EwmaConfig) -> dict:
    """EWMA drift detector (univariate).

    Returns:
      {
        'mu0': float,
        'sigma0': float,
        'alerts': list[int],
        'ewma': list[float]
      }

    Notes:
    - Uses a warmup window to estimate baseline mean/std.
    - Emits an alert when EWMA exceeds dynamic control limits.
    """

    if not values:
        return {"mu0": 0.0, "sigma0": 0.0, "alerts": [], "ewma": []}

    w = min(cfg.warmup, len(values))
    base = values[:w]
    mu0 = sum(base) / w
    # population std
    var0 = sum((x - mu0) ** 2 for x in base) / max(1, w)
    sigma0 = var0**0.5

    lam = cfg.lam
    L = cfg.L

    s = mu0
    ewma = []
    alerts = []

    for i, x in enumerate(values):
        s = lam * x + (1 - lam) * s
        ewma.append(s)

        t = i + 1
        # control limit std for EWMA
        sigma_z = sigma0 * ((lam / (2 - lam)) * (1 - (1 - lam) ** (2 * t))) ** 0.5
        ucl = mu0 + L * sigma_z
        lcl = mu0 - L * sigma_z
        if s > ucl or s < lcl:
            alerts.append(i)

    return {"mu0": float(mu0), "sigma0": float(sigma0), "alerts": alerts, "ewma": ewma}
