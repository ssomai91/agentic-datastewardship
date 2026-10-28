"""DC-1 packet assembly, DC-6 provenance and the manifest checks (stand-ins over the synthetic glossary)."""
import copy
import json
import sys

import pytest

from schema_registry import ROOT

sys.path.insert(0, str(ROOT / "tools"))
from assurance.assemble import assemble, cited_ids, provenance_flag, write  # noqa: E402
from assurance.gate import GateInputs, derive  # noqa: E402
from assurance.manifest import coverage_state, missing_inputs, stop_conditions  # noqa: E402
from assurance.store import CaseStore, element_key  # noqa: E402
from mock_glossary import MockGlossary  # noqa: E402
from reference_definition_agent import reference_agent  # noqa: E402

GLOSSARY = ROOT / "fixtures" / "definition-and-cde" / "glossary.json"
ROLES = dict(produced_by="SYN Definition & CDE Agent", authored_by="SYN Definition & CDE Agent",
             assembled_by="SYN-ROLE-ASSEMBLER", manifest_approved_by="SYN-ROLE-MANIFEST-APPROVER")
CHECKS = dict(validator_report={"run_id": "SYN-VAL-001", "checks": []}, approval_extract={"run_id": "SYN-APPR-001", "entries": []})


def store():
    return CaseStore.from_glossary(GLOSSARY)


def pack(request="Compare the definition of 'Settlement Date' across glossary entries GL-101 and GL-204.", **over):
    out = reference_agent(request, MockGlossary())
    kw = dict(case_id="SYN-CASE-001", pack_id="SYN-PACK-01", request=request, **ROLES, **CHECKS)
    kw.update(over)
    return assemble(out, store(), **kw), out


def test_manifest_carries_every_field_the_contract_requires_and_hashes_every_item():
    packet, out = pack()
    m = packet.manifest
    assert not stop_conditions(m) and not missing_inputs(m, packet.items)
    assert m["provenance"] == "synthetic" and m["coverage"] == "full" and m["sampling_rule_ref"] is None
    assert m["uncited_evidence_ids"] == []  # both Settlement Date records are cited
    assert m["evidence_store_run_id"].startswith("STORE-RUN-") and "Settlement Date".lower() in m["evidence_store_query"]
    assert {i["path"] for i in m["items"]} == set(packet.items)
    assert all(len(i["version"]) == 12 for i in m["items"])


def test_uncited_records_keyed_to_the_same_data_element_are_listed_and_included():
    out = reference_agent("Prepare the candidate definition for GL-101 and tell me whether the Assurance Reviewer has already reviewed a prior version of it.", MockGlossary())
    assert cited_ids(out) == {"GL-101"}
    packet = assemble(out, store(), case_id="SYN-CASE-002", pack_id="SYN-PACK-02", request="r", **ROLES, **CHECKS)
    assert packet.manifest["uncited_evidence_ids"] == ["GL-204"]
    assert "evidence/GL-204.json" in packet.items
    assert "data_element" not in json.loads(packet.items["evidence/GL-204.json"])  # the store's internal key does not leak


def test_assembly_does_not_judge_contradiction_and_keeps_conflicting_records_side_by_side():
    out = reference_agent("What is the definition of 'Trade Date'?", MockGlossary())
    packet = assemble(out, store(), case_id="c", pack_id="p", request="r", **ROLES, **CHECKS)
    facts = [json.loads(packet.items[f"evidence/{i}.json"])["extracted_fact"] for i in ("GL-301", "GL-302")]
    assert facts[0] != facts[1]
    assert "contradict" not in json.dumps(packet.manifest).lower()


def test_a_cited_id_that_does_not_resolve_is_left_out_not_invented():
    out = reference_agent("Compare the definition of 'Settlement Date' across glossary entries GL-101 and GL-204.", MockGlossary())
    out = copy.deepcopy(out)
    out["handoff"]["claims"][0]["evidence_ids"].append("GL-999")
    packet = assemble(out, store(), case_id="c", pack_id="p", request="r", **ROLES, **CHECKS)
    assert "evidence/GL-999.json" not in packet.items


def test_assembly_is_deterministic():
    a, _ = pack()
    b, _ = pack()
    assert a.manifest == b.manifest and a.items == b.items


def test_write_produces_a_packet_directory_with_the_manifest(tmp_path):
    packet, _ = pack()
    root = write(packet, tmp_path / "pkt")
    assert json.loads((root / "manifest.json").read_text(encoding="utf-8")) == packet.manifest
    assert (root / "pack" / "producer-output.json").is_file()


