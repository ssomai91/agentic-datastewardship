"""Consistency of the three forms of each agent: Markdown contract, JSON contract, Claude prompt.

The Markdown contract is the source of truth (docs/AUTHORITY-CHAIN.md). A failure here names the
lower-ranked artefact that has drifted.
"""
import json
import re
from pathlib import Path

import pytest

from schema_registry import ROOT, SCHEMAS, load

READ_ONLY = {"Read", "Grep", "Glob"}
# Tools each prompt may hold. The Builder alone may write (generated prompts only, per its contract).
ALLOWED_TOOLS = {
    "stewardship-agent-architect": READ_ONLY,
    "agent-risk-reviewer": READ_ONLY,
    "agent-evaluation-designer": READ_ONLY,
    "claude-agent-builder": READ_ONLY | {"Write"},
    "definition-and-cde-agent": READ_ONLY,
}
TIERS = {
    "stewardship-agent-architect": "factory",
    "agent-risk-reviewer": "factory",
    "agent-evaluation-designer": "factory",
    "claude-agent-builder": "factory",
    "definition-and-cde-agent": "operational",
}
AGENTS = sorted(TIERS)


def read(path):
    return Path(path).read_text(encoding="utf-8")


def markdown_contract(agent):
    path = ROOT / "agents" / TIERS[agent] / f"{agent}.md"
    text = read(path)
    return {
        "path": f"agents/{TIERS[agent]}/{agent}.md",
        "name": re.search(r"^# Agent Contract: (.+)$", text, re.M).group(1).strip(),
        "version": re.search(r"^## Version\s+`?([0-9]+\.[0-9]+\.[0-9]+)", text, re.M).group(1),
        "status": re.search(r"^## Status\s+`?(\w+)", text, re.M).group(1),
    }


def json_contract(agent):
    return load(ROOT / "contracts" / f"{agent}.contract.json")


def prompt(agent):
    text = read(ROOT / ".claude" / "agents" / f"{agent}.md")
    front = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    assert front, f"{agent}: prompt has no frontmatter"
    fields = dict(
        (m.group(1), m.group(2).strip())
        for m in re.finditer(r"^(\w+):\s*(.*)$", front.group(1), re.M)
    )
    return {"fields": fields, "body": text[front.end():], "text": text}


def test_every_agent_in_the_repo_is_covered_by_this_file():
    on_disk = {p.stem for p in (ROOT / "agents").rglob("*.md")}
    assert on_disk == set(AGENTS), "add the new agent to TIERS and ALLOWED_TOOLS in test_agent_consistency.py"
    assert {p.stem for p in (ROOT / ".claude" / "agents").glob("*.md")} == set(AGENTS)


@pytest.mark.parametrize("agent", AGENTS)
def test_json_contract_matches_markdown_contract(agent):
    md, js = markdown_contract(agent), json_contract(agent)
    assert js["name"] == md["name"], f"{agent}: JSON name differs from Markdown contract"
    assert js["version"] == md["version"], f"{agent}: JSON version differs from Markdown contract"
    assert js["status"] == md["status"], f"{agent}: JSON status differs from Markdown contract"


@pytest.mark.parametrize("agent", AGENTS)
def test_prompt_frontmatter_is_complete_and_named_for_the_file(agent):
    fields = prompt(agent)["fields"]
    assert fields.get("name") == agent
    assert fields.get("description"), f"{agent}: prompt needs a description"
    assert fields.get("tools"), f"{agent}: prompt needs an explicit tools list"


@pytest.mark.parametrize("agent", AGENTS)
def test_prompt_tools_do_not_exceed_what_the_agent_may_hold(agent):
    tools = {t.strip() for t in prompt(agent)["fields"]["tools"].split(",")}
    extra = tools - ALLOWED_TOOLS[agent]
    assert not extra, f"{agent}: prompt grants {sorted(extra)}, more than the contract allows"


@pytest.mark.parametrize("agent", AGENTS)
def test_prompt_names_its_governing_contract(agent):
    md = markdown_contract(agent)
    assert md["path"] in prompt(agent)["body"], f"{agent}: prompt must name {md['path']}"


@pytest.mark.parametrize("agent", AGENTS)
def test_prompt_version_reference_matches_contract_when_present(agent):
    versions = set(re.findall(r"\(v([0-9]+\.[0-9]+\.[0-9]+)\)", prompt(agent)["body"]))
    assert versions <= {markdown_contract(agent)["version"]}, f"{agent}: prompt cites a different contract version"


@pytest.mark.parametrize("agent", AGENTS)
def test_prompt_and_contract_text_are_not_mis_encoded(agent):
    for path in (
        ROOT / "agents" / TIERS[agent] / f"{agent}.md",
        ROOT / ".claude" / "agents" / f"{agent}.md",
        ROOT / "contracts" / f"{agent}.contract.json",
    ):
        text = read(path)
        assert "�" not in text and "â€" not in text, f"{path.name}: mis-encoded characters"


@pytest.mark.parametrize("agent", AGENTS)
def test_json_contract_confidence_labels_match_the_claim_schema(agent):
    labels = load(SCHEMAS / "material-claim.schema.json")["properties"]["confidence"]["enum"]
    assert json_contract(agent)["confidence_labels"] == labels


@pytest.mark.parametrize("agent", AGENTS)
def test_json_contract_handoff_returns_cover_every_handoff_schema_field(agent):
    required = set(load(SCHEMAS / "agent-handoff.schema.json")["required"])
    returns = set(json_contract(agent)["handoff_contract"]["returns"])
    assert required <= returns, f"{agent}: handoff returns missing {sorted(required - returns)}"


@pytest.mark.parametrize("agent", AGENTS)
def test_markdown_contract_handoff_returns_cover_every_handoff_schema_field(agent):
    text = read(ROOT / "agents" / TIERS[agent] / f"{agent}.md")
    block = re.search(r"### Returns\s+```yaml\n(.*?)```", text, re.S).group(1)
    keys = set(re.findall(r"^(\w+):", block, re.M))
    required = set(load(SCHEMAS / "agent-handoff.schema.json")["required"])
    assert required <= keys, f"{agent}: Markdown Returns block missing {sorted(required - keys)}"


@pytest.mark.parametrize("agent", AGENTS)
def test_json_and_markdown_returns_agree_on_fields(agent):
    text = read(ROOT / "agents" / TIERS[agent] / f"{agent}.md")
    block = re.search(r"### Returns\s+```yaml\n(.*?)```", text, re.S).group(1)
    assert set(re.findall(r"^(\w+):", block, re.M)) == set(json_contract(agent)["handoff_contract"]["returns"])


@pytest.mark.parametrize("agent", AGENTS)
def test_prompt_tells_the_agent_to_return_claims_with_evidence(agent):
    body = prompt(agent)["body"]
    assert "`claims`" in body and "material-claim.schema.json" in body, f"{agent}: prompt must instruct claims in the handoff"


def test_definition_agent_confidence_label_rule_for_non_evidence_claims_is_in_all_three_forms():
    agent = "definition-and-cde-agent"
    md = read(ROOT / "agents" / TIERS[agent] / f"{agent}.md")
    js = json.dumps(json_contract(agent))
    for label, text in (("Markdown", md), ("JSON", js), ("prompt", prompt(agent)["body"])):
        assert "human_decision_required" in text and "Unable to determine" in text, f"{label}: claim-label rule missing"
