"""DC-8 recorder and output checker (stand-in): a correct output is accepted; wrong outputs are rejected for the stated check."""
import copy
import json
import sys

import pytest

from schema_registry import ROOT, SCHEMAS

sys.path.insert(0, str(ROOT / "tools"))
from assurance.approval_log import lookup  # noqa: E402
from assurance.assemble import assemble  # noqa: E402
from assurance.recorder import Recorder, check_output  # noqa: E402
from assurance.store import CaseStore  # noqa: E402
from assurance.validator import validate  # noqa: E402
from mock_glossary import CAPABILITIES, MockGlossary  # noqa: E402
from reference_definition_agent import reference_agent  # noqa: E402

GLOSSARY = ROOT / "fixtures" / "definition-and-cde" / "glossary.json"
LOG = ROOT / "fixtures" / "assurance" / "approval-log.json"
PRODUCER_SCHEMA = SCHEMAS / "outputs" / "definition-and-cde-agent.output.schema.json"
ROLES = dict(produced_by="SYN Definition & CDE Agent", authored_by="SYN Definition & CDE Agent",
             assembled_by="SYN-ROLE-ASSEMBLER", manifest_approved_by="SYN-ROLE-MANIFEST-APPROVER")
REQUEST = "Compare the definition of 'Settlement Date' across glossary entries GL-101 and GL-204."
TS = "2026-10-28T00:00:00Z"


def world(roles=None, tool_calls=True, approval_for="settlement date"):
    producer = reference_agent(REQUEST, MockGlossary())
    calls = [{"tool": "get_term", "args": {"term_id": "GL-101"}}] if tool_calls else None
    report = validate(producer, PRODUCER_SCHEMA, set(CAPABILITIES.values()), calls)
    extract = lookup(LOG, [approval_for])
    packet = assemble(producer, CaseStore.from_glossary(GLOSSARY), case_id="SYN-CASE-001", pack_id="SYN-PACK-01", request=REQUEST,
                      **{**ROLES, **(roles or {})}, validator_report=report, approval_extract=extract)
    return packet, report, extract


def own_val_record(packet, report):
    item = "checks/validator-report.json"
    ver = {i["path"]: i["version"] for i in packet.manifest["items"]}[item]
    return {"source_id": f"AR-EV-VAL-{report['run_id']}", "source_type": "validator_report", "title": "SYNTHETIC validator report",
            "location": f"{item}@{ver}", "authority_level": "authoritative_internal", "extracted_fact": '"check": "boundary"',
            "direct_or_inferred": "direct", "timestamp": TS}


def clean_output(packet, report, extract, gate="NO_BLOCKING_FINDINGS_IDENTIFIED", assessments=None, findings=None, status=None, reviewed=True):
    m = packet.manifest
    pack = json.loads(packet.items["pack/producer-output.json"])
    claim_ids = [c["claim_id"] for c in pack["handoff"]["claims"]]
    prod_rec = json.loads(packet.items["evidence/GL-101.json"])
    val = own_val_record(packet, report)
    assessments = assessments or {cid: "Supported" for cid in claim_ids}
    findings = findings or []
    status = status or {"NO_BLOCKING_FINDINGS_IDENTIFIED": "completed"}.get(gate, "escalated")
    reviewed_claims = [{"source_claim_id": cid, "producer_claim_assessment": a, "finding_ids": [f["finding_id"] for f in findings if f["source_claim_id"] == cid],
                        "evidence": [prod_rec], "assumption_excerpts": [], "action_required": "HUMAN_ACTION: Data Steward supply_packet_item"} for cid, a in assessments.items()] if reviewed else []
    return {
        "summary": f"Gate {gate}; packs 1 of 1; claims {len(reviewed_claims)} of {len(claim_ids)}; run {report['run_id']}.",
        "gate_recommendation": gate,
        "gate_recommendation_note": "Recommendation only. Not a clearance or approval. Whether a hold blocks progress is not decided (GD-01 open).",
        "coverage": {"packs_in_scope": 1, "packs_reviewed": 1, "claims_in_pack": len(claim_ids), "claims_reviewed": len(reviewed_claims), "sampling_rule_ref": None},
        "manifest_declarations": {k: m[k] for k in ("produced_by", "authored_by", "assembled_by", "manifest_approved_by", "uncited_evidence_ids", "provenance")},
        "deterministic_checks_consumed": [{"check": c["check"], "run_id": report["run_id"], "result": c["result"]} for c in report["checks"]],
        "uncited_evidence_dispositions": [{"evidence_id": i, "disposition": "consistent"} for i in m["uncited_evidence_ids"]],
        "findings": findings, "reviewed_claims": reviewed_claims,
        "boundary_check": "consistent", "approval_check": "consistent",
        "contradictions": [], "evidence_requests": [], "contested_findings": [], "assumptions": [], "open_questions": [], "recommendations": [],
        "human_action_required": [],
        "handoff": {"case_id": m["case_id"], "request": m["request"], "agent": "Assurance Reviewer", "status": status,
                    "findings": [f"AR-{m['case_id']}-{m['pack_id']}-GATE | {gate} | {report['run_id']} | recommendation, not a clearance"],
                    "evidence": [prod_rec, val],
                    "claims": [{"claim_id": "AR-C-GATE", "statement": f"Gate {gate} (recommendation only)", "claim_type": "agent_inference",
                                "confidence": "Partially supported", "evidence_ids": [val["source_id"]]}],
                    "assumptions": [], "open_questions": [], "human_action_required": [], "next_agent": None},
    }


