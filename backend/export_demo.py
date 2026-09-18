import json
import os
from dataclasses import asdict

from data.santa_barbara import CLAIMS, CURATED_LABEL, INCIDENT_ID, SOURCES
from reconciliation.normalize import normalize_claim
from reconciliation.status import derive_incident_status, field_narrative

OUTPUT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "frontend", "src", "data", "case-santa-barbara.json"
)


def _serialize_claim(c) -> dict:
    return {
        "id": c.id,
        "field": c.field.value,
        "raw_value": c.raw_value,
        "normalized_value": normalize_claim(c.field, c.raw_value),
        "source_id": c.source_id,
        "event_date": c.event_date.isoformat() if c.event_date else None,
        "publication_date": c.publication_date.isoformat() if c.publication_date else None,
        "excerpt": c.excerpt,
    }


def _serialize_source(s) -> dict:
    return {"id": s.id, "name": s.name, "type": s.type.value, "url": s.url}


def _serialize_group(g) -> dict:
    return {
        "normalized_value": g.normalized_value,
        "display_value": g.display_value,
        "claim_ids": g.claim_ids,
        "source_ids": sorted(g.source_ids),
    }


def build_payload() -> dict:
    result = derive_incident_status(INCIDENT_ID, CLAIMS)
    return {
        "label": CURATED_LABEL,
        "incident": {
            "id": INCIDENT_ID,
            "title": "Santa Barbara Well 1",
            "location_label": "Nembe, Bayelsa State",
            "period_label": "November 2021",
        },
        "sources": [_serialize_source(s) for s in SOURCES],
        "claims": [_serialize_claim(c) for c in CLAIMS],
        "fields": {
            field.value: {
                "status": assessment.status.value,
                "note": assessment.note,
                "narrative": field_narrative(field, assessment.status),
                "groups": [_serialize_group(g) for g in assessment.groups],
                "contributing_claim_ids": assessment.contributing_claim_ids,
            }
            for field, assessment in result.fields.items()
        },
        "summary": result.summary,
    }


def main() -> None:
    payload = build_payload()
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
