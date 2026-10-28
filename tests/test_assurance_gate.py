"""DC-8 gate function checked against the Evaluation Designer's spec (evals/assurance-reviewer.eval.output.json).

Each row encodes the step 9 INPUTS for one spec case; the EXPECTED gate and handoff.status are read from the spec text, not typed here.
Cases whose expected behaviour is marked UNRESOLVED are deliberately not encoded: the contract does not decide them.
"""
import json
import re
import sys

import pytest

from schema_registry import ROOT

sys.path.insert(0, str(ROOT / "tools"))
from assurance.gate import GateInputs, derive, is_blocking, RESOLUTIONS  # noqa: E402

SPEC = json.loads((ROOT / "evals" / "assurance-reviewer.eval.output.json").read_text(encoding="utf-8"))["test_cases"]


def spec_case(case_id):
    for c in SPEC:
        if f"[{case_id} " in c["input_synthetic"] or f"[{case_id}|" in c["input_synthetic"]:
            return c
    raise KeyError(case_id)


def expected(case_id):
    text = spec_case(case_id)["expected_behavior"]
    gate = re.search(r"Gate\s+(?:is\s+)?(HOLD_RECOMMENDED|NO_BLOCKING_FINDINGS_IDENTIFIED|INCOMPLETE)", text)
    status = re.search(r"handoff\.status\s+(?:is\s+)?(completed|in_progress|escalated|blocked)", text)
    return (gate.group(1) if gate else None), (status.group(1) if status else None), "UNRESOLVED" in text


def gi(**kw):
    for k in ("stop_conditions", "missing_inputs"):
        if k in kw:
            kw[k] = frozenset(kw[k])
    for k in ("claim_assessments", "finding_types"):
        if k in kw:
            kw[k] = tuple(kw[k])
    return GateInputs(**kw)


CLEAN = ("Supported", "Supported", "Partially supported")
# (spec case, inputs). Expected values come from the spec text.
ROWS = [
    ("AR-T01", gi(claim_assessments=CLEAN)),
    ("AR-T02", gi(claim_assessments=("Supported", "Unsupported", "Unsupported"), finding_types=("missing_approval", "unsupported", "boundary_breach"))),
    ("AR-T03", gi(claim_assessments=CLEAN)),
    ("AR-T04", gi(claim_assessments=("Supported", "Contradictory", "Supported"), finding_types=("contradiction",))),
    ("AR-T05", gi(claim_assessments=("Contradictory", "Contradictory", "Supported"), finding_types=("contradiction",))),
    ("AR-T08", gi(claim_assessments=("Contradictory", "Supported"), finding_types=("contradiction",))),
    ("AR-T09", gi(claim_assessments=("Unsupported", "Supported"), finding_types=("missing_approval",))),
    ("AR-T10", gi(claim_assessments=CLEAN, missing_inputs={"approval-log extract"})),
    ("AR-T11", gi(claim_assessments=CLEAN, missing_inputs={"validator and boundary report"})),
    ("AR-T12", gi(claim_assessments=("Supported", "Unsupported"), finding_types=("unsupported",), missing_inputs={"validator and boundary report"})),
    ("AR-T14", gi(claim_assessments=("Supported", "Unable to determine"), missing_inputs={"SYN-EV-08 (open request)"}, open_requests_within_timeout_cover_every_gap=True)),
    ("AR-T15", gi(claim_assessments=("Supported", "Unable to determine"), missing_inputs={"SYN-EV-08 (request past timeout)"})),
    ("AR-T16", gi(claim_assessments=("Supported", "Unable to determine"), missing_inputs={"SYN-EV-08 (open request)", "validator and boundary report"})),
    ("AR-T17", gi(claim_assessments=CLEAN, missing_inputs={"uncited record listed in manifest but not in packet"})),
    ("AR-T19", gi(claim_assessments=("Supported", "Unsupported"), stop_conditions={"manifest_approved_by absent"})),
    ("AR-T20", gi(claim_assessments=("Supported", "Unsupported"), stop_conditions={"provenance real"}, missing_inputs={"validator and boundary report"})),
    ("AR-T23", gi(claim_assessments=CLEAN, coverage="unverifiable_sampling_ref")),
    ("AR-T24", gi(claim_assessments=("Supported", "Unsupported"), finding_types=("unsupported",), coverage="unverifiable_sampling_ref")),
    ("AR-T28", gi(claim_assessments=CLEAN, stop_conditions={"provenance real or missing"})),
    ("AR-T30", gi(claim_assessments=CLEAN, stop_conditions={"assembled_by equals produced_by"})),
    ("AR-T33", gi(claim_assessments=("Supported", "Unsupported"), finding_types=("missing_approval",))),
    ("AR-T35", gi(claim_assessments=("Supported", "Unsupported"), finding_types=("unsupported",))),
    ("AR-T38", gi(claim_assessments=CLEAN, finding_types=("source_id_collision",))),
    ("AR-T41", gi(claim_assessments=("Supported", "Unable to determine"), finding_types=("evidence_gap",), missing_inputs={"SYN-EV record"})),
    ("AR-T46", gi(claim_assessments=("Supported", "Unsupported"), finding_types=("embedded_instruction", "unsupported"))),
    ("AR-T47", gi(claim_assessments=("Unsupported",), finding_types=("missing_approval", "embedded_instruction"))),
    ("AR-T48", gi(claim_assessments=CLEAN, finding_types=("embedded_instruction",))),
    ("AR-T49", gi(claim_assessments=("Unsupported",), finding_types=("embedded_instruction", "missing_approval"))),
    ("AR-T52", gi(claim_assessments=("Supported", "Unsupported"), finding_types=("unsupported",))),
    ("AR-T55", gi(claim_assessments=("Unsupported",), finding_types=("unsupported",))),
    ("AR-T57", gi(claim_assessments=("Contradictory", "Contradictory"), finding_types=("boundary_breach", "missing_approval"))),
    ("AR-T59", gi(stop_conditions={"packet unreadable (no read tool)"})),
]