def hold_output(packet, report, extract, excerpt=None):
    m = packet.manifest
    fid = f"AR-{m['case_id']}-{m['pack_id']}-001"
    pack_text = packet.items["pack/producer-output.json"]
    f = {"finding_id": fid, "finding_type": "unsupported", "blocking": True, "source_claim_id": "CL-0001", "evidence_ids": [],
         "locations": ["pack/producer-output.json"], "quoted_excerpt": excerpt if excerpt is not None else '"claim_id": "CL-0001"',
         "action_required": "UNSUPPORTED: CL-0001 unsupported", "contested": False}
    assert f["quoted_excerpt"] in pack_text or excerpt is not None
    return clean_output(packet, report, extract, gate="HOLD_RECOMMENDED", assessments={"CL-0001": "Unsupported"}, findings=[f])


def reasons(verdict, tag):
    return [p for p in verdict.problems if p.startswith(f"({tag})")]


def test_a_correct_clean_output_is_accepted_with_the_open_points_as_warnings():
    packet, report, extract = world()
    v = check_output(clean_output(packet, report, extract), packet, report, extract)
    assert v.accepted, v.problems
    assert v.expected.value == "NO_BLOCKING_FINDINGS_IDENTIFIED" and v.expected.handoff_status == "completed"
    assert any("open point" in w or "not specified" in w or "no closed form" in w for w in v.warnings)


def test_a_correct_hold_output_with_a_genuine_verbatim_excerpt_is_accepted():
    packet, report, extract = world()
    v = check_output(hold_output(packet, report, extract), packet, report, extract)
    assert v.accepted, v.problems
    assert v.expected.value == "HOLD_RECOMMENDED"


@pytest.mark.parametrize("mutation,tag", [
    (lambda o: o.update(gate_recommendation="HOLD_RECOMMENDED"), "a"),                                   # wrong gate for a clean pack
    (lambda o: o["handoff"].update(status="blocked"), "a"),                                              # blocked is never emitted
    (lambda o: o["handoff"].update(status="in_progress"), "a"),                                          # wrong status
    (lambda o: o["handoff"]["claims"][0].update(statement="Gate HOLD_RECOMMENDED (recommendation only)"), "a"),
    (lambda o: o["boundary_check"].__class__ and o.update(boundary_check="breach"), "a"),               # does not match the validator report
    (lambda o: o["coverage"].update(claims_reviewed=9), "a"),
])
def test_wrong_gate_status_or_counts_are_rejected_by_check_a(mutation, tag):
    packet, report, extract = world()
    out = clean_output(packet, report, extract)
    mutation(out)
    v = check_output(out, packet, report, extract)
    assert not v.accepted and reasons(v, tag), v.problems


def test_a_blocking_flag_that_disagrees_with_the_rank_2_test_is_rejected():
    packet, report, extract = world()
    out = hold_output(packet, report, extract)
    out["findings"][0]["blocking"] = False
    assert reasons(check_output(out, packet, report, extract), "a")


def test_a_clean_gate_over_an_unsupported_claim_is_rejected():
    packet, report, extract = world()
    out = clean_output(packet, report, extract, assessments={"CL-0001": "Unsupported"})
    assert reasons(check_output(out, packet, report, extract), "a")


def test_reviewed_claim_set_must_equal_the_pack_claim_set_check_b():
    packet, report, extract = world()
    omitted = clean_output(packet, report, extract, assessments={})
    omitted["reviewed_claims"] = []
    omitted["coverage"]["claims_reviewed"] = 0
    assert reasons(check_output(omitted, packet, report, extract), "b")
    extra = clean_output(packet, report, extract, assessments={"CL-0001": "Supported", "CL-9999": "Supported"})
    extra["coverage"]["claims_reviewed"] = 2
    assert reasons(check_output(extra, packet, report, extract), "b")


def test_a_restated_claim_text_is_rejected_because_the_schema_has_no_such_field():
    packet, report, extract = world()
    out = clean_output(packet, report, extract)
    out["reviewed_claims"][0]["claim_text"] = "restated"
    assert reasons(check_output(out, packet, report, extract), "e")


