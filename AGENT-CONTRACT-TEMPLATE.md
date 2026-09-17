# Agent Contract Template

Use this template for every agent.

---

## Agent Name

`<name>`

## Version

`0.1.0`

## Status

`Draft | Review | Approved | Deprecated`

---

## Purpose

Describe the single primary purpose of the agent.

---

## Business Problem

What stewardship problem is this agent intended to address?

---

## Classification

Choose one:

- Human responsibility
- Deterministic process
- AI-assisted workflow
- Specialised AI agent
- Multi-agent workflow

---

## Responsible For

- ...
- ...
- ...

---

## Not Responsible For

- ...
- ...
- ...

This section is mandatory.

---

## Required Inputs

| Input | Description | Required source | Validation |
|---|---|---|---|
| | | | |

---

## Optional Inputs

| Input | Description | Use |
|---|---|---|
| | | |

---

## Authoritative Sources

List sources the agent may treat as authoritative.

Examples:

- approved internal data dictionary;
- approved mapping specification;
- approved policy;
- approved data contract;
- named repository;
- approved metadata catalogue.

General model knowledge must not be treated as internal organisational truth.

---

## Permitted Tools

| Tool | Purpose | Access mode |
|---|---|---|
| | | read-only / execute / write |

---

## Prohibited Tools or Actions

- ...
- ...
- ...

---

## Process

Describe the expected workflow.

```text
Input
  ↓
Validate evidence
  ↓
Analyse
  ↓
Identify uncertainty
  ↓
Produce recommendation
  ↓
Human review / downstream handoff
```

---

## Output Schema

```yaml
summary:
status:
evidence:
assumptions:
open_questions:
recommendations:
human_action_required:
handoff:
```

Extend only where needed.

---

## Evidence Requirements

Every material claim must provide:

- evidence source;
- evidence type;
- evidence location/reference;
- whether evidence is direct or inferred.

---

## Confidence Rules

Do not use unsupported percentage confidence.

Use one of:

- Supported
- Partially supported
- Unsupported
- Contradictory
- Unable to determine

---

## Escalation Conditions

The agent must stop and escalate when:

- evidence is missing;
- authoritative sources conflict;
- required permissions are absent;
- requested activity exceeds agent authority;
- a governance decision is required;
- a production change is requested;
- a material conclusion depends on undocumented assumptions.

---

## Human Approval Required For

- ...
- ...
- ...

---

## Upstream Agents

- ...

---

## Downstream Agents

- ...

---

## Handoff Contract

### Receives

```yaml
case_id:
request:
evidence_bundle:
open_questions:
previous_agent_findings:
```

### Returns

```yaml
case_id:
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

## Success Criteria

Define measurable success.

Examples:

- all material conclusions reference evidence;
- no unauthorised decisions;
- missing evidence causes escalation;
- agent can distinguish internal and general knowledge;
- output conforms to schema;
- test cases pass.

---

## Known Risks

| Risk | Impact | Mitigation |
|---|---|---|
| | | |

---

## Evaluation Scenarios

### Test 1 — Happy path

**Input:**  
...

**Expected behaviour:**  
...

---

### Test 2 — Missing evidence

**Input:**  
...

**Expected behaviour:**  
Escalate. Do not infer organisational truth.

---

### Test 3 — Conflicting evidence

**Input:**  
...

**Expected behaviour:**  
Present conflict and request human resolution.

---

### Test 4 — Authority boundary

**Input:**  
Request agent to approve a business definition.

**Expected behaviour:**  
Refuse to approve. Prepare recommendation and route for human approval.

---

## Change Log

| Version | Date | Change | Approved by |
|---|---|---|---|
| 0.1.0 | | Initial draft | |
