from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class Rule:
    id: str
    name: str
    severity: str
    event_type: str
    where: Dict[str, Any]


def load_rules(path: str) -> List[Rule]:
    doc = yaml.safe_load(open(path, "r", encoding="utf-8"))
    rules = []
    for r in doc.get("rules", []):
        m = r.get("match", {})
        rules.append(
            Rule(
                id=r["id"],
                name=r.get("name", r["id"]),
                severity=r.get("severity", "medium"),
                event_type=m.get("type", ""),
                where=m.get("where", {}),
            )
        )
    return rules


def _get_field(obj: Dict[str, Any], dotted: str) -> Optional[str]:
    parts = dotted.split(".")
    cur: Any = obj
    for p in parts:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return None
    return None if cur is None else str(cur)


def _match_clause(event: Dict[str, Any], clause: Dict[str, Any]) -> bool:
    field = clause.get("field")
    if not field:
        return False
    value = _get_field(event, field)
    if value is None:
        return False

    if "contains" in clause:
        return str(clause["contains"]) in value
    if "regex" in clause:
        return re.search(clause["regex"], value) is not None
    if "equals" in clause:
        return value == str(clause["equals"])
    return False


def rule_matches(rule: Rule, event: Dict[str, Any]) -> bool:
    if rule.event_type and event.get("type") != rule.event_type:
        return False

    where = rule.where or {}
    any_of = where.get("any_of")
    all_of = where.get("all_of")

    if any_of:
        return any(_match_clause(event, c) for c in any_of)
    if all_of:
        return all(_match_clause(event, c) for c in all_of)

    return False


def validate_rules(path: str) -> List[str]:
    errs: List[str] = []
    try:
        rules = load_rules(path)
    except Exception as e:
        return [f"failed to parse rules: {e}"]

    ids = set()
    for r in rules:
        if not r.id:
            errs.append("rule missing id")
        if r.id in ids:
            errs.append(f"duplicate rule id: {r.id}")
        ids.add(r.id)
        if r.severity not in {"low", "medium", "high", "critical"}:
            errs.append(f"invalid severity: {r.id} -> {r.severity}")
        if not r.event_type:
            errs.append(f"missing event type: {r.id}")
    return errs
