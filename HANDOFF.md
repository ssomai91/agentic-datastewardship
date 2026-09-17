# Claude Code Handoff

## Project

**Name:** AI-Augmented Investment Operations Data Stewardship  
**Primary user:** Data Steward  
**Development approach:** Multi-agent, evidence-led, human-governed  
**Current phase:** Architecture and agent definition

---

## Objective

Design a governed multi-agent system that helps a Data Steward:

- understand Investment Operations context;
- define and maintain data meaning;
- identify and manage critical data elements;
- assess source-to-target mappings;
- reason about lineage;
- define and test data-quality controls;
- analyse quality exceptions;
- identify recurring patterns and likely root causes;
- prepare evidence for stewardship decisions;
- identify unresolved questions requiring SME or Data Owner input.

The system must improve the quality and scalability of stewardship work without transferring accountability from humans to AI.

---

## Important non-goals

Do not design a system that:

- autonomously approves business definitions;
- autonomously designates critical data elements;
- changes production data;
- changes production mappings;
- changes production quality thresholds;
- makes governance decisions;
- acts as the Data Owner;
- resolves operational incidents on behalf of operations teams;
- hides uncertainty;
- presents inferred organisational policy as fact.

---

## Decision model

Use this authority model consistently:

### AI may

- inspect approved artefacts;
- compare evidence;
- identify gaps;
- detect inconsistencies;
- suggest candidate definitions;
- suggest candidate mappings;
- suggest candidate data-quality rules;
- generate candidate SQL or tests;
- cluster recurring exceptions;
- produce root-cause hypotheses;
- identify missing lineage;
- prepare stewardship packs;
- recommend escalation.

### Human approval required

- business definition approval;
- CDE designation;
- ownership assignment;
- quality thresholds;
- acceptance of data-quality risk;
- production changes;
- governance decisions;
- policy interpretation where material;
- final root-cause determination where evidence is incomplete.

---

## Architecture principle

Do not create an agent because a task sounds intelligent.

Classify each capability as one of:

1. Human responsibility
2. Deterministic process
3. AI-assisted workflow
4. Specialised AI agent
5. Multi-agent workflow

Choose the least complex implementation that is safe and effective.

---

## Evidence policy

Every material agent output must distinguish between:

- **Authoritative internal evidence**
- **General industry context**
- **Agent inference**
- **Open question**
- **Human decision required**

Agents must never blur these categories.

---

## Confidence policy

Agents must not use vague confidence language without evidence.

Preferred pattern:

```text
STATUS: Supported / Partially supported / Unsupported / Contradictory

EVIDENCE:
- source 1
- source 2

ASSUMPTIONS:
- assumption 1

OPEN QUESTIONS:
- question 1

HUMAN ACTION REQUIRED:
- action
```

---

## First implementation target

Build the **Stewardship Agent Architect** before building operational stewardship agents.

Its purpose is to analyse candidate capabilities and produce agent contracts.

The Architect must not implement an agent automatically.

Its output is a design recommendation.

---

## Initial Agent Factory

### 1. Stewardship Agent Architect

Responsibilities:

- analyse proposed stewardship capabilities;
- decide whether they require an agent;
- identify inputs and outputs;
- define boundaries;
- identify evidence requirements;
- identify required human decisions;
- define handoffs;
- produce Agent Contracts.

### 2. Agent Risk & Governance Reviewer

Responsibilities:

- challenge proposed agent designs;
- identify excessive authority;
- identify hallucination risks;
- identify missing evidence controls;
- identify privacy/security concerns;
- identify overlapping responsibilities;
- recommend tighter constraints.

This reviewer must not be the same agent that produced the design.

### 3. Agent Evaluation Designer

Responsibilities:

- create evaluation scenarios;
- define expected safe behaviour;
- define failure cases;
- define evidence requirements;
- define escalation behaviour.

### 4. Claude Agent Builder

Responsibilities:

- convert approved Agent Contracts into Claude-compatible implementation artefacts;
- generate system prompts;
- generate schemas;
- generate test cases;
- generate tool-permission requirements;
- generate handoff definitions.

It must not alter an approved Agent Contract without surfacing the change.

---

## Candidate Operational Agents

These are hypotheses to be validated.

### Stewardship Orchestrator

Coordinates the workflow.

Must not become the primary expert.

### Investment Operations Context Agent

Provides evidence-backed domain context.

Must distinguish internal organisational knowledge from general industry knowledge.

### Definition & CDE Agent

Works on business definitions, synonyms, terminology conflicts, ownership gaps and critical data element evidence.

Must not approve definitions.

### Mapping & Lineage Agent

Examines source-target mappings, transformations, lineage gaps and downstream dependencies.

### Data Quality Agent

Translates approved requirements into candidate data-quality rules, tests and controls.

Must not set business thresholds.

### Exception & Root-Cause Agent

Clusters quality failures and generates evidence-backed hypotheses about recurring process weaknesses.

### Assurance Reviewer

Independently reviews evidence, assumptions, unsupported claims, contradictions and missing approvals.

---

## Required implementation behaviour

Claude Code should:

1. keep each agent definition in a separate file;
2. use a shared Agent Contract schema;
3. include explicit `not_responsible_for` sections;
4. include escalation conditions;
5. include human approval requirements;
6. include evidence requirements;
7. include tool permissions;
8. include test scenarios;
9. version all material changes;
10. avoid hidden implicit handoffs between agents.

---

## Initial operating mode

Use:

> **Read → Analyse → Recommend**

Do not design around:

> Read → Decide → Change

Autonomous production changes are out of scope for the initial system.

---

## Suggested implementation sequence

1. Define Agent Contract schema.
2. Build Stewardship Agent Architect.
3. Build Agent Risk & Governance Reviewer.
4. Build Agent Evaluation Designer.
5. Test Agent Factory on the candidate operational agents.
6. Review outputs manually.
7. Approve minimum viable operational architecture.
8. Build Assurance Reviewer.
9. Build one operational agent.
10. Run controlled evaluation.
11. Iterate.
12. Add orchestration only after individual agents behave reliably.

---

## Success criteria

The project succeeds if it produces a system where:

- agents know their boundaries;
- humans know where accountability sits;
- claims are traceable;
- unsupported assumptions are visible;
- quality controls can be linked back to definitions;
- mappings can be linked back to meaning;
- lineage can be linked to downstream impact;
- exceptions can be analysed as recurring patterns;
- agents can be evaluated independently;
- governance can be applied to the agents themselves.
