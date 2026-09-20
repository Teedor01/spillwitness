from export_demo import build_payload


def _claims_by_id(payload):
    return {c["id"]: c for c in payload["claims"]}


def _sources_by_id(payload):
    return {s["id"]: s for s in payload["sources"]}


def test_cause_sabotage_traces_to_nosdra_nuprc():
    payload = build_payload()
    claims, sources = _claims_by_id(payload), _sources_by_id(payload)

    cause = payload["fields"]["CAUSE"]
    sabotage_group = next(g for g in cause["groups"] if g["normalized_value"] == "SABOTAGE")
    assert "nosdra-nuprc-jiv" in sabotage_group["source_ids"]

    nosdra_cause_claim = next(
        c for cid in sabotage_group["claim_ids"]
        if (c := claims[cid])["source_id"] == "nosdra-nuprc-jiv"
    )
    assert nosdra_cause_claim["normalized_value"] == "SABOTAGE"
    assert sources[nosdra_cause_claim["source_id"]]["type"] == "FEDERAL_REGULATOR"


def test_cause_equipment_failure_traces_to_bayelsa_technical_committee():
    payload = build_payload()
    claims, sources = _claims_by_id(payload), _sources_by_id(payload)

    cause = payload["fields"]["CAUSE"]
    equipment_group = next(g for g in cause["groups"] if g["normalized_value"] == "EQUIPMENT_FAILURE")
    assert equipment_group["source_ids"] == ["bayelsa-technical-committee"]

    claim = claims[equipment_group["claim_ids"][0]]
    assert sources[claim["source_id"]]["type"] == "STATE_GOVERNMENT"


def test_cause_is_contested_with_incompatible_claims_reason():
    payload = build_payload()
    assert payload["fields"]["CAUSE"]["status"] == "CONTESTED"
    assert payload["fields"]["CAUSE"]["reason"] == "INCOMPATIBLE_CLAIMS"


def test_volume_two_million_traces_to_governor_diri():
    payload = build_payload()
    claims, sources = _claims_by_id(payload), _sources_by_id(payload)

    volume = payload["fields"]["VOLUME"]
    two_million_group = max(volume["groups"], key=lambda g: float(g["normalized_value"]))
    assert two_million_group["source_ids"] == ["bayelsa-governor"]
    claim = claims[two_million_group["claim_ids"][0]]
    assert "two million" in claim["raw_value"].lower()
    assert sources[claim["source_id"]]["type"] == "STATE_GOVERNMENT"


def test_volume_4150_traces_to_nosdra_dg():
    payload = build_payload()
    claims, sources = _claims_by_id(payload), _sources_by_id(payload)

    volume = payload["fields"]["VOLUME"]
    small_group = min(volume["groups"], key=lambda g: float(g["normalized_value"]))
    assert small_group["source_ids"] == ["nosdra-dg"]
    claim = claims[small_group["claim_ids"][0]]
    assert "4,150" in claim["raw_value"]
    assert sources[claim["source_id"]]["type"] == "FEDERAL_REGULATOR"


def test_volume_is_conflicting_with_incompatible_claims_reason():
    payload = build_payload()
    assert payload["fields"]["VOLUME"]["status"] == "CONFLICTING"
    assert payload["fields"]["VOLUME"]["reason"] == "INCOMPATIBLE_CLAIMS"


def test_every_claim_carries_a_normalized_value_or_explicit_none():
    payload = build_payload()
    for claim in payload["claims"]:
        assert "normalized_value" in claim


def test_thecable_attribution_is_exposed_not_baked_into_the_name():
    payload = build_payload()
    sources = _sources_by_id(payload)
    thecable = sources["thecable-jiv-member"]
    assert thecable["name"] == "TheCable"
    assert thecable["attributed_to"] is not None
    assert "Ekpenyong" in thecable["attributed_to"]


def test_sources_without_attribution_expose_none_not_a_missing_key():
    payload = build_payload()
    for source in payload["sources"]:
        if source["id"] != "thecable-jiv-member":
            assert source["attributed_to"] is None


def test_location_group_does_not_erase_a_dissenting_claims_own_wording():
    payload = build_payload()
    claims = _claims_by_id(payload)
    location = payload["fields"]["LOCATION"]
    assert location["status"] == "CORROBORATED"
    assert len(location["groups"]) == 1

    group = location["groups"][0]
    raw_values = {claims[cid]["raw_value"] for cid in group["claim_ids"]}
    assert len(raw_values) == 2, "the two location claims should keep their own distinct wording"
    assert any("Well 1" in v for v in raw_values)
    assert any("River" in v for v in raw_values)

def test_thecable_cause_claim_is_marked_derived_from_the_jiv_finding():
    payload = build_payload()
    claims = _claims_by_id(payload)
    thecable_claim = claims["c-cause-2"]
    assert thecable_claim["derived_from_claim_id"] == "c-cause-1"
    assert thecable_claim["derived_from_label"] is not None


def test_sabotage_group_excludes_thecable_from_independent_count_but_keeps_the_record():
    payload = build_payload()
    sabotage_group = next(
        g for g in payload["fields"]["CAUSE"]["groups"] if g["normalized_value"] == "SABOTAGE"
    )
    assert set(sabotage_group["source_ids"]) == {"nosdra-nuprc-jiv", "thecable-jiv-member"}
    assert set(sabotage_group["claim_ids"]) == {"c-cause-1", "c-cause-2"}
    # But only one of them counts as independent evidentiary support.
    assert sabotage_group["independent_source_ids"] == ["nosdra-nuprc-jiv"]


def test_cause_status_is_unchanged_by_the_independence_correction():
    payload = build_payload()
    assert payload["fields"]["CAUSE"]["status"] == "CONTESTED"


def test_only_thecable_claim_is_marked_derived_among_all_current_claims():
    payload = build_payload()
    derived = [c["id"] for c in payload["claims"] if c["derived_from_claim_id"]]
    assert derived == ["c-cause-2"]
