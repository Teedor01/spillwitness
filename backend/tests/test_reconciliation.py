from datetime import date

from data.santa_barbara import CLAIMS as SB_CLAIMS, INCIDENT_ID as SB_INCIDENT_ID
from models.evidence import Claim, ClaimField, FieldStatus
from reconciliation.compare import claims_agree, claims_conflict, calculate_source_overlap
from reconciliation.normalize import normalize_cause, normalize_date, normalize_location, normalize_volume
from reconciliation.status import derive_field_status, derive_incident_status


def _claim(id_, field_, value, source_id, **kw):
    return Claim(id=id_, incident_id="test-incident", field=field_, raw_value=value, source_id=source_id, **kw)



def test_normalize_date_handles_multiple_formats():
    assert normalize_date("2021-11-05") == date(2021, 11, 5)
    assert normalize_date("November 5, 2021") == date(2021, 11, 5)
    assert normalize_date("Nov 5, 2021") == date(2021, 11, 5)
    assert normalize_date("not a date") is None


def test_normalize_location_merges_known_alias_and_typo():
    assert normalize_location("Santa Barbra River") == normalize_location("Santa Barbara River")


def test_normalize_location_corroborates_at_community_level_across_site_names():
    assert normalize_location("Santa Barbara Well 1, Nembe, Bayelsa State") == \
        normalize_location("Santa Barbra River, Nembe, Bayelsa State")


def test_normalize_location_does_not_merge_different_communities():
    assert normalize_location("Nembe, Bayelsa State") != normalize_location("Eleme, Rivers State")


def test_normalize_cause_maps_synonyms_to_same_bucket():
    assert normalize_cause("sabotage") == normalize_cause("external interference")
    assert normalize_cause("equipment failure") == normalize_cause("equipment and maintenance failure")
    assert normalize_cause("sabotage") != normalize_cause("equipment failure")


def test_normalize_volume_extracts_numbers_words_and_millions():
    assert normalize_volume("about two million barrels") == 2_000_000  
    assert normalize_volume("2,000,000 barrels") == 2_000_000
    assert normalize_volume("2 million barrels") == 2_000_000
    assert normalize_volume("no figure given here") is None



def test_identical_claims_agree():
    a = _claim("a", ClaimField.CAUSE, "sabotage", "src-1")
    b = _claim("b", ClaimField.CAUSE, "sabotage", "src-2")
    assert claims_agree(a, b)
    assert not claims_conflict(a, b)


def test_semantically_equivalent_claims_agree():
    a = _claim("a", ClaimField.CAUSE, "sabotage", "src-1")
    b = _claim("b", ClaimField.CAUSE, "third-party interference", "src-2")
    assert claims_agree(a, b)


def test_conflicting_dates_do_not_agree():
    a = _claim("a", ClaimField.DATE, "2021-11-05", "src-1")
    b = _claim("b", ClaimField.DATE, "2021-11-06", "src-2")
    assert not claims_agree(a, b)
    assert claims_conflict(a, b)


def test_conflicting_causes_conflict():
    a = _claim("a", ClaimField.CAUSE, "sabotage", "src-1")
    b = _claim("b", ClaimField.CAUSE, "equipment failure", "src-2")
    assert claims_conflict(a, b)


def test_same_source_never_conflicts_with_itself():
    a = _claim("a", ClaimField.CAUSE, "sabotage", "src-1")
    b = _claim("b", ClaimField.CAUSE, "equipment failure", "src-1")
    assert not claims_conflict(a, b)


def test_missing_quantity_never_agrees_or_conflicts():
    a = _claim("a", ClaimField.VOLUME, "the claim is disputed", "src-1")
    b = _claim("b", ClaimField.VOLUME, "2,000,000 barrels", "src-2")
    assert not claims_agree(a, b)
    assert not claims_conflict(a, b)


def test_source_overlap_groups_by_normalized_value():
    claims = [
        _claim("a", ClaimField.CAUSE, "sabotage", "src-1"),
        _claim("b", ClaimField.CAUSE, "external interference", "src-2"),
        _claim("c", ClaimField.CAUSE, "equipment failure", "src-3"),
    ]
    overlap = calculate_source_overlap(claims)
    assert overlap["SABOTAGE"] == {"src-1", "src-2"}
    assert overlap["EQUIPMENT_FAILURE"] == {"src-3"}



def test_no_claims_is_not_enough_evidence():
    assessment = derive_field_status(ClaimField.CAUSE, [])
    assert assessment.status == FieldStatus.NOT_ENOUGH_EVIDENCE


