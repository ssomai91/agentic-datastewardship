import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from schema_registry import validator_for

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
EXAMPLES = ROOT / "examples"


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.parametrize("schema_file", [
    "agent-contract.schema.json",
    "agent-handoff.schema.json",
    "evidence.schema.json",
    "material-claim.schema.json",
    "quality-issue.schema.json",
])
def test_schema_is_valid_json_schema(schema_file):
    schema = load(SCHEMAS / schema_file)
    Draft202012Validator.check_schema(schema)


def test_valid_contract_example_passes():
    schema = load(SCHEMAS / "agent-contract.schema.json")
    instance = load(EXAMPLES / "agent-contract.valid.example.json")
    Draft202012Validator(schema).validate(instance)


def test_invalid_contract_example_fails_on_missing_mandatory_fields():
    schema = load(SCHEMAS / "agent-contract.schema.json")
    instance = load(EXAMPLES / "agent-contract.invalid.example.json")
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.message)
    assert errors, "expected the invalid fixture to fail validation"
    missing = {e.message for e in errors}
    assert any("not_responsible_for" in m for m in missing)
    assert any("permitted_tools" in m for m in missing)


def test_valid_handoff_example_passes():
    instance = load(EXAMPLES / "agent-handoff.valid.example.json")
    validator_for(SCHEMAS / "agent-handoff.schema.json").validate(instance)


def test_valid_evidence_example_passes():
    schema = load(SCHEMAS / "evidence.schema.json")
    instance = load(EXAMPLES / "evidence.valid.example.json")
    Draft202012Validator(schema).validate(instance)
