# Build Backlog

## Phase 0 — Repository setup

### P0-01 Create repository structure

Create:

```text
agents/factory/
agents/operational/
contracts/
evals/
examples/
schemas/
prompts/
tests/
docs/
```

**Acceptance criteria**

- structure exists;
- naming conventions documented;
- no production connectivity.

---

## Phase 1 — Architecture validation

### P1-01 Review proposed agent architecture

Read:

- README.md
- HANDOFF.md
- ARCHITECTURE.md
- AGENT-CONTRACT-TEMPLATE.md

Produce:

- `docs/PROPOSED-ARCHITECTURE.md`
- `docs/ARCHITECTURE-RISKS.md`
- `docs/IMPLEMENTATION-SEQUENCE.md`

**Important:** Do not assume the candidate agent list is correct.

---

### P1-02 Classify each proposed capability

For each capability decide:

- human responsibility;
- deterministic process;
- AI-assisted workflow;
- specialised agent;
- multi-agent workflow.

Produce:

`docs/CAPABILITY-CLASSIFICATION.md`

---

## Phase 2 — Shared contracts

### P2-01 Create machine-readable Agent Contract schema

Create:

`schemas/agent-contract.schema.json`

Base it on `AGENT-CONTRACT-TEMPLATE.md`.

Required fields should include at minimum:

- name;
- purpose;
- responsible_for;
- not_responsible_for;
- authoritative_sources;
- permitted_tools;
- prohibited_actions;
- evidence_requirements;
- escalation_conditions;
- human_approval_required_for;
- success_criteria.

---

### P2-02 Create shared handoff schema

Create:

`schemas/agent-handoff.schema.json`

Suggested fields:

```yaml
case_id:
request:
agent:
status:
findings:
evidence:
assumptions:
open_questions:
human_action_required:
next_agent:
```

---

### P2-03 Define evidence model

Create:

`schemas/evidence.schema.json`

Suggested concepts:

- source_id;
- source_type;
- title;
- location;
- authority_level;
- extracted_fact;
- direct_or_inferred;
- timestamp;
- notes.

---

## Phase 3 — Build Agent Factory

### P3-01 Stewardship Agent Architect

Create:

`agents/factory/stewardship-agent-architect.md`

Use the Agent Contract Template.

The Architect should:

1. understand the business problem;
2. classify the capability;
3. separate reasoning from authority;
4. identify dependencies;
5. produce an Agent Contract;
6. challenge its own initial design;
7. return a recommendation.

Possible recommendations:

- CREATE AGENT
- CREATE DETERMINISTIC PROCESS
- KEEP AS HUMAN RESPONSIBILITY
- MERGE WITH EXISTING AGENT
- REDESIGN REQUIRED

---

### P3-02 Agent Risk & Governance Reviewer

Create:

`agents/factory/agent-risk-reviewer.md`

It must challenge designs produced by the Architect.

It must not rewrite silently.

Output:

```yaml
design_status:
risks:
authority_issues:
evidence_issues:
permission_issues:
overlap:
recommended_changes:
approval_required:
```

---

### P3-03 Agent Evaluation Designer

Create:

`agents/factory/agent-evaluation-designer.md`

It should create tests for:

- normal input;
- missing evidence;
- conflicting evidence;
- hallucination pressure;
- attempted unauthorised decision;
- tool failure;
- malformed data;
- ambiguous terminology.

---

### P3-04 Claude Agent Builder

Create:

`agents/factory/claude-agent-builder.md`

It converts approved contracts into Claude implementation artefacts.

Do not allow it to broaden scope beyond the approved contract.

---

## Phase 4 — Test the Agent Factory

### P4-01 Test on Definition & CDE capability

Run the Factory against:

> Support a Data Steward in locating, comparing and preparing business definitions and critical data element evidence.

Review whether the factory recommends an agent and whether its scope is appropriately narrow.

---

### P4-02 Test on deterministic quality check

Run the Factory against:

> Check whether Settlement Date is null for settled transactions.

Expected architectural challenge:

This may be primarily a deterministic SQL/data-quality rule, not a standalone agent.

---

### P4-03 Test on root-cause analysis

Run the Factory against:

> Analyse six months of quality exceptions to identify recurring patterns and candidate root causes.

Evaluate whether an AI-assisted or agent-based approach is justified.

---

## Phase 5 — Build first operational agent

Do not build the Orchestrator first.

Recommended initial candidate:

**Assurance Reviewer** or **Definition & CDE Agent**

Reason:

- narrow scope;
- low production authority;
- useful early value;
- strong testability.

Final choice requires architecture review.

---

## Phase 6 — Controlled evaluation

Create synthetic test data and examples.

Do not use confidential production data during initial development.

Evaluation dimensions:

- evidence traceability;
- boundary adherence;
- false inference rate;
- escalation behaviour;
- schema compliance;
- reproducibility;
- human usefulness.

---

## Phase 7 — Orchestration

Only after at least two agents pass independent evaluation:

- design multi-agent routing;
- define case state;
- define handoff persistence;
- define stopping conditions;
- define human approval checkpoints.

---

# Future backlog

Potential capabilities for later assessment:

- definition conflict detection;
- CDE completeness review;
- mapping-to-definition consistency;
- lineage gap detection;
- data contract generation;
- quality rule generation;
- SQL quality test generation;
- exception clustering;
- recurring defect analysis;
- change-impact analysis;
- domain review pack generation;
- governance action tracking;
- control coverage analysis.

Each item must pass through the Agent Factory before implementation.