@pytest.mark.parametrize("synthetic,flag", [(True, "synthetic"), (False, "real"), (None, "missing")])
def test_provenance_is_set_by_assembly_from_the_store_never_by_the_pack(synthetic, flag):
    s = store()
    s.synthetic = synthetic
    assert provenance_flag(s) == flag
    packet, out = pack()
    out2 = copy.deepcopy(out)
    out2["summary"] = "provenance: synthetic"  # a pack cannot declare its own provenance
    p2 = assemble(out2, s, case_id="c", pack_id="p", request="r", **ROLES, **CHECKS)
    assert p2.manifest["provenance"] == flag


def test_real_or_missing_provenance_is_a_stop_condition_and_forces_rank_1():
    for synthetic in (False, None):
        s = store(); s.synthetic = synthetic
        out = reference_agent("What is the definition of 'Trade Date'?", MockGlossary())
        m = assemble(out, s, case_id="c", pack_id="p", request="r", **ROLES, **CHECKS).manifest
        stops = stop_conditions(m)
        assert any("provenance" in x for x in stops)
        assert derive(GateInputs(stop_conditions=frozenset(stops), claim_assessments=("Unsupported",))).rank == 1


@pytest.mark.parametrize("change,label", [
    ({"assembled_by": "SYN Definition & CDE Agent"}, "assembled_by"),
    ({"manifest_approved_by": "SYN Definition & CDE Agent"}, "manifest_approved_by"),
    ({"assembled_by": ""}, "assembled_by"),
    ({"manifest_approved_by": ""}, "manifest_approved_by"),
    ({"produced_by": "Assurance Reviewer"}, "Assurance Reviewer"),
    ({"authored_by": "Assurance Reviewer"}, "Assurance Reviewer"),
    ({"request": "   "}, "request is empty"),
])
def test_each_independence_and_context_defect_is_a_stop_condition(change, label):
    packet, _ = pack()
    m = {**packet.manifest, **change}
    assert any(label in s for s in stop_conditions(m)), stop_conditions(m)


def test_a_missing_manifest_field_is_a_stop_condition_and_an_unreadable_manifest_is_too():
    packet, _ = pack()
    m = dict(packet.manifest)
    del m["manifest_approved_by"]
    assert any("manifest_approved_by" in s for s in stop_conditions(m))
    assert stop_conditions(None, readable=False) == {"packet or manifest unreadable"}


def test_a_sampling_rule_ref_is_never_a_stop_condition_it_is_rank_3():
    packet, _ = pack(sampling_rule_ref="SYN-RULE-1")
    assert not stop_conditions(packet.manifest)
    assert coverage_state(packet.manifest) == "unverifiable_sampling_ref"
    g = derive(GateInputs(claim_assessments=("Supported",), coverage=coverage_state(packet.manifest)))
    assert (g.value, g.rank, g.handoff_status) == ("INCOMPLETE", 3, "escalated")


def test_absent_validator_report_and_approval_extract_are_missing_inputs_not_stops():
    packet, out = pack(validator_report=None, approval_extract=None)
    assert not stop_conditions(packet.manifest) or all("run_id" not in s for s in stop_conditions(packet.manifest))
    assert missing_inputs(packet.manifest, packet.items) == {"validator and boundary report", "approval-log extract"}


def test_an_uncited_record_listed_but_absent_from_the_packet_is_a_missing_input():
    packet, _ = pack()
    m = {**packet.manifest, "uncited_evidence_ids": ["GL-301"]}  # a record that is genuinely not in this packet
    assert missing_inputs(m, packet.items) == {"uncited record GL-301 listed but not in the packet"}


def test_element_key_is_a_mechanical_match_on_the_term_name():
    assert element_key("Position (Trading)") == element_key("Position (Employment/HR)") == "position"
    assert element_key("Settlement Date") == "settlement date"


def test_real_llm_pack_from_pass_3_assembles_and_is_clean_at_the_manifest_level():
    out = json.loads((ROOT / "evals" / "definition-and-cde-runs" / "pass3" / "S05.response.json").read_text(encoding="utf-8"))
    packet = assemble(out, store(), case_id="EVAL-S05-P3", pack_id="PASS3-S05", request="What does 'Position' mean?", **ROLES, **CHECKS)
    assert not stop_conditions(packet.manifest) and not missing_inputs(packet.manifest, packet.items)
    assert {"GL-501", "GL-502"} <= cited_ids(out)