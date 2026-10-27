# Authority Chain: Markdown → JSON → Claude Prompt

Each agent exists in three forms. They are not equals. When they disagree, the higher one wins and the lower one is a defect to fix.

| Rank | Artefact | Location | Role |
|---|---|---|---|
| 1 | Agent Contract (Markdown) | `agents/factory/*.md`, `agents/operational/*.md` | **Source of truth.** Human-reviewed and approved. Follows `AGENT-CONTRACT-TEMPLATE.md`. Any change to scope, authority, evidence rules or escalation is made here first. |
| 2 | Machine-readable contract (JSON) | `contracts/<agent>.contract.json` | **Derived** from rank 1. Validated against `schemas/agent-contract.schema.json`. Used by tests and tooling, never edited to change behaviour on its own. |
| 3 | Claude subagent prompt | `.claude/agents/<agent>.md` | **Derived** from rank 1. The invokable subagent: frontmatter (`name`, `description`, `tools`) plus a system prompt. Its `tools` must not exceed the contract's `permitted_tools`, and it names its governing contract and version. |

## Rules

1. **Change flow is top-down.** Edit the Markdown contract, bump its version and change log, then regenerate or update the JSON, then the prompt. Never fix behaviour only in the prompt.
2. **The prompt may restate but never widen.** It may be shorter than the contract. It may not grant tools, authority, or approval rights the contract withholds.
3. **Approval attaches to the Markdown contract.** An agent is in draft until its contract is approved and a JSON contract exists (`docs/REPO-CONVENTIONS.md`). Nothing under `agents/operational/` is approved until it has passed the Agent Factory.
4. **Drift is a defect.** A mismatch in name, version, tools or authority between the three forms is a bug, reported against the lower-ranked artefact.
5. **Supporting JSON is not a contract.** `docs/dmbok2-citations.json` and `.dmbok-work/` are reference and working material. They carry no agent authority.

## What is enforced today

- `tests/test_contracts.py` pairs each Markdown contract with its JSON contract and validates the JSON against the schema.
- `tests/test_agent_consistency.py` checks, for all five agents, that:
  - the JSON contract's name, version and status equal the Markdown contract's;
  - the prompt's frontmatter `name` matches its file, and it has a description and an explicit `tools` list;
  - the prompt's tools do not exceed what the agent may hold (read-only, plus `Write` for the Builder only);
  - the prompt names its governing contract path, and any version it cites equals the contract's;
  - none of the three files has mis-encoded characters, and confidence labels match `schemas/material-claim.schema.json`;
  - the Markdown `Returns` block and the JSON `handoff_contract.returns` list the same fields, and cover every field `schemas/agent-handoff.schema.json` requires (including `request` and `claims`);
  - every prompt tells the agent to return `claims` with evidence ids.
- `tests/test_outputs.py` checks that each Factory agent's output schema (`schemas/outputs/`) has exactly the fields in its contract's `output_schema`.

## Known gaps

- The Stewardship Agent Architect's output schema has no `claims` field because its contract does not list one. Claims travel inside its embedded `handoff`.
- The Definition & CDE prompt is limited by the contract's assumption that no real glossary system is connected (backlog P4-04).