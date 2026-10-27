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
- Prompt-to-contract consistency (version, tools, authority) is **not** checked yet. It is backlog item P2-04.

## Known gaps

- Several `.claude/agents/*.md` files contain mis-encoded punctuation (for example `â€”` for an em dash). Re-save them as UTF-8 without BOM when P2-04 adds the consistency checks.
- The Definition & CDE prompt is limited by the contract's assumption that no real glossary system is connected (backlog P4-04).
