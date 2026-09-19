import os

from data.santa_barbara import CLAIMS as SB_CLAIMS, INCIDENT_ID, SOURCES
from extraction import pending
from extraction.llm_extractor import extract_offline
from extraction.schema import validate_extracted_item
from models.evidence import ClaimField, FieldStatus
from reconciliation.status import derive_incident_status

FIXTURE = os.path.join(
    os.path.dirname(__file__), "..", "extraction", "fixtures", "aiteo_thecable_2022-02-16.json"
)


def test_validator_accepts_a_well_formed_extraction():
    items = extract_offline(FIXTURE)
    result = validate_extracted_item(items[0])
    assert result.ok
    assert result.errors == []


def test_validator_rejects_forbidden_reconciliation_keys():
    bad_item = {
        "field": "CAUSE", "raw_value": "sabotage", "source_name": "X",
        "source_type": "NEWS", "excerpt": "text", "confidence": 0.9, "status": "CORROBORATED",
    }
    result = validate_extracted_item(bad_item)
    assert not result.ok
    assert any("forbidden" in e for e in result.errors)


def test_validator_rejects_missing_required_fields():
    incomplete = {"field": "CAUSE", "raw_value": "sabotage"}
    result = validate_extracted_item(incomplete)
    assert not result.ok
    assert any("missing required" in e for e in result.errors)


def test_validator_rejects_unknown_field_enum_value():
    bad_field = {
        "field": "CONCLUSION", "raw_value": "x", "source_name": "X",
        "source_type": "NEWS", "excerpt": "text",
    }
    result = validate_extracted_item(bad_field)
    assert not result.ok


def test_full_pipeline_extract_validate_pending_approve_reconcile(tmp_path):
    queue_path = str(tmp_path / "pending_claims.json")

    # 1. LLM extracts (offline fixture standing in for the live call,
    #    since no ANTHROPIC_API_KEY exists in this test environment).
    items = extract_offline(FIXTURE)

    # 2. Schema validates + queues for human review. Nothing is trusted yet.
    accepted, rejected = pending.submit_for_review(
        items, incident_id=INCIDENT_ID, source_id="aiteo-statement", path=queue_path
    )
    assert len(accepted) == 1
    assert rejected == []
    assert pending.list_pending(path=queue_path)[0]["status"] == "PENDING"

    baseline = derive_incident_status(INCIDENT_ID, SB_CLAIMS)
    sabotage_group = next(g for g in baseline.fields[ClaimField.CAUSE].groups if g.normalized_value == "SABOTAGE")
    assert sabotage_group.independent_source_ids == {"nosdra-nuprc-jiv"}


    pending_id = accepted[0].id
    pending.approve(pending_id, reviewer_note="verified against the source directly", path=queue_path)
    assert pending.list_pending(path=queue_path, status="APPROVED")[0]["status"] == "APPROVED"


    extracted_claims = pending.approved_to_claims(path=queue_path)
    assert len(extracted_claims) == 1
    merged_claims = SB_CLAIMS + extracted_claims

    result = derive_incident_status(INCIDENT_ID, merged_claims)


    sabotage_group = next(g for g in result.fields[ClaimField.CAUSE].groups if g.normalized_value == "SABOTAGE")
    assert sabotage_group.independent_source_ids == {"nosdra-nuprc-jiv", "aiteo-statement"}


    assert result.fields[ClaimField.CAUSE].status == FieldStatus.CONTESTED


def test_rejected_claims_never_reach_reconciliation(tmp_path):
    queue_path = str(tmp_path / "pending_claims.json")
    items = extract_offline(FIXTURE)
    accepted, _ = pending.submit_for_review(items, INCIDENT_ID, "aiteo-statement", path=queue_path)
    pending.reject(accepted[0].id, reviewer_note="could not verify against the primary source", path=queue_path)

    extracted_claims = pending.approved_to_claims(path=queue_path)
    assert extracted_claims == []


def test_shipped_santa_barbara_dataset_is_untouched_by_the_extraction_module():
    from data.santa_barbara import CLAIMS
    assert len(CLAIMS) == 12
    assert all(not c.id.startswith("extracted-") for c in CLAIMS)
