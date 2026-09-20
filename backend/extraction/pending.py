from __future__ import annotations

import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

from extraction.schema import validate_extracted_item
from models.evidence import Claim, ClaimField

DEFAULT_QUEUE_PATH = os.path.join(os.path.dirname(__file__), "pending_claims.json")


@dataclass
class PendingClaim:
    id: str
    incident_id: str
    source_id: str  
    status: str 
    data: dict  
    submitted_at: str
    reviewed_at: str | None = None
    reviewer_note: str = ""


def _load(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)


def _save(path: str, items: list[dict]) -> None:
    with open(path, "w") as f:
        json.dump(items, f, indent=2)


def submit_for_review(
    extracted_items: list[dict], incident_id: str, source_id: str, path: str = DEFAULT_QUEUE_PATH
) -> tuple[list[PendingClaim], list[str]]:
    """Validates each extracted item and queues the valid ones as
    PENDING. Invalid items are never queued... their errors are returned
    so the operator sees exactly why, but nothing invalid ever reaches
    the human-review step disguised as reviewable."""
    accepted: list[PendingClaim] = []
    rejected_reasons: list[str] = []

    for item in extracted_items:
        result = validate_extracted_item(item)
        if not result.ok:
            rejected_reasons.append(f"{item!r} -> {result.errors}")
            continue
        pending = PendingClaim(
            id=str(uuid.uuid4())[:8],
            incident_id=incident_id,
            source_id=source_id,
            status="PENDING",
            data=result.claim_data,
            submitted_at=datetime.now(timezone.utc).isoformat(),
        )
        accepted.append(pending)

    existing = _load(path)
    existing.extend(asdict(p) for p in accepted)
    _save(path, existing)
    return accepted, rejected_reasons


def list_pending(path: str = DEFAULT_QUEUE_PATH, status: str | None = "PENDING") -> list[dict]:
    items = _load(path)
    if status is None:
        return items
    return [i for i in items if i["status"] == status]


def approve(pending_id: str, reviewer_note: str = "", path: str = DEFAULT_QUEUE_PATH) -> dict:
    items = _load(path)
    for item in items:
        if item["id"] == pending_id:
            if item["status"] != "PENDING":
                raise ValueError(f"pending claim {pending_id} is already {item['status']}")
            item["status"] = "APPROVED"
            item["reviewed_at"] = datetime.now(timezone.utc).isoformat()
            item["reviewer_note"] = reviewer_note
            _save(path, items)
            return item
    raise KeyError(f"no pending claim with id {pending_id}")


def reject(pending_id: str, reviewer_note: str, path: str = DEFAULT_QUEUE_PATH) -> dict:
    items = _load(path)
    for item in items:
        if item["id"] == pending_id:
            if item["status"] != "PENDING":
                raise ValueError(f"pending claim {pending_id} is already {item['status']}")
            item["status"] = "REJECTED"
            item["reviewed_at"] = datetime.now(timezone.utc).isoformat()
            item["reviewer_note"] = reviewer_note
            _save(path, items)
            return item
    raise KeyError(f"no pending claim with id {pending_id}")


def approved_to_claims(path: str = DEFAULT_QUEUE_PATH) -> list[Claim]:
    """Converts every APPROVED pending item, and only APPROVED items,
    into a real Claim. This is the single point where extracted data
    crosses into the trusted model... everything upstream of this
    function is still just proposed data, however well-formed."""
    claims: list[Claim] = []
    for item in _load(path):
        if item["status"] != "APPROVED":
            continue
        d = item["data"]
        claims.append(Claim(
            id=f"extracted-{item['id']}",
            incident_id=item["incident_id"],
            field=ClaimField(d["field"]),
            raw_value=d["raw_value"],
            source_id=item["source_id"],
            excerpt=d.get("excerpt"),
        ))
    return claims
