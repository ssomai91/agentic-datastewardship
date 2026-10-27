import copy

import pytest

from handoff_checks import handoff_reference_problems
from schema_registry import ROOT, SCHEMAS, load, validator_for

HANDOFF = SCHEMAS / "agent-handoff.schema.json"
CLAIM = SCHEMAS / "material-claim.schema.json"
EXAMPLE = load(ROOT / "examples" / "agent-handoff.valid.example.json")


def errors(schema_path, instance):
    return list(validator_for(schema_path).iter_errors(instance))


def test_valid_handoff_with_evidence_and_claims_passes():
    assert errors(HANDOFF, EXAMPLE) == []
    assert handoff_reference_problems(EXAMPLE) == []


def test_handoff_evidence_must_be_structured_records():
    bad = copy.deepcopy(EXAMPLE)
    bad["evidence"] = ["a plain string is no longer evidence"]
    assert errors(HANDOFF, bad)


def test_handoff_evidence_record_needs_authority_level():
    bad = copy.deepcopy(EXAMPLE)
    del bad["evidence"][0]["authority_level"]
    assert errors(HANDOFF, bad)


def test_handoff_requires_claims_field():
    bad = copy.deepcopy(EXAMPLE)
    del bad["claims"]
    assert any("claims" in e.message for e in errors(HANDOFF, bad))


@pytest.mark.parametrize("field", ["claim_id", "statement", "claim_type", "confidence", "evidence_ids"])
def test_claim_requires_each_field(field):
    bad = copy.deepcopy(EXAMPLE["claims"][0])
    del bad[field]
    assert errors(CLAIM, bad)


def test_claim_rejects_unknown_confidence_label():
    bad = copy.deepcopy(EXAMPLE["claims"][0])
    bad["confidence"] = "Probably"
    assert errors(CLAIM, bad)


def test_claim_rejects_unknown_claim_type():
    bad = copy.deepcopy(EXAMPLE["claims"][0])
    bad["claim_type"] = "hunch"
    assert errors(CLAIM, bad)


@pytest.mark.parametrize("confidence", ["Supported", "Partially supported", "Contradictory"])
def test_supported_style_claims_need_evidence(confidence):
    bad = copy.deepcopy(EXAMPLE["claims"][0])
    bad.update(confidence=confidence, claim_type="agent_inference", evidence_ids=[])
    assert errors(CLAIM, bad)


@pytest.mark.parametrize("claim_type", ["authoritative_internal", "general_industry"])
def test_evidence_based_claim_types_need_evidence(claim_type):
    bad = copy.deepcopy(EXAMPLE["claims"][0])
    bad.update(claim_type=claim_type, confidence="Unsupported", evidence_ids=[])
    assert errors(CLAIM, bad)


@pytest.mark.parametrize("confidence", ["Unsupported", "Unable to determine"])
def test_inference_and_open_question_may_have_no_evidence(confidence):
    ok = copy.deepcopy(EXAMPLE["claims"][0])
    ok.update(claim_type="open_question", confidence=confidence, evidence_ids=[])
    assert errors(CLAIM, ok) == []


def test_claim_citing_missing_evidence_is_caught():
    bad = copy.deepcopy(EXAMPLE)
    bad["claims"][0]["evidence_ids"] = ["EV-9999"]
    assert handoff_reference_problems(bad) == ["CL-0001 cites unknown evidence EV-9999"]


def test_duplicate_ids_are_caught():
    bad = copy.deepcopy(EXAMPLE)
    bad["claims"].append(copy.deepcopy(bad["claims"][0]))
    bad["evidence"].append(copy.deepcopy(bad["evidence"][0]))
    assert set(handoff_reference_problems(bad)) == {"duplicate evidence source_id", "duplicate claim_id"}