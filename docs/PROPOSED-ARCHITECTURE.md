# Proposed Architecture (Revised)

## Overview

The core operating principle is unchanged:

> **AI proposes → evidence supports → the Data Steward evaluates → the appropriate human owner approves.**

The system remains organised in two layers:

- **Layer 1 — Agent Factory.** Designs and governs the operational agents before any of them touch a real stewardship case. Nothing here inspects Investment Operations evidence; its evidence domain is the organisation's own design principles, non-goals, decision model, and the candidate/agent registry.
- **Layer 2 — Operational Stewardship Team.** Works actual stewardship cases: business definitions, mappings and lineage, data-quality controls, exception patterns, and assurance review — always as recommendations routed to the Data Steward and the relevant human owner, never as autonomous decisions.

This document revises `ARCHITECTURE.md` in light of two rounds of scrutiny: the Stewardship Agent Architect classified all 11 originally proposed candidates against the five-way model (Human responsibility / Deterministic process / AI-assisted workflow / Specialised AI agent / Multi-agent workflow), and an independent Agent Risk & Governance Reviewer then challenged every one of those classifications. The result is not a smaller headcount — every one of the 11 original capabilities survives in some form — but it is a materially tighter set of contracts. Every single candidate, including the Architect's and the Risk Reviewer's own, was sent back with a **redesign** verdict; none was approved to build exactly as first proposed, and one (the Stewardship Orchestrator) is deferred rather than built now.

## Revised architecture: the minimum viable set

### Layer 1 — Agent Factory

All four Factory roles are kept, but two proposed mergers were examined and rejected, and every surviving contract needs concrete tightening before it is handed to Claude Agent Builder.

The **Architect** and **Risk & Governance Reviewer** stay as two separate agents specifically because they must not grade the same work: an agent should not be the primary evidence for its own necessity, and a design should not be checked only by the entity that produced it. Both contracts, however, were themselves found to fall short of this repository's own `AGENT-CONTRACT-TEMPLATE.md` — missing a Status field, a Not Responsible For section, a Permitted Tools table, an Output Schema, and a Handoff Contract block — and must be resubmitted in template-conformant form, with the Architect's necessity verdicts carrying an explicit confidence label rather than being asserted as settled.

The **Agent Evaluation Designer** was originally proposed for merging into the Risk Reviewer (plus Claude Agent Builder for implementation). That merge is rejected: folding test-plan authorship into the Risk Reviewer would let the same agent that finds a risk also single-handedly decide whether its own test coverage is sufficient, a self-review conflict, and would bury taxonomy-tagged coverage inside free-text critique prose instead of a distinct, auditable artefact. It is kept as a genuinely lightweight step — no tools, no evidence access beyond the approved contract and the Risk Reviewer's findings, applying a fixed ten-category taxonomy rather than inventing its own — which is why it is classified as an **AI-assisted workflow**, not a standing agent.

**Claude Agent Builder** is kept but narrowed. Most of what it produces (schemas, tool lists, permission policy) is mechanically derivable from an approved contract and should be deterministic templating, not free-form generation; only the prompt wording and failure-behaviour prose genuinely benefit from drafting, and that drafting must consume the Evaluation Designer's already-approved test spec rather than invent its own. Its write access is restricted to a staging path — never directly into the approval-gated `agents/operational/` or `contracts/` directories — and every artefact set must ship with a field-to-prompt coverage trace so scope creep beyond the approved contract is machine-checkable rather than left to a reviewer's attention.

### Layer 2 — Operational Stewardship Team

Six of the seven original operational candidates are kept as Specialised AI agents, each tightened around a concrete permissions or evidence-boundary gap; the seventh, the Orchestrator, is deferred.

The **Investment Operations Context Agent** was originally proposed for a three-way split into the Orchestrator, Definition & CDE Agent, and Mapping & Lineage Agent. That merge is rejected: the overlap with Definition & CDE is real only at the narrow term-definition edge, the bulk of the Context Agent's stated scope (trading/settlement lifecycle, TBOR/IBOR/ABOR, NAV, reconciliation, source-platform architecture) has no home in Definition & CDE's charter, and folding it into the Orchestrator would make the Orchestrator "the primary expert" — something its own operating rule explicitly forbids. It is kept as a single, bounded, zero-decision-authority capability, with the term/CDE-meaning boundary against Definition & CDE written as a binding handoff contract rather than left as a prose recommendation.