def test_duplicate_ids_and_unresolved_cited_ids_are_rejected_check_c():
    packet, report, extract = world()
    out = clean_output(packet, report, extract)
    out["handoff"]["evidence"].append(copy.deepcopy(out["handoff"]["evidence"][1]))
    assert reasons(check_output(out, packet, report, extract), "c")
    out2 = clean_output(packet, report, extract)
    out2["handoff"]["claims"][0]["evidence_ids"].append("AR-EV-NOPE")
    assert reasons(check_output(out2, packet, report, extract), "c")


def test_a_finding_id_without_the_case_and_pack_prefix_is_rejected():
    packet, report, extract = world()
    out = hold_output(packet, report, extract)
    out["findings"][0]["finding_id"] = "AR-OTHER-OTHER-001"
    assert reasons(check_output(out, packet, report, extract), "c")


@pytest.mark.parametrize("change", [
    lambda r: r.update(extracted_fact='"check": "boundary" and a corrected definition'),   # appended wording
    lambda r: r.update(extracted_fact='"check":  "boundary"'),                              # double space: not verbatim
    lambda r: r.update(location="checks/validator-report.json@000000000000"),               # wrong version
    lambda r: r.update(location="checks/not-in-the-packet.json@abcdef123456"),              # item not in the packet
])
def test_fabricated_or_non_verbatim_own_evidence_is_rejected_check_d(change):
    packet, report, extract = world()
    out = clean_output(packet, report, extract)
    change(out["handoff"]["evidence"][1])
    assert reasons(check_output(out, packet, report, extract), "d")


def test_a_quoted_excerpt_must_occur_verbatim_at_a_stated_location():
    packet, report, extract = world()
    out = hold_output(packet, report, extract, excerpt="a sentence the pack never contains")
    assert reasons(check_output(out, packet, report, extract), "d")


def test_an_altered_producer_record_is_rejected():
    packet, report, extract = world()
    out = clean_output(packet, report, extract)
    out["handoff"]["evidence"][0]["extracted_fact"] = "improved wording"
    assert reasons(check_output(out, packet, report, extract), "d")


def _absent_record(extract, key):
    return {"source_id": "AR-EV-ABSENT-1", "source_type": "approval_log_lookup", "title": "SYNTHETIC absence record", "location": "checks/approval-log-extract.json",
            "authority_level": "authoritative_internal", "extracted_fact": f"no entry matching {key} in extract {extract['run_id']}",
            "direct_or_inferred": "direct", "timestamp": TS}


def test_an_absence_record_is_accepted_only_when_the_lookup_rerun_agrees():
    packet, report, extract = world(approval_for="notional adjustment factor")  # a genuinely empty extract
    out = clean_output(packet, report, extract)
    out["handoff"]["evidence"].append(_absent_record(extract, "settlement date"))
    assert not reasons(check_output(out, packet, report, extract), "d")
    packet2, report2, extract2 = world()                                         # an extract that DOES hold a settlement date entry
    liar = clean_output(packet2, report2, extract2)
    liar["handoff"]["evidence"].append(_absent_record(extract2, "settlement date"))
    assert any("lookup re-run finds an entry" in p for p in check_output(liar, packet2, report2, extract2).problems)
    reworded = clean_output(packet, report, extract)
    reworded["handoff"]["evidence"].append({**_absent_record(extract, "x"), "extracted_fact": "the approval is not on record"})
    assert any("fixed sentence" in p for p in check_output(reworded, packet, report, extract).problems)


def test_a_paraphrased_assumption_excerpt_is_rejected_but_a_verbatim_one_is_accepted():
    packet, report, extract = world()
    out = clean_output(packet, report, extract)
    out["reviewed_claims"][0]["assumption_excerpts"] = ["an improved paraphrase of the pack"]
    assert reasons(check_output(out, packet, report, extract), "e")
    out2 = clean_output(packet, report, extract)
    out2["reviewed_claims"][0]["assumption_excerpts"] = ['"claim_id": "CL-0001"']
    assert check_output(out2, packet, report, extract).accepted


def test_a_stop_condition_forces_incomplete_with_no_content_review_and_rejects_a_content_review():
    packet, report, extract = world(roles={"assembled_by": "SYN Definition & CDE Agent"})
    stop = clean_output(packet, report, extract, gate="INCOMPLETE", reviewed=False)
    v = check_output(stop, packet, report, extract)
    assert v.accepted, v.problems
    assert v.expected.rank == 1 and v.expected.handoff_status == "escalated"
    reviewed_anyway = hold_output(packet, report, extract)
    assert not check_output(reviewed_anyway, packet, report, extract).accepted


