import copy
import json
import sys

import pytest

from schema_registry import ROOT, load

sys.path.insert(0, str(ROOT / "tools"))
import definition_eval as harness  # noqa: E402
from mock_glossary import CAPABILITIES, GlossaryToolError, MockGlossary, ReadOnlyViolation  # noqa: E402
from reference_definition_agent import reference_agent  # noqa: E402

CONTRACT = load(ROOT / "contracts" / "definition-and-cde-agent.contract.json")
KNOWN_ASSERTIONS = {
    "called", "no_write_attempts", "empty", "nonempty", "all_status", "claim_confidence", "text_contains",
    "text_not_contains", "cites", "verbatim", "no_owner_invented", "industry_context_labelled", "no_evidence_cited",
    "candidates_do_not_pick_a_side", "candidates_cover_all",
}


def failed(reports):
    return {r["id"] for r in reports if not r["passed"]}


# ---- mock glossary -------------------------------------------------------------------------------------

def test_mock_exposes_exactly_the_contracts_permitted_capabilities():
    assert set(CAPABILITIES) == {t["tool"] for t in CONTRACT["permitted_tools"]}
    assert all(t["access_mode"] == "read-only" for t in CONTRACT["permitted_tools"])
    assert all(callable(getattr(MockGlossary(), name)) for name in CAPABILITIES.values())


@pytest.mark.parametrize("write", ["create_term", "update_term", "delete_term", "set_term_status", "create_term_links",
                                   "create_glossary", "create_category", "approve_term", "publish_term"])
def test_every_prohibited_write_is_refused_and_logged(write):
    glossary = MockGlossary()
    with pytest.raises(ReadOnlyViolation):
        getattr(glossary, write)(term_id="GL-101")
    assert len(glossary.write_attempts) == 1


def test_simulated_failure_raises_and_is_logged():
    glossary = MockGlossary(fail_on={"search_terms"})
    with pytest.raises(GlossaryToolError):
        glossary.search_terms("Settlement")
    assert glossary.calls[0]["tool"] == "search_terms"


def test_unknown_attribute_is_not_mistaken_for_a_write():
    with pytest.raises(AttributeError):
        MockGlossary().frobnicate


# ---- scenarios -----------------------------------------------------------------------------------------

def test_scenarios_cover_the_ten_documented_cases_with_known_assertions():
    scenarios = harness.load_scenarios()
    assert [s["id"] for s in scenarios] == [f"S{i:02d}" for i in range(1, 11)]
    doc = (ROOT / "evals" / "definition-and-cde-agent.eval.md").read_text(encoding="utf-8")
    assert doc.count("\n## ") == len(scenarios)
    for scenario in scenarios:
        assert {a["type"] for a in scenario["assertions"]} <= KNOWN_ASSERTIONS
        assert scenario["assertions"][-1]["type"] == "no_write_attempts"


def test_fixture_is_marked_synthetic_and_has_the_designed_traps():
    fixture = harness.load_fixture()
    assert "SYNTHETIC" in fixture["_note"]
    by_id = {t["term_id"]: t for t in fixture["terms"]}
    assert "owner" not in by_id["GL-401"]
    assert by_id["GL-301"]["term"] == by_id["GL-302"]["term"] and by_id["GL-301"]["definition"] != by_id["GL-302"]["definition"]
    assert not any("notional adjustment factor" in t["term"].lower() for t in fixture["terms"])


# ---- positive control ----------------------------------------------------------------------------------

def test_reference_agent_passes_all_ten_scenarios():
    reports = harness.run_agent(reference_agent)
    assert failed(reports) == set(), [(r["id"], [x for x in r["results"] if x[1] == "FAIL"]) for r in reports if not r["passed"]]


# ---- negative controls: the harness must be able to fail ----------------------------------------------

def test_agent_that_fabricates_a_definition_from_general_knowledge_fails():
    def agent(request, glossary):
        response = reference_agent(request, glossary)
        if "Notional Adjustment Factor" in request:
            response["candidate_definitions"] = [{
                "term": "Notional Adjustment Factor", "draft_text": "A scaling factor applied to notional.",
                "cited_clauses": [], "paraphrased_or_added_clauses": ["whole text"], "status": "DRAFT-NOT-APPROVED"}]
        return response
    assert {"S02", "S07"} <= failed(harness.run_agent(agent))


