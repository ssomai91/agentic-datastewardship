# AI-Augmented Data Stewardship — Claude Code Handoff

## Purpose

This repository is intended to design and progressively build a multi-agent AI support system for an Investment Operations Data Steward.

The system is not intended to replace the Data Steward, Data Owner, SMEs, operational teams, or governance forums.

The core operating principle is:

> **AI proposes → evidence supports → the Data Steward evaluates → the appropriate human owner approves.**

The project should favour trustworthy, auditable, explainable stewardship over maximum automation.

---

## Status of this build

`agents/factory/`, `agents/operational/`, `contracts/`, and `schemas/` are fully populated on this branch, even though `docs/REPO-CONVENTIONS.md` and `docs/IMPLEMENTATION-SEQUENCE.md` both state that nothing should be written under those directories before Data Steward / project owner approval. This is a deliberate choice on this branch, not an oversight: it builds a proposed, draft solution end-to-end — every Agent Contract carries `status: Draft`, and none carry `status: Approved` — so that concrete, reviewable artefacts exist for the Data Steward to evaluate before committing to the full governance-approval cycle set out in `docs/IMPLEMENTATION-SEQUENCE.md`. Populating these directories here does **not** constitute Data Steward approval of any individual agent; each contract still requires its own Architect → Risk Reviewer → Eval Designer → Builder pass and its own human sign-off before it can move beyond `Draft`.

---

## Business context

The target role is a Data Steward within Investment Operations Data.

The stewardship scope includes responsibilities such as:

- data quality and fitness-for-purpose;
- business definitions;
- critical data elements;
- data dictionaries;
- documentation;
- data-quality rules and controls;
- source-to-target mapping;
- lineage;
- data contracts;
- root-cause analysis;
- recurring quality-pattern identification;
- upstream dependency management;
- governance reporting;
- continuous improvement.

The role is explicitly a **data governance role rather than an operational incident-resolution role**.

The intended AI architecture should therefore help the steward reason across definitions, quality, lineage, mappings, evidence and controls.

---

## Key design principles

1. Human accountability remains explicit.
2. Agents must not invent business definitions or policy.
3. Internal authoritative evidence takes precedence over general knowledge.
4. Unsupported conclusions must be flagged, not silently inferred.
5. Every material conclusion should be traceable to evidence.
6. Use the minimum permissions required.
7. Prefer read-and-recommend before read-write or autonomous action.
8. Separate agents by responsibility, evidence and decision rights.
9. Avoid creating agents when deterministic automation is more appropriate.
10. Keep the agent set as small as possible while preserving useful separation of concerns.

---

## Initial architecture

The first layer is an **Agent Factory** used to design and govern the operational agents.

### Agent Factory

- Stewardship Agent Architect
- Agent Risk & Governance Reviewer
- Agent Evaluation Designer
- Claude Agent Builder

The second layer is the **Operational Stewardship Team**.

### Operational agents

- Stewardship Orchestrator
- Investment Operations Context Agent
- Definition & CDE Agent
- Mapping & Lineage Agent
- Data Quality Agent
- Exception & Root-Cause Agent
- Assurance Reviewer

These are starting hypotheses, not fixed requirements.

The Stewardship Agent Architect must independently assess whether all of them are required.

---

## Recommended repository structure

```text
.
├── README.md
├── HANDOFF.md
├── ARCHITECTURE.md
├── AGENT-CONTRACT-TEMPLATE.md
├── BUILD-BACKLOG.md
├── agents/
│   ├── factory/
│   └── operational/
├── contracts/
├── evals/
├── examples/
├── schemas/
├── prompts/
├── tests/
└── docs/
```

---

## First Claude Code task

Read all markdown files in this repository.

Then:

1. Analyse the proposed architecture.
2. Identify unnecessary, overlapping, missing or overly broad agents.
3. Recommend the minimum viable agent set.
4. Do not generate production agents yet.
5. Produce the proposed architecture as `docs/PROPOSED-ARCHITECTURE.md`.
6. Produce a gap/risk analysis as `docs/ARCHITECTURE-RISKS.md`.
7. Produce a recommended implementation sequence as `docs/IMPLEMENTATION-SEQUENCE.md`.

Human approval is required before moving into implementation.

> Terminology: "Data Steward" is used as a neutral title. DMBOK2 stewardship definitions are general industry context only; see `docs/STEWARDSHIP-FRAMEWORK.md`.
