from pathlib import Path

from sentinel_stream.audit import append_detection, verify_chain
from sentinel_stream.model import Detection, Event


def test_audit_chain_roundtrip(tmp_path: Path):
    out = tmp_path / "audit.jsonl"

    ev = Event(ts="2026-01-01T00:00:00Z", host="h", source="s", type="t", data={"k": "v"})
    det = Detection(
        ts=ev.ts,
        host=ev.host,
        rule_id="r1",
        rule_name="rule",
        severity="low",
        event=ev,
    )

    prev = None
    prev = append_detection(out, det, prev)
    prev = append_detection(out, det, prev)

    assert out.exists()
    assert verify_chain(out) is True

    # tamper should fail
    lines = out.read_text(encoding="utf-8").splitlines()
    lines[0] = lines[0].replace("low", "critical")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert verify_chain(out) is False
