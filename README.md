# Sentinel Stream

**Sentinel Stream** is a local-first, policy-driven telemetry pipeline (collection → normalization → rules → audit log) designed for defensive security and observability.

It is built to be:
- **Offline-first**: works on a laptop with no external dependencies.
- **Extensible**: collectors and rules are plugins.
- **Auditable**: every detection is written to an append-only log.

## What you get (v1)
- Pluggable collectors (filesystem + process snapshot)
- Normalized event schema
- Rule engine (YAML rules)
- Append-only JSONL audit log + integrity chain (hash linking)
- CLI to run, validate rules, and query the audit log

## Quickstart
```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# Linux/macOS
# source .venv/bin/activate

pip install -r requirements.txt

# Validate bundled rules
python -m sentinel_stream rules validate rules\default.yml

# Run once (collect + detect)
python -m sentinel_stream run --once --rules rules\default.yml --out data\audit.jsonl

# Query last 20 detections
python -m sentinel_stream audit tail --file data\audit.jsonl --n 20
```

## Event model (simplified)
Each event is a JSON object:
- `ts` (RFC3339)
- `host`
- `source` (collector name)
- `type` (event type)
- `data` (event payload)

Detections are written as audit records that include:
- matched rule id/name
- event snapshot
- integrity fields (`prev_hash`, `hash`)

## Roadmap
- Network socket collector
- Windows ETW collector (optional)
- Live mode with periodic collection
- Rule packs (baseline hardening, dev workstation, server)

## License
MIT
