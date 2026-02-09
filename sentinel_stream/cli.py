from __future__ import annotations

import argparse
import socket
from pathlib import Path

from rich.console import Console

from .audit import iter_records, verify_chain
from .collectors import process_snapshot, scan_user_home
from .detectors.ewma import EwmaConfig, ewma_detect
from .pipeline import run_pipeline
from .rules import load_rules, validate_rules
from .simulate import SimConfig, synthetic_stream


def cmd_rules_validate(args) -> int:
    errs = validate_rules(args.file)
    if errs:
        for e in errs:
            print(e)
        return 2
    print("OK")
    return 0


def cmd_run(args) -> int:
    host = args.host or socket.gethostname()
    rules = load_rules(args.rules)
    out = Path(args.out)

    def event_stream():
        # collectors (v1): FS + process snapshot
        yield from scan_user_home(host=host, max_files=args.max_files)
        yield from process_snapshot(host=host)

    res = run_pipeline(host=host, events=event_stream(), rules=rules, out_file=out)
    print(f"events={res.events} detections={res.detections} audit_ok={res.audit_ok}")
    return 0 if res.audit_ok else 3


def cmd_audit_tail(args) -> int:
    c = Console()
    file = Path(args.file)
    rows = list(iter_records(file))[-args.n :]
    for r in rows:
        c.print(r)
    return 0


def cmd_audit_verify(args) -> int:
    ok = verify_chain(Path(args.file))
    print("OK" if ok else "FAIL")
    return 0 if ok else 4


def cmd_simulate_run(args) -> int:
    host = args.host or socket.gethostname()
    rules = load_rules(args.rules)
    out = Path(args.out)

    cfg = SimConfig(n=args.n, drift_at=args.drift_at, seed=args.seed)
    events = synthetic_stream(cfg, host=host)
    res = run_pipeline(host=host, events=events, rules=rules, out_file=out)
    print(f"events={res.events} detections={res.detections} audit_ok={res.audit_ok}")
    return 0 if res.audit_ok else 3


def cmd_drift_ewma(args) -> int:
    # Read a newline-separated list of numbers (one per line)
    vals = []
    p = Path(args.input)
    for line in p.read_text(encoding='utf-8', errors='ignore').splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            vals.append(float(line))
        except ValueError:
            continue

    cfg = EwmaConfig(lam=args.lam, L=args.L, warmup=args.warmup)
    out = ewma_detect(vals, cfg)
    first = out['alerts'][0] if out['alerts'] else None
    print(f"alerts={len(out['alerts'])} first_alert={first} mu0={out['mu0']:.4f} sigma0={out['sigma0']:.4f}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="sentinel-stream")
    sub = p.add_subparsers(dest="cmd", required=True)

    rules = sub.add_parser("rules")
    rules_sub = rules.add_subparsers(dest="rules_cmd", required=True)
    rv = rules_sub.add_parser("validate")
    rv.add_argument("file")
    rv.set_defaults(fn=cmd_rules_validate)

    run = sub.add_parser("run")
    run.add_argument("--rules", required=True)
    run.add_argument("--out", required=True)
    run.add_argument("--host", default=None)
    run.add_argument("--once", action="store_true")
    run.add_argument("--max-files", type=int, default=2000)
    run.set_defaults(fn=cmd_run)

    audit = sub.add_parser("audit")
    audit_sub = audit.add_subparsers(dest="audit_cmd", required=True)
    at = audit_sub.add_parser("tail")
    at.add_argument("--file", required=True)
    at.add_argument("--n", type=int, default=20)
    at.set_defaults(fn=cmd_audit_tail)

    av = audit_sub.add_parser("verify")
    av.add_argument("--file", required=True)
    av.set_defaults(fn=cmd_audit_verify)

    sim = sub.add_parser("simulate")
    sim.add_argument("--rules", required=True)
    sim.add_argument("--out", required=True)
    sim.add_argument("--host", default=None)
    sim.add_argument("--n", type=int, default=2000)
    sim.add_argument("--drift-at", type=int, default=1200)
    sim.add_argument("--seed", type=int, default=1337)
    sim.set_defaults(fn=cmd_simulate_run)

    drift = sub.add_parser("drift")
    drift_sub = drift.add_subparsers(dest="drift_cmd", required=True)
    ew = drift_sub.add_parser("ewma")
    ew.add_argument("--input", required=True, help="Text file with one numeric value per line")
    ew.add_argument("--lam", type=float, default=0.05)
    ew.add_argument("--L", type=float, default=3.0)
    ew.add_argument("--warmup", type=int, default=500)
    ew.set_defaults(fn=cmd_drift_ewma)

    return p


def main() -> int:
    p = build_parser()
    args = p.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
