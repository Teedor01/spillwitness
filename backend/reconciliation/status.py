from __future__ import annotations

from models.evidence import (
    Claim,
    ClaimField,
    FieldAssessment,
    FieldStatus,
    IncidentAssessment,
    ValueGroup,
)
from reconciliation.normalize import normalize_claim

_CONTESTED_FIELDS = {ClaimField.CAUSE}


def derive_field_status(claim_field: ClaimField, claims: list[Claim]) -> FieldAssessment:
    field_claims = [c for c in claims if c.field == claim_field]

    if not field_claims:
        return FieldAssessment(
            field=claim_field,
            status=FieldStatus.NOT_ENOUGH_EVIDENCE,
            note="No source makes a claim on this field.",
        )

    groups_by_value: dict[str, ValueGroup] = {}
    unquantified_claim_ids: list[str] = []

    for c in field_claims:
        key = normalize_claim(c.field, c.raw_value)
        if key is None:
            unquantified_claim_ids.append(c.id)
            continue
        group = groups_by_value.setdefault(
            key, ValueGroup(normalized_value=key, display_value=c.raw_value)
        )
        group.claim_ids.append(c.id)
        group.source_ids.add(c.source_id)

    groups = sorted(groups_by_value.values(), key=lambda g: len(g.source_ids), reverse=True)
    contributing = [cid for g in groups for cid in g.claim_ids] + unquantified_claim_ids

    if not groups:
        return FieldAssessment(
            field=claim_field,
            status=FieldStatus.NOT_ENOUGH_EVIDENCE,
            contributing_claim_ids=contributing,
            note="Sources reference this field but none state a concrete value.",
        )

    if len(groups) == 1:
        sole_group = groups[0]
        if len(sole_group.source_ids) >= 2:
            status = FieldStatus.CORROBORATED
            note = f"{len(sole_group.source_ids)} independent sources agree."
        else:
            status = FieldStatus.UNRESOLVED
            note = "Only one source makes this claim; not independently corroborated."
        return FieldAssessment(
            field=claim_field, status=status, groups=groups,
            contributing_claim_ids=contributing, note=note,
        )

    status = FieldStatus.CONTESTED if claim_field in _CONTESTED_FIELDS else FieldStatus.CONFLICTING
    lead, runner_up = groups[0], groups[1]
    note = (
        f"{len(groups)} distinct values reported: "
        f"'{lead.display_value}' ({len(lead.source_ids)} source(s)) vs. "
        f"'{runner_up.display_value}' ({len(runner_up.source_ids)} source(s))."
    )
    return FieldAssessment(
        field=claim_field, status=status, groups=groups,
        contributing_claim_ids=contributing, note=note,
    )


def _occurrence_line(status: FieldStatus) -> str:
    return {
        FieldStatus.CORROBORATED: "Incident occurrence is well supported.",
        FieldStatus.UNRESOLVED: "Incident occurrence is reported by a single source and not independently corroborated.",
        FieldStatus.NOT_ENOUGH_EVIDENCE: "Incident occurrence is not established by available evidence.",
    }.get(status, "Incident occurrence status could not be determined.")


def _cause_line(status: FieldStatus) -> str:
    return {
        FieldStatus.CORROBORATED: "The cause is supported by multiple independent sources.",
        FieldStatus.CONTESTED: "The cause remains contested across sources. No causal conclusion is asserted.",
        FieldStatus.UNRESOLVED: "A cause has been suggested by a single source and is not independently corroborated.",
        FieldStatus.NOT_ENOUGH_EVIDENCE: "No source has stated a cause. The cause is not established.",
    }.get(status, "Cause status could not be determined.")


def _volume_line(status: FieldStatus) -> str:
    return {
        FieldStatus.CORROBORATED: "Reported volume figures are consistent across sources.",
        FieldStatus.CONFLICTING: "Reported volume figures conflict significantly across sources. No single figure is asserted as correct.",
        FieldStatus.UNRESOLVED: "A volume figure comes from a single source and is not independently corroborated.",
        FieldStatus.NOT_ENOUGH_EVIDENCE: "No source has stated a volume figure.",
    }.get(status, "Volume status could not be determined.")


_FIELD_LINE_FN = {
    ClaimField.OCCURRENCE: _occurrence_line,
    ClaimField.CAUSE: _cause_line,
    ClaimField.VOLUME: _volume_line,
}


def field_narrative(claim_field: ClaimField, status: FieldStatus) -> str:
    fn = _FIELD_LINE_FN.get(claim_field)
    if fn is None:

        return ""
    return fn(status)


def derive_incident_status(incident_id: str, claims: list[Claim]) -> IncidentAssessment:
    fields = {f: derive_field_status(f, claims) for f in ClaimField}

    lines = [
        _occurrence_line(fields[ClaimField.OCCURRENCE].status),
        _cause_line(fields[ClaimField.CAUSE].status),
        _volume_line(fields[ClaimField.VOLUME].status),
    ]

    return IncidentAssessment(incident_id=incident_id, fields=fields, summary=" ".join(lines))
