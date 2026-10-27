import copy

import pytest

from schema_registry import ROOT, SCHEMAS, load, validator_for

SCHEMA = SCHEMAS / "evidence.schema.json"
EVIDENCE = load(ROOT / "examples" / "evidence.valid.example.json")
LABELS = ["unassigned", "internal_use_only", "confidential", "restricted_confidential"]


def errors(instance):
    return list(validator_for(SCHEMA).iter_errors(instance))


def test_label_is_optional():
    assert "confidentiality_label" not in EVIDENCE
    assert errors(EVIDENCE) == []


@pytest.mark.parametrize("label", LABELS)
def test_each_provisional_label_is_accepted(label):
    ok = copy.deepcopy(EVIDENCE)
    ok["confidentiality_label"] = label
    assert errors(ok) == []


@pytest.mark.parametrize("label", ["public", "registered_confidential", "Confidential", ""])
def test_other_values_are_rejected(label):
    bad = copy.deepcopy(EVIDENCE)
    bad["confidentiality_label"] = label
    assert errors(bad)


def test_doc_lists_exactly_the_schema_labels():
    text = (ROOT / "docs" / "DATA-CLASSIFICATION.md").read_text(encoding="utf-8")
    enum = load(SCHEMA)["properties"]["confidentiality_label"]["enum"]
    assert enum == LABELS
    assert all(f"`{label}`" in text for label in enum)
