import copy
import json

import pytest

from handoff_checks import handoff_reference_problems
from schema_registry import ROOT, SCHEMAS, load, validator_for

AGENTS = [
    "stewardship-agent-architect",
    "agent-risk-reviewer",
    "agent-evaluation-designer",
    "claude-agent-builder",
    "definition-and-cde-agent",
    "assurance-reviewer",
]


def schema_path(agent):
    return SCHEMAS / "outputs" / f"{agent}.output.schema.json"


def example(agent):
    return load(ROOT / "examples" / "outputs" / f"{agent}.output.valid.example.json")


def errors(agent, instance):
    return list(validator_for(schema_path(agent)).iter_errors(instance))


@pytest.mark.parametrize("agent", AGENTS)
def test_valid_output_example_passes(agent):
    instance = example(agent)
    assert errors(agent, instance) == []
    assert handoff_reference_problems(instance["handoff"]) == []


@pytest.mark.parametrize("agent", AGENTS)
def test_output_schema_matches_contract_output_schema_fields(agent):
    contract = load(ROOT / "contracts" / f"{agent}.contract.json")
    schema = load(schema_path(agent))
    assert set(schema["properties"]) == set(contract["output_schema"]), (
        f"{agent}: output schema fields differ from the contract's output_schema"
    )
    optional = {k for k, v in contract["output_schema"].items() if "(optional" in v}
    assert set(schema["required"]) == set(contract["output_schema"]) - optional


@pytest.mark.parametrize("agent", AGENTS)
def test_output_rejects_missing_summary(agent):
    bad = copy.deepcopy(example(agent))
    del bad["summary"]
    assert errors(agent, bad)


@pytest.mark.parametrize("agent", AGENTS)
def test_output_rejects_undeclared_field(agent):
    bad = copy.deepcopy(example(agent))
    bad["approved"] = True
    assert errors(agent, bad)


@pytest.mark.parametrize("agent", AGENTS)
def test_output_handoff_is_validated(agent):
    bad = copy.deepcopy(example(agent))
    bad["handoff"]["status"] = "approved"
    assert errors(agent, bad)


@pytest.mark.parametrize("agent,field", [
    ("stewardship-agent-architect", "necessity_verdict"),
    ("agent-risk-reviewer", "final_verdict"),
])
def test_verdict_must_be_in_the_five_values(agent, field):
    bad = copy.deepcopy(example(agent))
    bad[field] = "approve"
    assert errors(agent, bad)


def test_architect_classification_must_be_one_of_five():
    bad = copy.deepcopy(example("stewardship-agent-architect"))
    bad["classification"] = "Autonomous agent"
    assert errors("stewardship-agent-architect", bad)


def test_risk_finding_needs_certainty_label():
    bad = copy.deepcopy(example("agent-risk-reviewer"))
    del bad["findings"][0]["certainty"]
    assert errors("agent-risk-reviewer", bad)
    bad["findings"][0]["certainty"] = "MAYBE"
    assert errors("agent-risk-reviewer", bad)


def test_eval_test_case_needs_all_three_fields():
    bad = copy.deepcopy(example("agent-evaluation-designer"))
    del bad["test_cases"][0]["expected_behavior"]
    assert errors("agent-evaluation-designer", bad)


def test_builder_may_only_write_under_prompts():
    bad = copy.deepcopy(example("claude-agent-builder"))
    bad["generated_files"] = ["contracts/example.contract.json"]
    assert errors("claude-agent-builder", bad)


def test_builder_coverage_trace_entry_needs_both_fields():
    bad = copy.deepcopy(example("claude-agent-builder"))
    del bad["coverage_trace"][0]["prompt_passage"]
    assert errors("claude-agent-builder", bad)

def test_architect_optional_fields_are_strings_and_draft_is_not_a_handoff_status():
    ok = copy.deepcopy(example("stewardship-agent-architect"))
    ok["draft_agent_contract"] = "# Agent Contract: Illustrative"
    assert errors("stewardship-agent-architect", ok) == []
    bad = copy.deepcopy(ok)
    bad["draft_agent_contract"] = {"name": "not a string"}
    assert errors("stewardship-agent-architect", bad)
    bad = copy.deepcopy(ok)
    bad["handoff"]["status"] = "Draft"
    assert errors("stewardship-agent-architect", bad)
