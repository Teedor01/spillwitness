from __future__ import annotations

from models.evidence import Claim
from reconciliation.normalize import normalize_claim


def claims_agree(a: Claim, b: Claim) -> bool:
    """Two claims on the same field agree if they normalize to the same
    value. A claim that fails to normalize to anything concrete (None)
    never counts as agreeing with anything, including another None."""
    if a.field != b.field:
        return False
    na, nb = normalize_claim(a.field, a.raw_value), normalize_claim(b.field, b.raw_value)
    if na is None or nb is None:
        return False
    return na == nb


def claims_conflict(a: Claim, b: Claim) -> bool:
    """Two claims conflict if they're on the same field, both carry a
    concrete normalized value, those values differ, and they come from
    different sources. A single source contradicting itself over time is
    a correction, not a conflict, so same-source claims never conflict
    here."""
    if a.field != b.field or a.source_id == b.source_id:
        return False
    na, nb = normalize_claim(a.field, a.raw_value), normalize_claim(b.field, b.raw_value)
    if na is None or nb is None:
        return False
    return na != nb


def calculate_source_overlap(claims: list[Claim]) -> dict[str, set[str]]:
    """Group a list of same-field claims by normalized value, returning
    the set of distinct source_ids backing each value. Claims that don't
    normalize to a concrete value are grouped under None and excluded
    from corroboration counts (they're evidence of activity, not of a
    specific value)."""
    groups: dict[str, set[str]] = {}
    for c in claims:
        key = normalize_claim(c.field, c.raw_value)
        if key is None:
            continue
        groups.setdefault(key, set()).add(c.source_id)
    return groups