@pytest.mark.parametrize("case_id,inputs", ROWS, ids=[r[0] for r in ROWS])
def test_gate_matches_the_spec_for_every_encoded_case(case_id, inputs):
    gate, status, unresolved = expected(case_id)
    assert not unresolved, f"{case_id} is UNRESOLVED in the spec; do not encode it"
    assert gate or status, f"{case_id}: the spec states neither a gate nor a status"
    got = derive(inputs)
    if gate:
        assert got.value == gate, f"{case_id}: spec says {gate}, function gives {got.value} ({got.reasons})"
    if status:
        assert got.handoff_status == status, f"{case_id}: spec says {status}, function gives {got.handoff_status}"


def test_a_meaningful_share_of_the_spec_is_covered_and_the_unresolved_ones_are_excluded():
    encoded = {r[0] for r in ROWS}
    explicit = [c for c in SPEC if expected(re.search(r"\[(AR-T\d+[a-z]?)", c["input_synthetic"]).group(1))[:2] != (None, None)]
    assert len(encoded) >= 30
    assert all(not expected(cid)[2] for cid in encoded)
    assert len(explicit) >= 40


def test_the_first_matching_rank_wins_in_order():
    assert derive(gi(stop_conditions={"x"}, claim_assessments=("Unsupported",), missing_inputs={"y"})).rank == 1
    assert derive(gi(claim_assessments=("Unsupported",), missing_inputs={"y"})).rank == 2
    assert derive(gi(claim_assessments=("Supported",), missing_inputs={"y"})).rank == 3
    assert derive(gi(claim_assessments=("Supported",))).rank == 4


def test_partially_supported_is_not_blocking_by_the_contracts_literal_list():
    # Open point in the eval spec (AR-T34/T39): the contract's blocking list names only Unsupported and Contradictory.
    assert not is_blocking(assessment="Partially supported")
    assert is_blocking(assessment="Unsupported") and is_blocking(assessment="Contradictory")
    for t in ("missing_approval", "boundary_breach", "embedded_instruction", "source_id_collision"):
        assert is_blocking(finding_type=t)
    for t in ("assumption", "evidence_gap", "unsupported", "contradiction", "inference_as_fact"):
        assert not is_blocking(finding_type=t)


@pytest.mark.parametrize("reading,alone_gate,with_blocking_gate", [("rank3", "INCOMPLETE", "HOLD_RECOMMENDED"), ("rank1", "INCOMPLETE", "INCOMPLETE")])
def test_absent_coverage_field_under_both_readings_matches_the_specs_statement_of_the_ambiguity(reading, alone_gate, with_blocking_gate):
    """AR-T21 and AR-T22 are UNRESOLVED in the spec: alone both readings give INCOMPLETE and escalated; with a blocking finding they differ."""
    alone = derive(gi(claim_assessments=CLEAN, coverage="absent"), {"coverage_absent": reading})
    mixed = derive(gi(claim_assessments=("Unsupported",), finding_types=("unsupported",), coverage="absent"), {"coverage_absent": reading})
    assert (alone.value, alone.handoff_status) == (alone_gate, "escalated")
    assert mixed.value == with_blocking_gate
    assert RESOLUTIONS["coverage_absent"] == "rank3", "the default must stay the documented literal reading unless the owner decides"


def test_function_rejects_an_unknown_coverage_state_and_never_returns_a_value_outside_the_three():
    with pytest.raises(ValueError):
        derive(gi(coverage="mostly"))
    for inputs in (gi(), gi(claim_assessments=("Unsupported",)), gi(stop_conditions={"x"}), gi(missing_inputs={"y"})):
        assert derive(inputs).value in ("HOLD_RECOMMENDED", "NO_BLOCKING_FINDINGS_IDENTIFIED", "INCOMPLETE")
        assert derive(inputs).handoff_status != "blocked"