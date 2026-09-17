import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_TAXONOMY = [
    "Happy path", "Missing evidence", "Conflicting evidence", "Incomplete data",
    "Ambiguous terminology", "Incorrect mapping", "Unsupported inference",
    "Unauthorised decision attempt", "Tool unavailable", "Downstream dependency unknown",
]


def test_definition_cde_eval_covers_full_taxonomy():
    text = (ROOT / "evals" / "definition-and-cde-agent.eval.md").read_text(encoding="utf-8")
    for category in REQUIRED_TAXONOMY:
        assert category in text, f"missing taxonomy category: {category}"


def test_definition_cde_eval_inputs_are_all_labelled_synthetic():
    text = (ROOT / "evals" / "definition-and-cde-agent.eval.md").read_text(encoding="utf-8")
    inputs = re.findall(r"\*\*Input:\*\*\s*(.+)", text)
    assert len(inputs) == 10
    assert all(i.strip().startswith("SYNTHETIC") for i in inputs), "every Input line must start with SYNTHETIC"


def test_factory_scenarios_reference_the_exact_denied_tools_from_definition_cde_contract():
    import json
    with open(ROOT / "contracts/definition-and-cde-agent.contract.json", encoding="utf-8") as f:
        contract = json.load(f)
    text = (ROOT / "evals" / "factory-test-scenarios.md").read_text(encoding="utf-8")
    for tool in ["qlik_create_glossary_term", "qlik_update_glossary_term", "qlik_delete_glossary_term",
                 "qlik_update_term_status", "qlik_create_glossary_term_links"]:
        assert tool in contract["prohibited_tools_or_actions"]
        assert tool in text, f"P4-01 pass condition must name {tool} explicitly"
