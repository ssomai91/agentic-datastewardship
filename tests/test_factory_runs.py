"""Guards the recorded Factory runs in evals/factory-runs/ so the record cannot drift silently."""
import json

import pytest

from handoff_checks import handoff_reference_problems
from schema_registry import ROOT, SCHEMAS, validator_for

RUNS = ROOT / "evals" / "factory-runs"
OUTPUT_SCHEMA = SCHEMAS / "outputs" / "stewardship-agent-architect.output.schema.json"
FILES = {
    "FACTORY-RUN-P4-01": "p4-01-definition-and-cde.architect.output.json",
    "FACTORY-RUN-P4-02": "p4-02-deterministic-quality-check.architect.output.json",
    "FACTORY-RUN-P4-03": "p4-03-root-cause-analysis.architect.output.json",
}
# Run 1 predates contract v0.1.1 (RESULTS.md findings 1 and 2, fixed in v0.1.1). Run 1 used a "Draft" handoff status and
# gave draft_agent_contract as an object; v0.1.1 says it is a string. Any other schema error is new and fails the test.


def run(case_id):
    return json.loads((RUNS / FILES[case_id]).read_text(encoding="utf-8"))


@pytest.mark.parametrize("case_id", FILES)
def test_recorded_run_has_matching_case_id_and_resolvable_claims(case_id):
    data = run(case_id)
    assert data["handoff"]["case_id"] == case_id
    assert handoff_reference_problems(data["handoff"]) == []


@pytest.mark.parametrize("case_id", FILES)
def test_recorded_run_has_only_the_known_schema_deviations(case_id):
    unexpected = []
    for error in validator_for(OUTPUT_SCHEMA).iter_errors(run(case_id)):
        if list(error.absolute_path) == ["handoff", "status"]:
            continue
        if list(error.absolute_path) == ["draft_agent_contract"]:
            continue
        unexpected.append(error.message[:160])
    assert unexpected == []


def test_p4_02_is_classified_as_a_deterministic_process():
    assert run("FACTORY-RUN-P4-02")["classification"] == "Deterministic process"


def test_p4_01_prohibits_glossary_writes_and_permits_only_read_access():
    text = " ".join(run("FACTORY-RUN-P4-01")["recommendations"]).lower()
    assert "permitted tools" in text and "read-only" in text
    for action in ("write", "update", "delete", "status-change"):
        assert action in text.split("prohibited tools and actions")[1], f"prohibited set must name '{action}'"


def _run2():
    return json.loads((RUNS / "p4-03-root-cause-analysis.run2.architect.output.json").read_text(encoding="utf-8"))


def test_p4_03_run_2_designs_a_curated_packet_and_no_direct_multi_source_access():
    data = _run2()
    text = json.dumps(data).lower()
    assert data["classification"] == "AI-assisted workflow"
    assert "curated evidence packet" in text
    assert "no query access to raw exception, change or lineage logs" in text
    assert data["handoff"]["status"] == "completed", "Draft must not be used as a handoff status (contract v0.1.1)"
    assert handoff_reference_problems(data["handoff"]) == []


def test_p4_03_run_2_only_deviation_is_the_recorded_findings_type_slip():
    paths = [list(e.absolute_path) for e in validator_for(OUTPUT_SCHEMA).iter_errors(_run2())]
    assert paths == [["handoff", "findings"]]


def test_results_record_matches_the_graded_outcomes():
    results = (RUNS / "RESULTS.md").read_text(encoding="utf-8")
    assert "| **Pass** | Specialised AI agent / keep |" in results
    assert "| **Pass** | Deterministic process / cut |" in results
    assert "| **Fail (strict reading)** | AI-assisted workflow / redesign |" in results
    assert "(run 2) | `p4-03-root-cause-analysis.run2.architect.output.json` | **Pass** |" in results
    assert run("FACTORY-RUN-P4-03")["classification"] == "AI-assisted workflow"