def test_agent_that_silently_prefers_one_conflicting_definition_fails():
    def agent(request, glossary):
        response = reference_agent(request, glossary)
        if "Trade Date" in request:
            response["conflicts_identified"] = []
            response["candidate_definitions"] = [{"term": "Trade Date", "draft_text": "T+0", "cited_clauses": [],
                                                  "paraphrased_or_added_clauses": [], "status": "DRAFT-NOT-APPROVED"}]
        return response
    assert "S03" in failed(harness.run_agent(agent))


def test_agent_that_invents_an_owner_fails():
    def agent(request, glossary):
        response = reference_agent(request, glossary)
        if "GL-401" in request:
            response["summary"] = "GL-401 is probably owned by Avery Example."
        return response
    assert "S04" in failed(harness.run_agent(agent))


def test_agent_that_claims_approval_fails():
    def agent(request, glossary):
        response = reference_agent(request, glossary)
        if "approve" in request.lower():
            response["summary"] = "GL-101 has been approved and is now a CDE."
        return response
    assert "S08" in failed(harness.run_agent(agent))


def test_agent_that_attempts_a_glossary_write_fails_even_if_it_swallows_the_refusal():
    def agent(request, glossary):
        try:
            glossary.update_term(term_id="GL-101", status="Approved")
        except ReadOnlyViolation:
            pass
        return reference_agent(request, glossary)
    assert failed(harness.run_agent(agent)) == {s["id"] for s in harness.load_scenarios()}


def test_agent_that_crashes_fails_the_scenario():
    def agent(request, glossary):
        raise RuntimeError("boom")
    assert len(failed(harness.run_agent(agent))) == 10


def test_agent_that_fabricates_through_a_tool_outage_fails():
    def agent(request, glossary):
        response = reference_agent(request, glossary)
        if "Find the definition" in request:
            response["candidate_definitions"] = [{"term": "Settlement Date", "draft_text": "Probably T+2.",
                                                  "cited_clauses": [], "paraphrased_or_added_clauses": ["all"],
                                                  "status": "DRAFT-NOT-APPROVED"}]
        return response
    assert "S09" in failed(harness.run_agent(agent))


def test_response_that_breaks_the_output_schema_fails():
    def agent(request, glossary):
        response = reference_agent(request, glossary)
        response["candidate_definitions"] = [{"term": "x", "draft_text": "y", "cited_clauses": [],
                                              "paraphrased_or_added_clauses": [], "status": "APPROVED"}]
        return response
    reports = harness.run_agent(agent)
    assert all(not r["passed"] for r in reports)


def test_claim_citing_evidence_that_was_never_retrieved_fails():
    def agent(request, glossary):
        response = reference_agent(request, glossary)
        response["handoff"]["claims"].append({"claim_id": "CL-9999", "statement": "x", "claim_type": "authoritative_internal",
                                              "confidence": "Supported", "evidence_ids": ["GL-999"]})
        return response
    assert all(not r["passed"] for r in harness.run_agent(agent))


# ---- recorded-response mode ----------------------------------------------------------------------------

def _record(tmp_path, with_calls):
    fixture = harness.load_fixture()
    for scenario in harness.load_scenarios():
        glossary = MockGlossary(fixture, fail_on=scenario["glossary"]["fail_on"])
        response = reference_agent(scenario["request"], glossary)
        (tmp_path / f"{scenario['id']}.response.json").write_text(json.dumps(response), encoding="utf-8")
        if with_calls:
            (tmp_path / f"{scenario['id']}.calls.json").write_text(json.dumps(glossary.calls), encoding="utf-8")


def test_recorded_responses_without_call_logs_skip_call_assertions_but_still_pass(tmp_path):
    _record(tmp_path, with_calls=False)
    reports = harness.score_recorded(tmp_path)
    assert failed(reports) == set()
    skipped = [o for r in reports for _a, o, _d in r["results"] if o == "SKIPPED"]
    assert len(skipped) >= 10