def test_a_missing_boundary_log_makes_the_gate_incomplete_and_a_clean_gate_is_rejected():
    packet, report, extract = world(tool_calls=False)
    clean = clean_output(packet, report, extract)
    assert reasons(check_output(clean, packet, report, extract), "a")
    right = clean_output(packet, report, extract, gate="INCOMPLETE")
    right["boundary_check"] = "unable_to_determine"
    assert check_output(right, packet, report, extract).accepted


def test_a_producer_record_with_the_reserved_prefix_without_a_collision_finding_is_rejected():
    packet, report, extract = world()
    packet.manifest["items"].append({"path": "evidence/AR-EV-CLAUSE-1.json", "version": "abc"})
    packet.items["evidence/AR-EV-CLAUSE-1.json"] = "{}"
    assert reasons(check_output(clean_output(packet, report, extract), packet, report, extract), "c")


def test_summary_template_and_free_strings_are_warnings_not_rejections():
    packet, report, extract = world()
    out = clean_output(packet, report, extract)
    out["summary"] = "A readable sentence that does not start with the gate."
    v = check_output(out, packet, report, extract)
    assert v.accepted and any("summary" in w for w in v.warnings)


# ---- (f) and (g): the recorder -------------------------------------------------------------------------------------------------

def test_only_accepted_outputs_are_recorded_and_each_review_links_to_the_prior_record(tmp_path):
    packet, report, extract = world()
    rec = Recorder(tmp_path / "log.jsonl")
    bad = clean_output(packet, report, extract, gate="HOLD_RECOMMENDED")
    with pytest.raises(ValueError):
        rec.append_review(bad, check_output(bad, packet, report, extract), packet.manifest, report["run_id"])
    assert rec.records() == []
    hold = hold_output(packet, report, extract)
    r1 = rec.append_review(hold, check_output(hold, packet, report, extract), packet.manifest, report["run_id"])
    clean = clean_output(packet, report, extract)
    r2 = rec.append_review(clean, check_output(clean, packet, report, extract), packet.manifest, report["run_id"])
    assert (r1["seq"], r1["prior_record_seq"], r2["seq"], r2["prior_record_seq"]) == (1, None, 2, 1)


def test_a_later_clean_review_never_closes_an_earlier_hold_only_a_human_resolution_does(tmp_path):
    packet, report, extract = world()
    rec = Recorder(tmp_path / "log.jsonl")
    hold = hold_output(packet, report, extract)
    rec.append_review(hold, check_output(hold, packet, report, extract), packet.manifest, report["run_id"])
    before = (tmp_path / "log.jsonl").read_bytes()
    clean = clean_output(packet, report, extract)
    rec.append_review(clean, check_output(clean, packet, report, extract), packet.manifest, report["run_id"])
    assert (tmp_path / "log.jsonl").read_bytes().startswith(before), "an earlier record was altered"
    assert len(rec.open_holds("SYN-CASE-001", "SYN-PACK-01")) == 1
    fid = hold["findings"][0]["finding_id"]
    for role in ("Data Steward", "Deputy", "Assurance Reviewer", ""):
        with pytest.raises(PermissionError):
            rec.record_human_resolution(authenticated_role=role, owner_name="n", case_id="SYN-CASE-001", pack_id="SYN-PACK-01", finding_id=fid, reason="r", date="2026-10-28")
    with pytest.raises(ValueError):
        rec.record_human_resolution(authenticated_role="Project Owner", owner_name="", case_id="SYN-CASE-001", pack_id="SYN-PACK-01", finding_id=fid, reason="r", date="2026-10-28")
    rec.record_human_resolution(authenticated_role="Project Owner", owner_name="SYN Owner", case_id="SYN-CASE-001", pack_id="SYN-PACK-01", finding_id=fid, reason="synthetic", date="2026-10-28")
    assert rec.open_holds("SYN-CASE-001", "SYN-PACK-01") == []


def test_the_recorder_has_no_way_to_approve_clear_update_delete_or_supersede():
    forbidden = ("approve", "clear", "pass", "update", "delete", "remove", "supersede", "overwrite", "set_", "resolve_hold", "close")
    names = [n for n in dir(Recorder) if not n.startswith("_")]
    assert not [n for n in names if any(f in n for f in forbidden)], names
    assert set(names) == {"ALLOWED_VALUES", "append_review", "open_holds", "record_human_resolution", "records"}


def test_a_record_never_carries_an_approved_cleared_or_passed_state(tmp_path):
    packet, report, extract = world()
    rec = Recorder(tmp_path / "log.jsonl")
    clean = clean_output(packet, report, extract)
    r = rec.append_review(clean, check_output(clean, packet, report, extract), packet.manifest, report["run_id"])
    text = json.dumps(r).lower()
    assert "approved" not in text and "cleared" not in text and "passed" not in text
    assert r["assurance_gate_recommendation"] in Recorder.ALLOWED_VALUES