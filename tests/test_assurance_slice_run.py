"""The six packets for the first Assurance Reviewer run and their FROZEN expected results."""
import json
import sys

import pytest

from schema_registry import ROOT

sys.path.insert(0, str(ROOT / "tools"))
from assurance import run_slice  # noqa: E402
from assurance.gate import GateInputs, derive  # noqa: E402
from assurance.manifest import coverage_state, missing_inputs, stop_conditions  # noqa: E402
from assurance.validator import result_of  # noqa: E402

PASS1 = ROOT / "evals" / "assurance-runs" / "pass1"
EXPECTED = json.loads((ROOT / "evals" / "assurance-runs" / "EXPECTED.json").read_text(encoding="utf-8"))["packets"]
PACKETS = run_slice.packets()


def test_expected_results_are_frozen_for_exactly_these_six_packets():
    assert set(EXPECTED) == set(PACKETS) == {"A1", "A2", "A3", "A4", "A5", "A6"}
    for e in EXPECTED.values():
        assert e["expected_gate"] and e["expected_status"] and e["expected_rank"]


@pytest.mark.parametrize("pid", sorted(PACKETS))
def test_committed_packets_are_exactly_what_the_builder_produces(pid):
    committed = json.loads((PASS1 / pid / "manifest.json").read_text(encoding="utf-8"))
    assert committed == PACKETS[pid].manifest
    for item in PACKETS[pid].manifest["items"]:
        assert (PASS1 / pid / item["path"]).read_text(encoding="utf-8") == PACKETS[pid].items[item["path"]]


def inputs(pid, assessments):
    m = PACKETS[pid].manifest
    return GateInputs(frozenset(stop_conditions(m)), tuple(assessments), (), frozenset(missing_inputs(m, PACKETS[pid].items)), coverage_state(m))


@pytest.mark.parametrize("pid", ["A1", "A2", "A3", "A4"])
def test_the_content_packets_have_no_stop_condition_and_no_missing_input(pid):
    m = PACKETS[pid].manifest
    assert not stop_conditions(m) and not missing_inputs(m, PACKETS[pid].items)


def test_a5_is_a_rank_1_stop_on_provenance_and_a6_a_rank_3_gap_exactly_as_frozen():
    a5 = derive(inputs("A5", ()))
    assert (a5.value, a5.rank, a5.handoff_status) == (EXPECTED["A5"]["expected_gate"], EXPECTED["A5"]["expected_rank"], EXPECTED["A5"]["expected_status"])
    assert any("provenance" in r for r in a5.reasons)
    a6 = derive(inputs("A6", ("Supported",)))
    assert (a6.value, a6.rank, a6.handoff_status) == (EXPECTED["A6"]["expected_gate"], EXPECTED["A6"]["expected_rank"], EXPECTED["A6"]["expected_status"])
    assert missing_inputs(PACKETS["A6"].manifest, PACKETS["A6"].items) == {"approval-log extract"}


def test_the_seeded_defect_is_in_a3_and_a4_only_and_the_injection_is_in_a4_only():
    def pack(pid):
        return json.loads(PACKETS[pid].items["pack/producer-output.json"])
    ids = {pid: [c["claim_id"] for c in pack(pid)["handoff"]["claims"]] for pid in PACKETS}
    assert "CL-SEED-1" in ids["A3"] and "CL-SEED-1" in ids["A4"]
    assert not any("CL-SEED-1" in v for k, v in ids.items() if k not in ("A3", "A4"))
    assert "Reviewer note" in pack("A4")["summary"] and "Reviewer note" not in pack("A3")["summary"]


def test_the_seed_really_is_unsupported_by_the_cited_record_and_every_producer_pack_is_valid():
    rec = json.loads(PACKETS["A3"].items["evidence/GL-101.json"])
    assert "owner" not in rec["extracted_fact"].lower()
    for pid, packet in PACKETS.items():
        report = json.loads(packet.items["checks/validator-report.json"])
        assert result_of(report, "output_schema") == "pass", pid
        assert result_of(report, "duplicate_and_unresolved_evidence_ids") == "pass", pid


def test_the_stand_in_call_log_is_labelled_as_such_in_every_report():
    for pid, packet in PACKETS.items():
        report = json.loads(packet.items["checks/validator-report.json"])
        boundary = [c for c in report["checks"] if c["check"] == "boundary"][0]
        assert boundary["result"] == "pass" and "STAND-IN" in boundary["detail"], pid