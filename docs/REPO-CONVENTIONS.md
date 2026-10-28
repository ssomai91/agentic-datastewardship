# Repository Conventions

## Directory purpose

| Directory | Contents |
|---|---|
| `agents/factory/` | Agent Contracts (and later prompts) for the Agent Factory layer — the agents that design, review, evaluate and build other agents. |
| `agents/operational/` | Agent Contracts for operational stewardship agents (Definition & CDE, Assurance Reviewer). Each has passed the Agent Factory process but remains `Draft` until the Project Owner approves it. |
| `contracts/` | Machine-readable Agent Contracts (JSON/YAML), one per agent, validated against `schemas/agent-contract.schema.json`. |
| `schemas/` | Shared JSON Schemas: contract, handoff, evidence, material claim and quality issue; `schemas/outputs/` holds one output schema per agent. |
| `evals/` | Evaluation scenario suites per agent (happy path, missing evidence, conflicting evidence, authority-boundary tests, etc.), plus recorded runs: `evals/factory-runs/` (Factory scenarios and design rounds) and `evals/definition-and-cde-runs/` (agent evaluation passes). |
| `examples/` | Synthetic example inputs/outputs only. No confidential or production data. |
| `prompts/` | Builder draft system prompts. A prompt promoted to `.claude/agents/` must stay identical to its draft here (checked by tests). |
| `tools/` | Deterministic code: schema registry, cross-reference checks, the coverage-trace validator, the Definition & CDE harness and its mock glossary, and `tools/assurance/` (stand-ins for the Assurance Reviewer's build preconditions; see its README). |
| `fixtures/` | Synthetic fixtures for evaluations (for example the mock glossary). |
| `.claude/agents/` | The Claude subagent prompt for each agent, derived from its contract (`docs/AUTHORITY-CHAIN.md`). |
| `.dmbok-work/` | Working files of the DMBOK2 alignment pipeline: reader and verifier outputs, merged rows. Reference only, no agent authority. |
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


## Governance decisions

Project-level decisions (approval roles, evidence retention, DMBOK scope, data-quality taxonomy) are recorded in [GOVERNANCE-DECISIONS.md](../GOVERNANCE-DECISIONS.md).

