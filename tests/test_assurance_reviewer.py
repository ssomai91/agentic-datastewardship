"""Guards the Phase 6 Assurance Reviewer artefacts: eval spec, prompt copy, Builder trace and the recorded design rounds."""
import json
import re
import subprocess
import sys

import pytest

from schema_registry import ROOT, SCHEMAS, load

RUNS = ROOT / "evals" / "factory-runs"
CONTRACT_JSON = load(ROOT / "contracts" / "assurance-reviewer.contract.json")
CONTRACT_MD = (ROOT / "agents" / "operational" / "assurance-reviewer.md").read_text(encoding="utf-8")
EVAL = load(ROOT / "evals" / "assurance-reviewer.eval.output.json")
CATEGORIES = {
    "happy path", "conflicting evidence", "missing evidence", "incomplete data", "ambiguous terminology",
    "incorrect mapping", "unsupported inference", "unauthorised decision attempt", "tool unavailable", "downstream dependency unknown",
}


def test_contract_is_still_a_draft_in_both_forms_and_nothing_approves_it():
    assert CONTRACT_JSON["status"] == "Draft"
    assert re.search(r"## Status\s+`Draft`", CONTRACT_MD)
    assert "Approved" not in {row.get("approved_by") for row in CONTRACT_JSON["change_log"]}


def test_every_change_log_row_in_both_forms_is_unapproved_and_the_last_row_is_the_current_version():
    assert CONTRACT_JSON["change_log"][-1]["version"] == CONTRACT_JSON["version"]
    assert all("Draft" in row["approved_by"] for row in CONTRACT_JSON["change_log"])


def test_json_contract_lists_all_eight_build_preconditions():
    text = " ".join(CONTRACT_JSON["build_preconditions"])
    assert all(f"DC-{n}" in text for n in range(1, 9))
    assert "not be built or run against real cases" in text


def test_eval_spec_covers_all_ten_categories_with_synthetic_labelled_inputs():
    assert {c["taxonomy_category"] for c in EVAL["test_cases"]} == CATEGORIES
    assert all(c["input_synthetic"].lstrip().startswith("SYNTHETIC") for c in EVAL["test_cases"])
    assert len(EVAL["test_cases"]) >= 60


def test_rendered_eval_doc_matches_the_machine_readable_spec():
    doc = (ROOT / "evals" / "assurance-reviewer.eval.md").read_text(encoding="utf-8")
    assert "No case has been run" in doc
    assert len(re.findall(r"(?m)^### AR-T\d+", doc)) == len(EVAL["test_cases"])
    assert len(re.findall(r"(?m)^\d+\. UNRESOLVED", doc)) == len(EVAL["unresolved_thresholds"])


def test_contract_points_the_owner_at_the_open_points_found_by_the_eval_designer():
    assert "20 points" in CONTRACT_MD and "evals/assurance-reviewer.eval.md" in CONTRACT_MD


def test_prompt_in_claude_agents_is_identical_to_the_builders_draft():
    assert (ROOT / ".claude" / "agents" / "assurance-reviewer.md").read_bytes() == (ROOT / "prompts" / "assurance-reviewer.md").read_bytes()


def test_builder_coverage_trace_validates_against_the_real_contract():
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "validate_coverage_trace.py"), str(RUNS / "p6-assurance-reviewer.builder.output.json"),
         str(ROOT / "contracts" / "assurance-reviewer.contract.json")],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout


def test_builder_trace_covers_the_prompt_path_it_names():
    out = load(RUNS / "p6-assurance-reviewer.builder.output.json")
    assert out["generated_files"] == ["prompts/assurance-reviewer.md"]
    assert set(out["uncovered_fields"]) == {"evaluation_scenarios", "change_log"}


def test_design_rounds_are_recorded_and_the_final_review_found_nothing_blocking():
    for name in ("architect", "architect-v1", "architect-v2", "architect-v3"):
        suffix = "architect.output.json" if name == "architect" else f"{name}.output.json"
        assert (RUNS / f"p6-assurance-reviewer.{suffix}").is_file()
    final = load(RUNS / "p6-assurance-reviewer.review-v3.reviewer.output.json")
    assert final["final_verdict"] == "keep"
    assert not [f for f in final["findings"] if f["issue"].lstrip().startswith("[BLOCKING]")]
    assert (RUNS / "p6-assurance-reviewer.STOPPING-RULE.md").is_file()


def test_gate_values_in_the_output_schema_match_the_contract():
    schema = load(SCHEMAS / "outputs" / "assurance-reviewer.output.schema.json")
    values = set(schema["properties"]["gate_recommendation"]["enum"])
    assert values == {"HOLD_RECOMMENDED", "NO_BLOCKING_FINDINGS_IDENTIFIED", "INCOMPLETE"}
    assert all(v in CONTRACT_MD for v in values)
