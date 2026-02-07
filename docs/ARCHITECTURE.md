# Architecture

## Pipeline
1) Collectors produce `Event`s
2) Normalizer keeps a consistent schema (`Event` model)
3) Rule engine matches YAML rules against events
4) Detections are appended to an audit log (JSONL)

## Audit log integrity
Each detection record includes:
- `prev_hash`: hash of previous record
- `hash`: hash of the current record payload

This creates an append-only hash chain suitable for lightweight tamper evidence.
