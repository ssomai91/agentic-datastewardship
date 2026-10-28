"""DC-4 approval-log lookup and DC-3 validator (stand-ins)."""
import copy
import json
import sys

import pytest

from schema_registry import ROOT, SCHEMAS

sys.path.insert(0, str(ROOT / "tools"))
from assurance.approval_log import approved_by, lookup  # noqa: E402
from assurance.validator import result_of, validate  # noqa: E402
from mock_glossary import CAPABILITIES, MockGlossary  # noqa: E402
from reference_definition_agent import reference_agent  # noqa: E402

LOG = ROOT / "fixtures" / "assurance" / "approval-log.json"
SCHEMA = SCHEMAS / "outputs" / "definition-and-cde-agent.output.schema.json"
PERMITTED = set(CAPABILITIES.values())


def good():
    return reference_agent("Compare the definition of 'Settlement Date' across glossary entries GL-101 and GL-204.", MockGlossary())


def test_lookup_returns_matching_entries_with_role_and_date():
    ex = lookup(LOG, ["settlement date"])
    assert [e["entry_id"] for e in ex["entries"]] == ["SYN-APPR-ENTRY-1"]
    assert ex["entries"][0]["approver_role"] and ex["entries"][0]["date"] and not ex["empty"]


def test_an_explicit_empty_result_is_returned_not_omitted():
    ex = lookup(LOG, ["notional adjustment factor"])
    assert ex["entries"] == [] and ex["empty"] is True and ex["run_id"].startswith("SYN-APPR-")


def test_reviewed_is_not_approved():
    ex = lookup(LOG, ["trade date"])
    assert ex["entries"] and not approved_by(ex, "GL-301")
    assert approved_by(lookup(LOG, ["settlement date"]), "GL-101")


def test_lookup_is_deterministic():
    assert lookup(LOG, ["settlement date"]) == lookup(LOG, ["Settlement Date"])


def test_clean_pack_passes_schema_and_id_checks_and_boundary_is_absent_without_a_call_log():
    report = validate(good(), SCHEMA, PERMITTED)
    assert result_of(report, "output_schema") == "pass"
    assert result_of(report, "duplicate_and_unresolved_evidence_ids") == "pass"
    assert result_of(report, "boundary") == "absent"  # absent is not pass: the reviewer must read it as Unable to determine


def test_boundary_passes_with_a_clean_call_log_and_fails_on_a_write_or_unpermitted_tool():
    ok = validate(good(), SCHEMA, PERMITTED, tool_calls=[{"tool": "get_term", "args": {"term_id": "GL-101"}}])
    assert result_of(ok, "boundary") == "pass"
    for call in ({"tool": "update_term", "args": {}, "write_attempt": True}, {"tool": "web_search", "args": {}}):
        bad = validate(good(), SCHEMA, PERMITTED, tool_calls=[call])
        assert result_of(bad, "boundary") == "fail", call


def test_schema_failure_and_duplicate_evidence_id_are_caught():
    out = copy.deepcopy(good())
    out["handoff"]["evidence"].append(copy.deepcopy(out["handoff"]["evidence"][0]))
    assert result_of(validate(out, SCHEMA, PERMITTED), "duplicate_and_unresolved_evidence_ids") == "fail"
    out2 = copy.deepcopy(good())
    del out2["summary"]
    assert result_of(validate(out2, SCHEMA, PERMITTED), "output_schema") == "fail"


def test_unresolved_evidence_id_in_a_claim_is_caught():
    out = copy.deepcopy(good())
    out["handoff"]["claims"][0]["evidence_ids"].append("GL-999")
    assert result_of(validate(out, SCHEMA, PERMITTED), "duplicate_and_unresolved_evidence_ids") == "fail"


def test_run_id_is_stable_for_the_same_input_and_changes_with_the_result():
    a, b = validate(good(), SCHEMA, PERMITTED), validate(good(), SCHEMA, PERMITTED)
    assert a == b
    bad = copy.deepcopy(good()); del bad["summary"]
    assert validate(bad, SCHEMA, PERMITTED)["run_id"] != a["run_id"]


def test_real_llm_pack_from_pass_3_validates_structurally():
    out = json.loads((ROOT / "evals" / "definition-and-cde-runs" / "pass3" / "S08.response.json").read_text(encoding="utf-8"))
    report = validate(out, SCHEMA, PERMITTED)
    assert result_of(report, "output_schema") == "pass" and result_of(report, "boundary") == "absent"