**Definition & CDE Agent**, **Mapping & Lineage Agent**, **Data Quality Agent**, and **Assurance Reviewer** are all kept as distinct Specialised AI agents — each owns an evidence domain and a decision boundary that would be blurred by merging it into a neighbour. Each needs concrete, mechanical fixes before build: an explicit tool allow/deny list for Definition & CDE Agent (any real glossary/catalog system it eventually integrates with is likely to include write, update, delete, and status-change tools alongside the read tools it actually needs — the actual system has not yet been selected); a scoped evidence-retrieval interface and a named deterministic lineage-tool dependency for Mapping & Lineage Agent, in place of open multi-system browsing; an approved Data-Quality-Dimension taxonomy as a hard blocking prerequisite, not an assumed input, for Data Quality Agent, plus resolution of a contradiction between "consume Mapping & Lineage's evidence" and an independent schema/DDL read path; and a named, audited gating mechanism plus a default 100%-coverage policy for Assurance Reviewer.

**Exception & Root-Cause Agent** is kept, but in a reconciled, narrower form. Its original design — independent, simultaneous read access to exception logs, change logs, lineage metadata, and quality-control history, with its own causal-reasoning identity — duplicates Mapping & Lineage's dependency-mapping work and gives it a larger permission footprint than any other candidate. The Architect's own proposed fix (dissolve it into an unnamed workflow coordinated by the Orchestrator) is also rejected, because that either breaches the Orchestrator's "not the primary expert" rule or leaves the causal narrative with no accountable author. The reconciled design keeps a named, low-permission agent that performs hypothesis-synthesis only, from a curated evidence packet assembled by Mapping & Lineage, Data Quality, and Context Agent — with no independent read access to raw logs.

The **Stewardship Orchestrator** is the one candidate not carried into the current build. Its stated rules — route rather than dominate, preserve evidence, maintain case state, surface unresolved questions, never turn partial evidence into a final decision — are control-flow and guardrail behaviour, expressible as a routing table, a case-state log, and a hard human-approval gate, not tasks that need generative judgment over evidence content. It is therefore split into a deterministic Case Routing & State Engine (code, not an agent) and a separately governed, human-overridable AI-assisted Intake Classifier, and its build is deferred until: the case-type taxonomy, routing table, and handoff/evidence schemas exist and are human-approved; an identity-bound owner for the `human_approval` and case-close actions is named; a data-handling and retention policy is set for the case log (which will carry copies of sensitive Investment Operations evidence); whether an existing enterprise case-management platform should be system of record is evaluated; and at least two operational agents have independently passed evaluation — consistent with this project's own build sequencing.

### Disposition table

| Candidate | Layer | Original classification | Final disposition | Why (short) |
|---|---|---|---|---|
| Stewardship Agent Architect | Factory | Specialised AI agent | **Kept**, redesigned | Self-graded its own necessity instead of the independent validation the project's own sequence specifies; contract must be resubmitted template-conformant with a confidence label, not asserted as settled. |
| Agent Risk & Governance Reviewer | Factory | Specialised AI agent | **Kept**, redesigned | Sound separation-of-duties design, but needs citation-to-clause discipline on its own findings, a named human override role, and explicit untrusted-input handling. |
| Agent Evaluation Designer | Factory | AI-assisted workflow (Architect proposed merging into Risk Reviewer + Claude Builder) | **Kept** as its own step; proposed merge **rejected** | Merging into Risk Reviewer would let the risk-finder also grade its own test coverage — a self-review conflict — and would bury tagged coverage inside free-text critique. |
| Claude Agent Builder | Factory | AI-assisted workflow (Architect proposed merging into Architect) | **Kept**, narrowed/split; proposed merge **rejected** | Merging into the Architect would collapse the design/implementation separation the pipeline exists to enforce. Split into deterministic templating + a narrow, bounded drafting pass. |
| Stewardship Orchestrator | Operational | Deterministic process | **Deferred**, decomposed | Its rules are control-flow/state/guardrail behaviour, not generative judgment. Split into a deterministic Case Routing & State Engine + a separate AI-assisted Intake Classifier; blocked on missing prerequisite artefacts and human-role bindings. |
| Investment Operations Context Agent | Operational | AI-assisted workflow (Architect proposed a 3-way split into Orchestrator, Definition & CDE, Mapping & Lineage) | **Kept** as one capability; proposed split **rejected** | Most of its scope has no home in Definition & CDE's charter, and folding it into the Orchestrator would make the Orchestrator "the primary expert," which its own rule forbids. |
| Definition & CDE Agent | Operational | Specialised AI agent | **Kept**, redesigned | Legitimate evidence-gathering-and-drafting work; needs an explicit tool allow/deny list against real connected glossary tools, an authoritative-sources list, and source-attribution on drafted text. |
| Mapping & Lineage Agent | Operational | Specialised AI agent | **Kept**, redesigned | Genuine semantic-comparison task; needs a scoped evidence-retrieval interface in place of open multi-system browsing, and a named lineage-tool dependency with a defined fallback. |
| Data Quality Agent | Operational | Specialised AI agent | **Kept**, redesigned | Needs an approved DQ-dimension taxonomy as a hard prerequisite, a resolved contradiction over schema/DDL access, and a narrowed "control owner" function (surface evidence only, never infer). |
| Exception & Root-Cause Agent | Operational | Multi-agent workflow | **Kept**, narrowed | Original independent multi-system access duplicated Mapping & Lineage and oversized its footprint; kept as a named, low-permission agent doing hypothesis-synthesis from a curated evidence packet only. |
| Assurance Reviewer | Operational | Specialised AI agent | **Kept**, redesigned | The one genuinely independent challenge function; needs a named, audited gating mechanism and a default 100%-review-coverage policy. |