def test_single_source_claim_is_unresolved_not_corroborated():
    claims = [_claim("a", ClaimField.CAUSE, "sabotage", "src-1")]
    assessment = derive_field_status(ClaimField.CAUSE, claims)
    assert assessment.status == FieldStatus.UNRESOLVED


def test_two_independent_agreeing_sources_are_corroborated():
    claims = [
        _claim("a", ClaimField.OCCURRENCE, "occurred", "src-1"),
        _claim("b", ClaimField.OCCURRENCE, "occurred", "src-2"),
    ]
    assessment = derive_field_status(ClaimField.OCCURRENCE, claims)
    assert assessment.status == FieldStatus.CORROBORATED


def test_three_sources_supporting_one_value_are_corroborated_with_full_provenance():
    claims = [
        _claim("a", ClaimField.OCCURRENCE, "occurred", "src-1"),
        _claim("b", ClaimField.OCCURRENCE, "occurred", "src-2"),
        _claim("c", ClaimField.OCCURRENCE, "occurred", "src-3"),
    ]
    assessment = derive_field_status(ClaimField.OCCURRENCE, claims)
    assert assessment.status == FieldStatus.CORROBORATED
    assert set(assessment.contributing_claim_ids) == {"a", "b", "c"}


def test_one_source_contradicting_two_is_still_conflicting_but_minority_is_visible():
    claims = [
        _claim("a", ClaimField.CAUSE, "sabotage", "src-1"),
        _claim("b", ClaimField.CAUSE, "sabotage", "src-2"),
        _claim("c", ClaimField.CAUSE, "equipment failure", "src-3"),
    ]
    assessment = derive_field_status(ClaimField.CAUSE, claims)
    assert assessment.status == FieldStatus.CONTESTED
    # majority group listed first
    assert assessment.groups[0].normalized_value == "SABOTAGE"
    assert len(assessment.groups[0].source_ids) == 2
    assert len(assessment.groups[1].source_ids) == 1


def test_cause_disagreement_is_contested_not_conflicting():
    claims = [
        _claim("a", ClaimField.CAUSE, "sabotage", "src-1"),
        _claim("b", ClaimField.CAUSE, "equipment failure", "src-2"),
    ]
    assert derive_field_status(ClaimField.CAUSE, claims).status == FieldStatus.CONTESTED


def test_volume_disagreement_is_conflicting_not_contested():
    claims = [
        _claim("a", ClaimField.VOLUME, "2,000,000 barrels", "src-1"),
        _claim("b", ClaimField.VOLUME, "4,150 barrels", "src-2"),
    ]
    assert derive_field_status(ClaimField.VOLUME, claims).status == FieldStatus.CONFLICTING


def test_missing_jiv_still_allows_occurrence_corroboration_from_other_sources():

    claims = [
        _claim("a", ClaimField.OCCURRENCE, "occurred", "operator-1"),
        _claim("b", ClaimField.OCCURRENCE, "occurred", "news-1"),
    ]
    assert derive_field_status(ClaimField.OCCURRENCE, claims).status == FieldStatus.CORROBORATED


def test_provenance_is_preserved_through_field_assessment():
    claims = [
        _claim("claim-a", ClaimField.CAUSE, "sabotage", "src-1"),
        _claim("claim-b", ClaimField.CAUSE, "equipment failure", "src-2"),
    ]
    assessment = derive_field_status(ClaimField.CAUSE, claims)
    assert set(assessment.contributing_claim_ids) == {"claim-a", "claim-b"}



def test_santa_barbara_incident_end_to_end():
    result = derive_incident_status(SB_INCIDENT_ID, SB_CLAIMS)

    assert result.fields[ClaimField.OCCURRENCE].status == FieldStatus.CORROBORATED

    assert result.fields[ClaimField.LOCATION].status == FieldStatus.CORROBORATED

    assert result.fields[ClaimField.DATE].status == FieldStatus.CORROBORATED

    assert result.fields[ClaimField.CAUSE].status == FieldStatus.CONTESTED
    cause_values = {g.normalized_value for g in result.fields[ClaimField.CAUSE].groups}
    assert cause_values == {"SABOTAGE", "EQUIPMENT_FAILURE"}

    assert result.fields[ClaimField.VOLUME].status == FieldStatus.CONFLICTING

    assert "contested" in result.summary.lower()
    assert "sabotage" not in result.summary.lower()
    assert "equipment" not in result.summary.lower()
