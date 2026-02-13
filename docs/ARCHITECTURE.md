# Architecture

Sentinel Stream uses a simple, production-shaped architecture:

**collector → pipeline → storage → api**

## Collector
Collectors produce normalized `Event` objects.

Current built-ins:
- `fs_scan`: lightweight filesystem path enumeration (home directory)
- `proc_snapshot`: process listing snapshot

Collectors are intentionally local-first and do not perform network exfiltration.

## Pipeline
The pipeline:
1. persists raw events
2. evaluates YAML rules against the event payload
3. writes any matches as `Detection` records

## Storage
Storage is split into two complementary backends:

- **SQLite**: query-friendly history for events/detections
- **Audit JSONL**: append-only tamper evidence for detections

### Audit log integrity
Each detection record includes:
- `prev_hash`: hash of previous record
- `hash`: hash of the current record payload

This creates a hash chain suitable for lightweight tamper-evidence.

## API
The (optional) HTTP API reads from SQLite and exposes detection queries.

It is kept intentionally small and read-only by default.
