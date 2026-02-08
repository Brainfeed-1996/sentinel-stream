from sentinel_stream.rules import load_rules, validate_rules


def test_default_rules_validate():
    errs = validate_rules("rules/default.yml")
    assert errs == []


def test_load_rules():
    rules = load_rules("rules/default.yml")
    assert len(rules) >= 1
    assert rules[0].id
