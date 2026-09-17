# Proposed Multi-Agent Architecture

## Overview

```text
                         HUMAN DATA STEWARD
                                |
                                v
                    STEWARDSHIP ORCHESTRATOR
                                |
      +-------------------------+-------------------------+
      |                         |                         |
      v                         v                         v
DOMAIN CONTEXT          DEFINITION & CDE          MAPPING & LINEAGE
      |                         |                         |
      +-------------------------+-------------------------+
                                |
                                v
                         DATA QUALITY
                                |
                                v
                     EXCEPTION / ROOT CAUSE
                                |
                                v
                       ASSURANCE REVIEWER
                                |
                                v
                         HUMAN DATA STEWARD
```

The diagram is conceptual.

The final design must be derived from actual stewardship workflows, not from this diagram alone.

---

# Layer 1 — Agent Factory

## Stewardship Agent Architect

### Purpose

Design the smallest useful agent architecture for a stewardship capability.

### Must answer

- What problem is being solved?
- Should it be an agent at all?
- What evidence does it need?
- What decisions are permitted?
- What decisions require humans?
- What tools are needed?
- What risks exist?
- What are its handoffs?
- How will it be evaluated?

---

## Agent Risk & Governance Reviewer

### Purpose

Challenge the Architect's proposed design.

### Focus

- excessive permissions;
- unclear decision rights;
- unsafe autonomy;
- hallucination risk;
- evidence gaps;
- duplicated responsibility;
- privacy/security concerns;
- inability to explain conclusions;
- dependency on undocumented assumptions.

---

## Agent Evaluation Designer

### Purpose

Define how the proposed agent will be tested before deployment.

### Test types

- happy path;
- conflicting evidence;
- missing evidence;
- incomplete data;
- ambiguous terminology;
- incorrect mapping;
- unsupported inference;
- unauthorised decision attempt;
- tool unavailable;
- downstream dependency unknown.

---

## Claude Agent Builder

### Purpose

Turn approved Agent Contracts into implementation artefacts.

### Output

- prompt;
- agent metadata;
- input schema;
- output schema;
- tool list;
- permission policy;
- handoff configuration;
- evaluation cases;
- example inputs;
- example outputs;
- failure behaviour.

---

# Layer 2 — Operational Stewardship Agents

## Stewardship Orchestrator

### Purpose

Coordinate multi-step stewardship workflows.

### Rules

- route rather than dominate;
- minimise unnecessary agents;
- preserve evidence;
- maintain case state;
- surface unresolved questions;
- never turn partial evidence into a final decision.

---

## Investment Operations Context Agent

### Purpose

Provide domain context.

### Content areas

Potentially:

- trading;
- orders;
- executions;
- transactions;
- positions;
- TBOR;
- IBOR;
- ABOR;
- valuation;
- NAV;
- reconciliation;
- regulatory reporting;
- enterprise data products;
- relevant source platforms.

### Required distinction

Every answer should distinguish:

```text
INTERNAL DOCUMENTED POSITION
GENERAL INDUSTRY CONTEXT
INFERENCE
OPEN QUESTION
```

---

## Definition & CDE Agent

### Purpose

Support semantic stewardship.

### Responsibilities

- locate existing definitions;
- compare definitions;
- identify conflicts;
- identify synonyms;
- identify ownership gaps;
- identify missing definitions;
- identify CDE evidence;
- prepare candidate definitions for human review.

### Prohibited

- final definition approval;
- assigning owners;
- declaring CDE status without approval.

---

## Mapping & Lineage Agent

### Purpose

Understand movement and transformation of data.

### Responsibilities

- source-target mapping analysis;
- transformation identification;
- lineage completeness;
- dependency mapping;
- downstream impact;
- mapping-definition consistency.

### Key question

> Did the meaning survive the transformation?

---

## Data Quality Agent

### Purpose

Convert approved business expectations into candidate controls.

### Responsibilities

- identify relevant quality dimension;
- propose quality rule;
- propose deterministic test;
- generate candidate SQL;
- identify required threshold;
- identify required evidence;
- identify control owner;
- link test back to business definition.

### Prohibited

- setting business thresholds;
- approving controls.

---

## Exception & Root-Cause Agent

### Purpose

Analyse patterns in quality exceptions.

### Responsibilities

- cluster exceptions;
- identify recurring characteristics;
- correlate failures with source/process changes;
- identify common upstream dependencies;
- propose hypotheses;
- identify evidence required to confirm root cause.

### Prohibited

- declaring root cause without sufficient evidence;
- resolving operational incidents directly.

---

## Assurance Reviewer

### Purpose

Challenge all material conclusions.

### Responsibilities

- verify claims against evidence;
- identify unsupported conclusions;
- identify assumptions;
- identify contradictions;
- identify missing approval;
- inspect SQL or logic;
- inspect lineage consistency;
- verify that agent boundaries were respected.

### Preferred output

```text
CLAIM:
...

STATUS:
Supported / Partially supported / Unsupported / Contradictory

EVIDENCE:
...

ASSUMPTIONS:
...

RISK:
...

ACTION REQUIRED:
...
```

---

# Long-term concept: Stewardship as Code

Where appropriate, governance artefacts should move toward structured and version-controlled representations.

Possible artefacts:

```text
definitions/
critical-data-elements/
mappings/
lineage/
quality-rules/
data-contracts/
controls/
exceptions/
evidence/
```

This does not mean converting every governance document into code.

It means ensuring important governance relationships are machine-readable where that improves traceability, testing or change-impact analysis.

---

# Example end-to-end flow

```text
Question:
Why are settled trades missing settlement dates?

        |
        v
Orchestrator
        |
        +--> Context Agent
        |       |
        |       +--> What is the relevant lifecycle context?
        |
        +--> Definition Agent
        |       |
        |       +--> What does Settlement Date mean?
        |
        +--> Mapping Agent
        |       |
        |       +--> Where does the value originate and transform?
        |
        +--> Quality Agent
        |       |
        |       +--> What approved rule should detect this?
        |
        +--> Exception Agent
        |       |
        |       +--> Is there a recurring pattern?
        |
        v
Assurance Reviewer
        |
        v
Human Data Steward
```
