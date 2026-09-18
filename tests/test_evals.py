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


def test_factory_scenarios_reference_the_same_denied_capabilities_as_definition_cde_contract():
    import json
    with open(ROOT / "contracts/definition-and-cde-agent.contract.json", encoding="utf-8") as f:
        contract = json.load(f)
    denied_in_contract = " ".join(contract["prohibited_tools_or_actions"]).lower()
    text = (ROOT / "evals" / "factory-test-scenarios.md").read_text(encoding="utf-8").lower()

    # Both documents must independently cover all four write-capability categories -
    # exact wording may differ between the contract and this acceptance doc, but the
    # capability categories denied must be the same set.
    action_keywords = ["creat", "updat", "delet", "status"]
    for keyword in action_keywords:
        assert keyword in denied_in_contract, f"contract's prohibited_tools_or_actions missing {keyword!r}-type action"
        assert keyword in text, f"P4-01 pass condition missing {keyword!r}-type action"
