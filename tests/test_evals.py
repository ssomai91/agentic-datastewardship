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
