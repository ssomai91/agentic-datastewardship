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


ASSUMPTIONS_HEADING = "## Assumptions Pending Human Confirmation"


@pytest.mark.parametrize("md_path,json_path", CONTRACT_PAIRS)
def test_assumptions_section_and_json_field_agree(md_path, json_path):
    """If the markdown has an Assumptions Pending Human Confirmation section, the JSON
    `assumptions` array must be non-empty, and vice versa - the two must never disagree
    about whether this agent carries a disclosed, unresolved governance assumption."""
    text = (ROOT / md_path).read_text(encoding="utf-8")
    md_has_section = bool(re.search(rf"^{re.escape(ASSUMPTIONS_HEADING)}\s*$", text, re.MULTILINE))

    with open(ROOT / json_path, encoding="utf-8") as f:
        instance = json.load(f)
    json_has_assumptions = bool(instance.get("assumptions"))

    assert md_has_section == json_has_assumptions, (
        f"{md_path} has {ASSUMPTIONS_HEADING!r} section: {md_has_section}, "
        f"but {json_path}'s 'assumptions' array is non-empty: {json_has_assumptions} - these must agree"
    )
    if md_has_section:
        assert len(instance["assumptions"]) >= 1


def _all_contract_names():
    names = set()
    for _md_path, json_path in CONTRACT_PAIRS:
        with open(ROOT / json_path, encoding="utf-8") as f:
            names.add(json.load(f)["name"])
    return names


KNOWN_FORWARD_REFERENCES = {"Assurance Reviewer"}


@pytest.mark.parametrize("md_path,json_path", CONTRACT_PAIRS)
def test_upstream_and_downstream_agents_reference_known_agents(md_path, json_path):
    """Every upstream_agents/downstream_agents entry must either name another contract
    that actually exists in this repo's set of 5, or be an explicitly allow-listed
    forward reference to an agent not yet built - anything else is a typo or an
    orphaned reference."""
    known_names = _all_contract_names()
    with open(ROOT / json_path, encoding="utf-8") as f:
        instance = json.load(f)
    for field in ("upstream_agents", "downstream_agents"):
        for entry in instance.get(field, []):
            assert entry in known_names or entry in KNOWN_FORWARD_REFERENCES, (
                f"{json_path}'s {field} entry {entry!r} does not match any of this repo's "
                f"contract names ({known_names}) and is not in the allow-list "
                f"({KNOWN_FORWARD_REFERENCES})"
            )
