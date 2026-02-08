from __future__ import annotations

import platform
import subprocess
from collections.abc import Iterable

from ..model import Event


def _win_process_chain() -> list[str]:
    # best-effort: use wmic when available (older), fallback to tasklist (no parent info)
    chains = []
    try:
        cmd = [
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-CimInstance Win32_Process | Select-Object "
            "Name,ProcessId,ParentProcessId | ConvertTo-Json",
        ]
        subprocess.check_output(cmd, text=True, encoding="utf-8", errors="replace")
        # We keep it simple: only emit raw snapshot; rules can match chain string if enriched later.
        chains.append("win32_process_snapshot")
        return chains
    except Exception:
        return ["win32_process_snapshot_unavailable"]


def process_snapshot(host: str) -> Iterable[Event]:
    if platform.system().lower().startswith("win"):
        chain = " -> ".join(_win_process_chain())
        yield Event(host=host, source="proc_snapshot", type="proc.snapshot", data={"chain": chain})
        return

    # POSIX: ps
    try:
        out = subprocess.check_output(
            ["ps", "-eo", "ppid=,pid=,comm="],
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        sample = "\n".join(out.splitlines()[:200])
        yield Event(host=host, source="proc_snapshot", type="proc.snapshot", data={"chain": sample})
    except Exception:
        yield Event(
            host=host,
            source="proc_snapshot",
            type="proc.snapshot",
            data={"chain": "ps_unavailable"},
        )