## Revised conceptual flow

```text
LAYER 1 — AGENT FACTORY (build-time; produces an approved Agent Contract)

        Capability or case need identified
                        |
                        v
         STEWARDSHIP AGENT ARCHITECT
        (drafts a candidate Agent Contract)
                        |
                        v
      AGENT RISK & GOVERNANCE REVIEWER
    (independently challenges the contract)
                        |
                        v
         AGENT EVALUATION DESIGNER
   (drafts a taxonomy-tagged test/acceptance plan)
                        |
                        v
           CLAUDE AGENT BUILDER
 (deterministic templating + narrow, bounded
        prompt/failure-behaviour draft)
                        |
                        v
        HUMAN GOVERNANCE SIGN-OFF
      (approves the contract before build)


LAYER 2 — OPERATIONAL STEWARDSHIP TEAM (run-time; works a case)

                 HUMAN DATA STEWARD
                        |
     (routing is human-mediated for now — the
      Stewardship Orchestrator is deferred; see
      "Removed or merged" below)
                        |
      +-----------------+-----------------+
      |                 |                 |
      v                 v                 v
CONTEXT AGENT   DEFINITION & CDE AGENT   MAPPING & LINEAGE AGENT
(process/platform    (owns term/CDE          (scoped evidence-
 knowledge only)        meaning)               retrieval only)
      |                 |                 |
      +-----------------+-----------------+
                        |
                        v
               DATA QUALITY AGENT
        (blocked on an approved DQ taxonomy)
                        |
                        v
          EXCEPTION & ROOT-CAUSE AGENT
   (hypothesis synthesis from a curated evidence
              packet — no independent reads)
                        |
                        v
               ASSURANCE REVIEWER
     (100% review coverage by default; gates
           the case pack with an audit log)
                        |
                        v
                 HUMAN DATA STEWARD
```

As with the original diagram, this is conceptual. The final design must still be derived from actual stewardship workflows, not from the diagram alone.

## Removed or merged from the original 11-candidate proposal

Nothing was cut outright — every one of the 11 originally proposed capabilities survives in this revision, in some form. What changed is shape, not headcount:

- **Stewardship Orchestrator — removed from the operational agent roster as a standalone, freestanding LLM agent.** Its behaviours (routing, case-state, evidence preservation, a human-approval gate) are control-flow and guardrail logic, not generative judgment over evidence content, so building it as an autonomous "Operational" agent was rejected. It is decomposed into a deterministic Case Routing & State Engine and a separately governed AI-assisted Intake Classifier, and its build is deferred behind missing prerequisite artefacts (case-type taxonomy, routing table, handoff/evidence schemas), undefined human-role bindings for approval and override, and an unresolved case-log data-handling policy.
- **Claude Agent Builder — narrowed out of its original "one generative agent does everything" shape.** The structural half of its output (schemas, tool lists, permission policy) is mechanically derivable from an approved contract and was removed from the agent's discretionary latitude in favour of deterministic templating; only a narrow, bounded drafting pass over prompt and failure-behaviour prose remains agentic, and even that must consume — not re-derive — the Evaluation Designer's test spec.
- **Agent Evaluation Designer into Agent Risk & Governance Reviewer (plus Claude Agent Builder) — proposed, and rejected.** The Architect's original recommendation was to fold test-plan authorship into the Risk Reviewer's critique. This was rejected because it would let the same agent that finds a risk also single-handedly judge whether its own test coverage of that risk is sufficient — a self-review conflict — and because it would dissolve a distinct, taxonomy-tagged, auditable test artefact into free-text critique prose, weakening traceability.
- **Investment Operations Context Agent split three ways into Stewardship Orchestrator, Definition & CDE Agent, and Mapping & Lineage Agent — proposed, and rejected.** The overlap with Definition & CDE Agent is real, but limited to the narrow edge of formal term/CDE meaning; the majority of the Context Agent's scope (trading and settlement lifecycle, TBOR/IBOR/ABOR, NAV computation, reconciliation, source-platform architecture) has no documented home in Definition & CDE's responsibilities. Routing that residual scope into the Orchestrator was rejected because it would make the Orchestrator "the primary expert," directly contradicting its own "route rather than dominate" rule.
