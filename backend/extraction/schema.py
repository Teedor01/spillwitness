from __future__ import annotations

from dataclasses import dataclass

from models.evidence import ClaimField, SourceType
from reconciliation.normalize import normalize_date

REQUIRED_KEYS = {"field", "raw_value", "source_name", "source_type", "excerpt"}
OPTIONAL_KEYS = {"source_url", "event_date", "publication_date"}
ALLOWED_KEYS = REQUIRED_KEYS | OPTIONAL_KEYS


FORBIDDEN_KEYS = {
    "status", "field_status", "confidence", "corroborated", "contested",
    "conflicting", "reconciliation", "independent", "verified",
    "reliability", "reason", "score",
}


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str]
    claim_data: dict | None  


def validate_extracted_item(item: dict) -> ValidationResult:
    errors: list[str] = []

    if not isinstance(item, dict):
        return ValidationResult(ok=False, errors=["item is not a JSON object"], claim_data=None)

    present_keys = set(item.keys())
    forbidden_present = present_keys & FORBIDDEN_KEYS
    if forbidden_present:
        errors.append(
            f"forbidden key(s) present: {sorted(forbidden_present)} - extraction must never "
            "propose a status, confidence, or reconciliation judgment"
        )

    missing = REQUIRED_KEYS - present_keys
    if missing:
        errors.append(f"missing required key(s): {sorted(missing)}")

    unknown = present_keys - ALLOWED_KEYS - FORBIDDEN_KEYS
    if unknown:
        errors.append(f"unrecognized key(s): {sorted(unknown)}")

    if errors:
        return ValidationResult(ok=False, errors=errors, claim_data=None)

    field = item.get("field")
    if field not in {f.value for f in ClaimField}:
        errors.append(f"'field' {field!r} is not one of {[f.value for f in ClaimField]}")

    source_type = item.get("source_type")
    if source_type not in {t.value for t in SourceType}:
        errors.append(f"'source_type' {source_type!r} is not one of {[t.value for t in SourceType]}")

    raw_value = item.get("raw_value")
    if not isinstance(raw_value, str) or not raw_value.strip():
        errors.append("'raw_value' must be a non-empty string")

    excerpt = item.get("excerpt")
    if not isinstance(excerpt, str) or not excerpt.strip():
        errors.append("'excerpt' must be a non-empty string (provenance is not optional)")

    for date_key in ("event_date", "publication_date"):
        raw_date = item.get(date_key)
        if raw_date is not None and normalize_date(str(raw_date)) is None:
            errors.append(f"'{date_key}' {raw_date!r} could not be parsed as a date")

    if errors:
        return ValidationResult(ok=False, errors=errors, claim_data=None)

    return ValidationResult(ok=True, errors=[], claim_data=item)
