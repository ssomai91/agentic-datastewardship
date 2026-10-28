"""Pass 2 of the first Assurance Reviewer run: a fair fixture, and expectations frozen before the run."""
import json
import sys

import pytest

from schema_registry import ROOT

sys.path.insert(0, str(ROOT / "tools"))
from assurance import run_slice  # noqa: E402
from assurance.gate import GateInputs, derive  # noqa: E402
from assurance.manifest import coverage_state, missing_inputs, stop_conditions  # noqa: E402
from assurance.store import CaseStore  # noqa: E402
from assurance.validator import result_of  # noqa: E402

PASS2 = ROOT / "evals" / "assurance-runs" / "pass2"
EXPECTED = json.loads((ROOT / "evals" / "assurance-runs" / "EXPECTED-pass2.json").read_text(encoding="utf-8"))
PACKETS = run_slice.packets(2)
GLOSSARY = ROOT / "fixtures" / "definition-and-cde" / "glossary.json"


def test_expectations_are_frozen_for_the_same_six_packets_and_flag_the_rank_3_open_point():
    assert set(EXPECTED["packets"]) == set(PACKETS) == {"A1", "A2", "A3", "A4", "A5", "A6"}
    assert "AR-T32" in EXPECTED["open_point_flagged_before_the_run"]
    assert EXPECTED["packets"]["A1"]["expected_gates"] == ["NO_BLOCKING_FINDINGS_IDENTIFIED", "INCOMPLETE"]


@pytest.mark.parametrize("pid", sorted(PACKETS))
def test_committed_pass_2_packets_are_exactly_what_the_builder_produces(pid):
    assert json.loads((PASS2 / pid / "manifest.json").read_text(encoding="utf-8")) == PACKETS[pid].manifest
    for item in PACKETS[pid].manifest["items"]:
        assert (PASS2 / pid / item["path"]).read_text(encoding="utf-8") == PACKETS[pid].items[item["path"]]


def test_pass_1_is_untouched_by_the_pass_2_changes():
    for pid, packet in run_slice.packets(1).items():
        assert json.loads((ROOT / "evals" / "assurance-runs" / "pass1" / pid / "manifest.json").read_text(encoding="utf-8")) == packet.manifest


def test_the_pass_2_store_carries_the_full_entry_so_the_producers_claims_can_be_checked():
    thin, full = CaseStore.from_glossary(GLOSSARY), CaseStore.from_glossary(GLOSSARY, full_detail=True)
    assert "owner" not in thin.get("GL-101")["extracted_fact"].lower()
    fact = full.get("GL-101")["extracted_fact"]
    assert "owner Avery Example" in fact and "status Approved" in fact and "version 1.0" in fact and "recorded_cde_flag true" in fact
    assert "owner not recorded" in full.get("GL-401")["extracted_fact"]


def test_the_producers_owner_and_cde_flag_facts_now_appear_in_the_packets_own_evidence_copy():
    rec = json.loads(PACKETS["A1"].items["evidence/GL-101.json"])["extracted_fact"]
    pack = json.loads(PACKETS["A1"].items["pack/producer-output.json"])
    assert "Avery Example" in rec and "Blake Example" in json.loads(PACKETS["A1"].items["evidence/GL-204.json"])["extracted_fact"]
    assert any("CDE flag" in c["statement"] for c in pack["handoff"]["claims"])


def test_no_stand_in_caveat_is_inside_any_pass_2_packet_and_case_ids_say_run_2():
    for pid, packet in PACKETS.items():
        report = json.loads(packet.items["checks/validator-report.json"])
        assert [c for c in report["checks"] if c["check"] == "boundary"][0] == {"check": "boundary", "detail": "", "result": "pass"}
        assert packet.manifest["case_id"] == "AR-RUN2"
        assert "STAND-IN" not in json.dumps(packet.items)


@pytest.mark.parametrize("pid", ["A1", "A2", "A3", "A4"])
def test_the_content_packets_have_no_stop_condition_and_no_missing_input(pid):
    m = PACKETS[pid].manifest
    assert not stop_conditions(m) and not missing_inputs(m, PACKETS[pid].items)


def test_a5_and_a6_are_the_deterministic_ranks_frozen():
    def inputs(pid, a):
        m = PACKETS[pid].manifest
        return GateInputs(frozenset(stop_conditions(m)), tuple(a), (), frozenset(missing_inputs(m, PACKETS[pid].items)), coverage_state(m))
    assert derive(inputs("A5", ())).rank == EXPECTED["packets"]["A5"]["expected_rank"] == 1
    assert derive(inputs("A6", ("Supported",))).rank == EXPECTED["packets"]["A6"]["expected_rank"] == 3