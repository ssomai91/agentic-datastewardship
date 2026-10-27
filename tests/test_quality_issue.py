import copy

import pytest

from schema_registry import ROOT, SCHEMAS, load, validator_for

SCHEMA = SCHEMAS / "quality-issue.schema.json"
EXAMPLE = load(ROOT / "examples" / "quality-issue.valid.example.json")


def errors(instance):
    return list(validator_for(SCHEMA).iter_errors(instance))


def test_valid_example_passes():
    assert errors(EXAMPLE) == []


@pytest.mark.parametrize("field", ["issue_id", "description", "root_causes", "remediation_options", "decision", "decision_owner"])
def test_each_minimum_field_is_required(field):
    bad = copy.deepcopy(EXAMPLE)
    del bad[field]
    assert errors(bad)


def test_empty_decision_owner_and_undeclared_fields_are_rejected():
    bad = copy.deepcopy(EXAMPLE)
    bad["decision_owner"] = ""
    assert errors(bad)
    bad = copy.deepcopy(EXAMPLE)
    bad["approved"] = True
    assert errors(bad)
