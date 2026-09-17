import json
import re
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_HEADINGS = [
    "## Agent Name", "## Version", "## Status", "## Purpose", "## Business Problem",
    "## Classification", "## Responsible For", "## Not Responsible For",
    "## Required Inputs", "## Authoritative Sources", "## Permitted Tools",
    "## Prohibited Tools or Actions", "## Process", "## Output Schema",
    "## Evidence Requirements", "## Confidence Rules", "## Escalation Conditions",
    "## Human Approval Required For", "## Upstream Agents", "## Downstream Agents",
    "## Handoff Contract", "## Success Criteria", "## Known Risks",
    "## Evaluation Scenarios", "## Change Log",
]

CONTRACT_PAIRS = [
    ("agents/factory/stewardship-agent-architect.md", "contracts/stewardship-agent-architect.contract.json"),
    ("agents/factory/agent-risk-reviewer.md", "contracts/agent-risk-reviewer.contract.json"),
    ("agents/factory/agent-evaluation-designer.md", "contracts/agent-evaluation-designer.contract.json"),
    ("agents/factory/claude-agent-builder.md", "contracts/claude-agent-builder.contract.json"),
    ("agents/operational/definition-and-cde-agent.md", "contracts/definition-and-cde-agent.contract.json"),
]


def load_schema():
    with open(ROOT / "schemas" / "agent-contract.schema.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.parametrize("md_path,json_path", CONTRACT_PAIRS)
def test_markdown_contract_has_all_mandatory_sections(md_path, json_path):
    text = (ROOT / md_path).read_text(encoding="utf-8")
    for heading in REQUIRED_HEADINGS:
        assert re.search(rf"^{re.escape(heading)}\s*$", text, re.MULTILINE), f"missing {heading} in {md_path}"


@pytest.mark.parametrize("md_path,json_path", CONTRACT_PAIRS)
def test_json_contract_validates_against_schema(md_path, json_path):
    schema = load_schema()
    with open(ROOT / json_path, encoding="utf-8") as f:
        instance = json.load(f)
    Draft202012Validator(schema).validate(instance)


@pytest.mark.parametrize("md_path,json_path", CONTRACT_PAIRS)
def test_json_contract_status_is_draft(md_path, json_path):
    with open(ROOT / json_path, encoding="utf-8") as f:
        instance = json.load(f)
    assert instance["status"] == "Draft"


def test_definition_cde_agent_denies_every_glossary_write_tool():
    with open(ROOT / "contracts/definition-and-cde-agent.contract.json", encoding="utf-8") as f:
        instance = json.load(f)
    denied = set(instance["prohibited_tools_or_actions"])
    must_deny = {
        "qlik_create_glossary_term", "qlik_update_glossary_term", "qlik_delete_glossary_term",
        "qlik_update_term_status", "qlik_create_glossary_term_links",
        "qlik_create_glossary", "qlik_create_glossary_category",
    }
    assert must_deny <= denied, f"missing denies: {must_deny - denied}"
    permitted_tool_names = {t["tool"] for t in instance["permitted_tools"]}
    assert permitted_tool_names.isdisjoint(must_deny), "a denied tool appears in permitted_tools"
