"""docs/GLOSSARY.md must keep up with the codes the repository actually uses."""
import re

from schema_registry import ROOT

GLOSSARY = (ROOT / "docs" / "GLOSSARY.md").read_text(encoding="utf-8")
DECISIONS = (ROOT / "GOVERNANCE-DECISIONS.md").read_text(encoding="utf-8")
CONTRACT = (ROOT / "agents" / "operational" / "assurance-reviewer.md").read_text(encoding="utf-8")


def test_every_governance_decision_in_the_register_is_in_the_glossary():
    ids = sorted(set(re.findall(r"\bGD-\d{2}\b", DECISIONS)))
    assert ids and [i for i in ids if i not in GLOSSARY] == []


def test_every_build_precondition_in_the_contract_is_in_the_glossary():
    ids = sorted(set(re.findall(r"\bDC-\d\b", CONTRACT)))
    assert len(ids) == 8 and [i for i in ids if i not in GLOSSARY] == []


def test_the_gate_values_and_confidence_labels_are_defined():
    for term in ("HOLD_RECOMMENDED", "NO_BLOCKING_FINDINGS_IDENTIFIED", "INCOMPLETE", "Supported", "Partially supported", "Unsupported",
                 "Contradictory", "Unable to determine"):
        assert term in GLOSSARY, term


def test_every_agent_name_is_in_the_glossary():
    import json
    for path in (ROOT / "contracts").glob("*.contract.json"):
        assert json.loads(path.read_text(encoding="utf-8"))["name"] in GLOSSARY, path.name


def test_the_open_decision_is_marked_open():
    assert re.search(r"\*\*GD-05\*\*[^\n]*\*\*Open\*\*", GLOSSARY)
    assert "GD-05" in DECISIONS and "**Open**" in DECISIONS


def test_the_glossary_is_linked_from_the_readme():
    assert "docs/GLOSSARY.md" in (ROOT / "README.md").read_text(encoding="utf-8")