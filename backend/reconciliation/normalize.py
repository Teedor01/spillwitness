from __future__ import annotations

import re
from datetime import date, datetime
from typing import Optional

from models.evidence import ClaimField


_LOCATION_ALIASES = {
    "santa barbra river": "santa barbara river, nembe, bayelsa state",
    "santa barbara river": "santa barbara river, nembe, bayelsa state",
    "santa barbara well 1": "santa barbara well 1, nembe, bayelsa state",
    "santa barbara well-head 1": "santa barbara well 1, nembe, bayelsa state",
    "santa barbara south well 1": "santa barbara well 1, nembe, bayelsa state",
    "nembe creek": "nembe creek, bayelsa state",
}


_KNOWN_COMMUNITIES = (
    "nembe, bayelsa state",
    "eleme, rivers state",
)


def normalize_location(raw: str) -> str:
    """Return a normalized key used to group location claims together."""
    key = re.sub(r"[^a-z0-9\s]", "", raw.lower()).strip()
    key = re.sub(r"\s+", " ", key)
    if key in _LOCATION_ALIASES:
        return _LOCATION_ALIASES[key]
    for community in _KNOWN_COMMUNITIES:
        lga, state = (part.strip() for part in community.split(","))
        if lga in key and state.split()[0] in key:
            return community
    return key



_DATE_FORMATS = (
    "%Y-%m-%d",
    "%B %d, %Y",
    "%b %d, %Y",
    "%d %B %Y",
    "%d %b %Y",
    "%m/%d/%Y",
)


def normalize_date(raw: str) -> Optional[date]:
    """Parse a handful of common date shapes. Returns None rather than
    guessing when the format isn't recognized: an unparsed date must
    surface as missing evidence, not a silently wrong one."""
    cleaned = raw.strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    return None



_CAUSE_KEYWORDS = {
    "SABOTAGE": (
        "sabotage",
        "third-party interference",
        "third party interference",
        "external interference",
        "vandalism",
        "illegal attachment",
    ),
    "EQUIPMENT_FAILURE": (
        "equipment failure",
        "equipment and maintenance failure",
        "maintenance failure",
        "mechanical failure",
        "operational failure",
    ),
}


def normalize_cause(raw: str) -> str:
    """Map free text to a small controlled vocabulary. Anything that
    doesn't match a known phrase stays as its own distinct bucket rather
    than being forced into SABOTAGE/EQUIPMENT_FAILURE... an unmapped cause
    claim should show up as unresolved, not silently miscategorized."""
    lowered = raw.lower()
    for canonical, phrases in _CAUSE_KEYWORDS.items():
        if any(phrase in lowered for phrase in phrases):
            return canonical
    return f"UNMAPPED:{lowered.strip()}"



_NUMBER_RE = re.compile(r"([\d,]+(?:\.\d+)?)\s*(million\s+)?barrels?", re.IGNORECASE)

_WORD_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}
_WORD_NUMBER_RE = re.compile(
    r"\b(" + "|".join(_WORD_NUMBERS) + r")\s+million\s+barrels?\b", re.IGNORECASE
)


def normalize_volume(raw: str) -> Optional[float]:
    """Extract a barrel figure as a float. Returns None if no number is
    present (e.g. a claim that only disputes another claim's number
    without offering its own)."""
    match = _NUMBER_RE.search(raw)
    if match:
        number = float(match.group(1).replace(",", ""))
        if match.group(2):
            number *= 1_000_000
        return number
    word_match = _WORD_NUMBER_RE.search(raw)
    if word_match:
        return float(_WORD_NUMBERS[word_match.group(1).lower()]) * 1_000_000
    return None


def normalize_claim(claim_field: ClaimField, raw_value: str) -> Optional[str]:
    """Single entry point used by the reconciliation engine. Returns a
    normalized key suitable for grouping, or None if raw_value carries no
    concrete comparable value for this field (e.g. a claim that only says
    "disputed" with no figure of its own)."""
    if claim_field == ClaimField.LOCATION:
        return normalize_location(raw_value)
    if claim_field == ClaimField.DATE:
        parsed = normalize_date(raw_value)
        return parsed.isoformat() if parsed else None
    if claim_field == ClaimField.CAUSE:
        return normalize_cause(raw_value)
    if claim_field == ClaimField.VOLUME:
        value = normalize_volume(raw_value)
        if value is None:
            return None
        return f"{value:.0e}"
    if claim_field == ClaimField.OCCURRENCE:
        return "OCCURRED"
    return raw_value.strip().lower()
