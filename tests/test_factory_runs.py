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
# Drift recorded in RESULTS.md findings 1 and 2. Any other schema error is new and fails the test.
KNOWN_EXTRA_FIELDS = {"evaluation_outline_pointer", "draft_agent_contract"}


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
        if "Additional properties" in error.message and any(f"'{f}'" in error.message for f in KNOWN_EXTRA_FIELDS):
            continue
        if list(error.absolute_path) == ["handoff", "status"]:
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


def test_results_record_matches_the_graded_outcomes():
    results = (RUNS / "RESULTS.md").read_text(encoding="utf-8")
    assert "| **Pass** | Specialised AI agent / keep |" in results
    assert "| **Pass** | Deterministic process / cut |" in results
    assert "| **Fail (strict reading)** | AI-assisted workflow / redesign |" in results
    assert run("FACTORY-RUN-P4-03")["classification"] == "AI-assisted workflow"