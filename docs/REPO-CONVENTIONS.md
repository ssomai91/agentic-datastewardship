# Repository Conventions

## Directory purpose

| Directory | Contents |
|---|---|
| `agents/factory/` | Agent Contracts (and later prompts) for the Agent Factory layer — the agents that design, review, evaluate and build other agents. |
| `agents/operational/` | Agent Contracts for approved operational stewardship agents. Nothing goes here until it has passed the Agent Factory and been approved. |
| `contracts/` | Machine-readable Agent Contracts (JSON/YAML), one per agent, validated against `schemas/agent-contract.schema.json`. |
| `schemas/` | Shared JSON Schemas: `agent-contract.schema.json`, `agent-handoff.schema.json`, `evidence.schema.json`. |
| `evals/` | Evaluation scenario suites per agent (happy path, missing evidence, conflicting evidence, authority-boundary tests, etc.), authored per `AGENT-CONTRACT-TEMPLATE.md`'s Evaluation Scenarios section. |
| `examples/` | Synthetic example inputs/outputs only. No confidential or production data. |
| `prompts/` | Draft system prompts, prior to being finalised into an approved Agent Contract. |
| `tests/` | Automated tests (schema compliance, evaluation-harness runs). |
| `docs/` | Architecture, risk, sequencing and governance documentation that is not itself an agent artefact. |

## Naming

- Agent files: kebab-case matching the agent's `Agent Name` in its contract, e.g. `stewardship-agent-architect.md`, `definition-and-cde-agent.md`.
- Schema files: `<subject>.schema.json`.
- Every agent must have a matching entry in `contracts/` once approved — a markdown contract under `agents/` without a corresponding machine-readable contract is still in draft.

## No production connectivity

Nothing in this repository connects to production systems, production data, or production credentials. `examples/` and `evals/` use synthetic data only.

## Authority

Markdown contract, JSON contract and Claude prompt form a fixed chain of authority; see [AUTHORITY-CHAIN.md](AUTHORITY-CHAIN.md).