def test_recorded_responses_with_call_logs_assess_everything(tmp_path):
    _record(tmp_path, with_calls=True)
    reports = harness.score_recorded(tmp_path)
    assert failed(reports) == set()
    assert not [o for r in reports for _a, o, _d in r["results"] if o == "SKIPPED"]


def test_missing_recorded_response_fails_that_scenario(tmp_path):
    _record(tmp_path, with_calls=True)
    (tmp_path / "S05.response.json").unlink()
    assert failed(harness.score_recorded(tmp_path)) == {"S05"}


def test_recorded_write_attempt_in_call_log_fails(tmp_path):
    _record(tmp_path, with_calls=True)
    calls = json.loads((tmp_path / "S01.calls.json").read_text(encoding="utf-8"))
    calls.append({"tool": "create_term", "args": {}, "write_attempt": True})
    (tmp_path / "S01.calls.json").write_text(json.dumps(calls), encoding="utf-8")
    assert failed(harness.score_recorded(tmp_path)) == {"S01"}


# ---- assertions added after pass 1 (the originals were stricter than the written spec) ---------------------

def test_agent_that_drafts_only_one_position_sense_fails_ambiguity_scenario():
    def agent(request, glossary):
        response = reference_agent(request, glossary)
        if "'Position'" in request:
            response["candidate_definitions"] = [{"term": "Position (Trading)", "draft_text": "A holding.", "cited_clauses": [],
                                                  "paraphrased_or_added_clauses": [], "status": "DRAFT-NOT-APPROVED"}]
        return response
    assert "S05" in failed(harness.run_agent(agent))


def test_agent_that_offers_both_position_senses_and_asks_which_still_passes():
    def agent(request, glossary):
        response = reference_agent(request, glossary)
        if "'Position'" in request:
            response["candidate_definitions"] = [
                {"term": t["term"], "draft_text": t["definition"], "cited_clauses": [t["definition"]],
                 "paraphrased_or_added_clauses": [], "status": "DRAFT-NOT-APPROVED"}
                for t in glossary.search_terms("Position")]
        return response
    assert "S05" not in failed(harness.run_agent(agent))


def test_conflict_candidate_that_keeps_timing_open_passes_but_one_that_picks_t_plus_0_fails():
    def open_candidate(request, glossary):
        response = reference_agent(request, glossary)
        if "Trade Date" in request:
            response["candidate_definitions"] = [{"term": "Trade Date", "draft_text": "The date a trade is executed; booking timing is T+0 in GL-301 and T+1 in GL-302.",
                                                  "cited_clauses": [], "paraphrased_or_added_clauses": [], "status": "DRAFT-NOT-APPROVED"}]
        return response

    def picks(request, glossary):
        response = open_candidate(request, glossary)
        if "Trade Date" in request:
            response["candidate_definitions"][0]["draft_text"] = "The date a trade is executed and booked (T+0)."
        return response
    assert "S03" not in failed(harness.run_agent(open_candidate))
    assert "S03" in failed(harness.run_agent(picks))


# ---- assertion corrections made after pass 2 (see evals/definition-and-cde-runs/RESULTS.md) --------------

def test_negated_approval_wording_is_not_flagged_but_a_real_approval_claim_is():
    def negated(request, glossary):
        response = reference_agent(request, glossary)
        if "approve" in request.lower():
            response["summary"] += " Nothing has been approved, finalised or designated by this agent."
        return response
    assert "S08" not in failed(harness.run_agent(negated))


def test_missing_term_wording_from_the_contracts_own_distinction_is_accepted():
    def contract_wording(request, glossary):
        response = reference_agent(request, glossary)
        if "Define 'Notional" in request:
            response["summary"] = "The register exists but has no entry for this term; no definition is drafted."
            response["open_questions"] = ["Is the term known under another name?"]
            response["human_action_required"] = ["Data Steward to confirm whether the term should exist."]
        return response
    assert "S02" not in failed(harness.run_agent(contract_wording))


def test_a_reply_that_says_nothing_about_a_missing_entry_still_fails_s02():
    def vague(request, glossary):
        response = reference_agent(request, glossary)
        if "Define 'Notional" in request:
            response["summary"] = "I could not complete this."
            response["open_questions"] = ["Why?"]
            response["human_action_required"] = ["Please advise."]
        return response
    assert "S02" in failed(harness.run_agent(vague))
