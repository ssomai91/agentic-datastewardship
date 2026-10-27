import copy
import sys

import pytest

from schema_registry import ROOT, SCHEMAS, load

sys.path.insert(0, str(ROOT / "tools"))
from validate_coverage_trace import coverage_trace_problems  # noqa: E402

CONTRACT = load(ROOT / "contracts" / "definition-and-cde-agent.contract.json")
CONTRACT_SCHEMA = load(SCHEMAS / "agent-contract.schema.json")
FIELDS = list(CONTRACT_SCHEMA["required"])
PASSAGE = "You are the Definition and CDE Agent"
FILES = {"prompts/definition-and-cde-agent.md": "Intro. " + PASSAGE + " for this repository."}


def good_output():
    return {
        "summary": "fixture",
        "generated_files": list(FILES),
        "coverage_trace": [{"contract_field": f, "prompt_passage": PASSAGE} for f in FIELDS[:-1]],
        "uncovered_fields": [FIELDS[-1]],
    }


def problems(output, files=FILES):
    return coverage_trace_problems(output, CONTRACT, CONTRACT_SCHEMA, files)


def test_complete_trace_passes():
    assert problems(good_output()) == []


def test_contract_has_every_required_field():
    assert set(FIELDS) <= set(CONTRACT)


def test_missing_field_is_reported():
    out = good_output()
    dropped = out["coverage_trace"].pop()["contract_field"]
    assert problems(out) == [f"contract field '{dropped}' is neither traced nor listed as uncovered"]


def test_invented_field_is_reported():
    out = good_output()
    out["coverage_trace"].append({"contract_field": "admin_override", "prompt_passage": PASSAGE})
    assert "'admin_override' is not a field of the approved contract" in problems(out)


def test_field_both_traced_and_uncovered_is_reported():
    out = good_output()
    out["uncovered_fields"].append(FIELDS[0])
    assert f"'{FIELDS[0]}' is both traced and listed as uncovered" in problems(out)


def test_duplicate_trace_entry_is_reported():
    out = good_output()
    out["coverage_trace"].append(copy.deepcopy(out["coverage_trace"][0]))
    assert f"'{FIELDS[0]}' is traced more than once" in problems(out)


@pytest.mark.parametrize("path", [
    "contracts/definition-and-cde-agent.contract.json",
    "agents/operational/definition-and-cde-agent.md",
    "prompts/../contracts/x.json",
    "docs/x.md",
])
def test_generated_file_outside_prompts_is_reported(path):
    out = good_output()
    out["generated_files"] = [path]
    assert any("outside prompts/" in p or "protected location" in p for p in problems(out, files=None))


def test_fabricated_passage_is_reported():
    out = good_output()
    out["coverage_trace"][0]["prompt_passage"] = "This sentence is nowhere in the prompt."
    assert problems(out) == [f"passage for '{FIELDS[0]}' does not occur in any generated file"]


def test_passage_match_ignores_case_and_whitespace():
    out = good_output()
    out["coverage_trace"][0]["prompt_passage"] = "  you ARE the\n Definition and CDE agent "
    assert problems(out) == []