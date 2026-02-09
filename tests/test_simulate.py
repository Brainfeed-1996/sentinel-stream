from sentinel_stream.simulate import SimConfig, synthetic_stream


def test_synthetic_stream_length():
    cfg = SimConfig(n=123, drift_at=60, seed=1)
    events = list(synthetic_stream(cfg, host="h"))
    assert len(events) == 123
    assert events[0].type == "telemetry.metric"
    assert "connections" in events[0].data
