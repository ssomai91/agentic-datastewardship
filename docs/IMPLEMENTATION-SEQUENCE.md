# Implementation Sequence

## Status: DRAFT — pending Data Steward / project owner approval

This document is a planning artefact, not an implementation authorization. It sets out the recommended, phase-by-phase build sequence for the Agent Factory and the operational stewardship agents, synthesised from the independent per-candidate classification and review pass summarised below.

**No agent contract files may be created until this document has been reviewed and approved by the human Data Steward / project owner.** Concretely, until that approval is recorded:

- Nothing is to be written under `agents/factory/`, `agents/operational/`, `contracts/`, `prompts/`, or `schemas/` (beyond an initial empty skeleton, per Phase 0).
- No Claude Agent Builder run, no Agent Contract draft, and no prompt draft is to be produced from this sequence.
- Phase 0 and 0b (repository skeleton, schema/template hardening, and naming the accountable human roles) may proceed, because they are documentation and scaffolding, not agent artefacts — but even the schemas should be treated as provisional until sign-off.

This is not a new rule invented for this document — it is this repository's own existing rule, stated in three places:

- `README.md`: *"Human approval is required before moving into implementation."*
- `docs/REPO-CONVENTIONS.md`: *"Nothing goes here [`agents/operational/`] until it has passed the Agent Factory and been approved."*
- `HANDOFF.md`'s Decision Model: production/governance decisions require human approval, and the Architect "must not implement an agent automatically."

This sequence document is itself a governance decision about *how* implementation will proceed. It therefore falls under the same gate. Approving it authorises Phase 0/0b scaffolding to begin in earnest and the Factory build (Phase 1 onward) to be scheduled — it does not itself approve any individual Agent Contract; each of those still goes through the Architect → Risk Reviewer → Eval Designer → Builder pipeline and its own human sign-off later.

---

## How this document relates to `BUILD-BACKLOG.md`

`BUILD-BACKLOG.md` set out a reasonable phase skeleton (Phase 0 repo setup → Phase 1 architecture validation → Phase 2 shared contracts → Phase 3 build the Factory → Phase 4 test the Factory → Phase 5 build first operational agent → Phase 6 controlled evaluation → Phase 7 orchestration). This document **keeps that skeleton** but revises its contents in several places where an independent review of each candidate agent's proposed design found the original backlog, or the Architect's own first-pass submissions against it, to be incomplete or to need a different order. The corrections are called out explicitly, in place, rather than left implicit:

| Backlog item | What the backlog said | What changes here, and why |
|---|---|---|
| P2-01 (contract schema) | Lists 11 baseline fields | **Corrected/extended.** The schema must also enforce a `status` field, a mandatory `not_responsible_for` section, a `permitted_tools` table with per-tool access mode and an explicit deny-list, an `output_schema`, a handoff `receives`/`returns` block, and a bounded confidence-label enum — every reviewed candidate contract was found to be missing at least one of these, and several of the gaps were safety-relevant, not cosmetic. |
| (not present) | No equivalent item | **Added.** Phase 0b: an approved Data-Quality-Dimension taxonomy and named human accountable roles are new, hard blocking prerequisites surfaced by review, not in the original backlog at all. |
| P3-01 – P3-04 (build all four Factory agents as one phase) | Built as a block, then tested together in Phase 4 | **Reordered.** Architect and Risk Reviewer are built and hardened as a checking pair first (Phase 1), because Risk Reviewer's independence only has value once it exists to catch exactly the self-review failure the Architect's own first submission exhibited. Eval Designer and Builder follow only once that pair is stable (Phase 2). |
| Architect's own recommendation on Eval Designer (`merge`) | — | **Overridden.** The independent review rejected folding Eval Designer's test-authoring into Risk Reviewer's critique (self-review conflict of interest) or into Builder alone. Eval Designer stays a distinct step — but a lightweight, template-driven one, not a heavyweight agent with its own tools. |
| Architect's own recommendation on Claude Agent Builder (`merge_or_overlap_with: [architect]`) | — | **Rejected.** Merging Builder into the Architect would destroy the one independent checkpoint between an approved design and what actually ships. Builder stays separate, split into a deterministic-templating half and a narrowly bounded generative-drafting half, writing only to a staging path. |
| P4-01 (test Factory on Definition & CDE capability) | "Review whether the factory recommends an agent and whether its scope is appropriately narrow." | **Sharpened.** This test now has a concrete, falsifiable acceptance bar: the Factory must independently produce the tool allow/deny-list fix this review found missing (blocking the real Qlik glossary write/delete/status-change tools), not just a generic "seems narrow enough" judgement. |
| Phase 5 ("Assurance Reviewer **or** Definition & CDE Agent") | Left as an either/or, "final choice requires architecture review" | **Resolved.** Definition & CDE Agent is recommended as the first operational agent, not Assurance Reviewer — see the dedicated section below. This also corrects `HANDOFF.md`'s suggested sequence step 8, which implied building Assurance Reviewer before any producer agent exists. |
| Phase 7 (Orchestration) | "Design multi-agent routing... define case state... define stopping conditions" | **Split and gated further.** The capability is divided into a deterministic Case Routing & State Engine and a separately-governed AI-assisted Intake Classifier; before either is built, this repo needs a decision on system-of-record (bespoke store vs. an existing case-management platform) and on who may set `human_approval` or close a case. |
| Future backlog list | "Each item must pass through the Agent Factory before implementation." | **Unchanged and reaffirmed.** Nothing in this review found reason to bypass that rule for definition-conflict detection, CDE completeness review, lineage-gap detection, etc. |

Everything else in `BUILD-BACKLOG.md` (the repository structure, the P2-02/P2-03 handoff and evidence schemas, the P4-02/P4-03 test cases, the Phase 6 evaluation dimensions) is **confirmed as-is** and carried forward into the phases below without change.

---

## Recommended build sequence

### Phase 0 — Repository scaffolding and hardened shared schemas
*(corrects and extends BUILD-BACKLOG P0-01, P2-01–P2-03)*

1. Create the directory structure already specified in `BUILD-BACKLOG.md` P0-01 (`agents/factory/`, `agents/operational/`, `contracts/`, `evals/`, `examples/`, `schemas/`, `prompts/`, `tests/`, `docs/`) and confirm the naming conventions in `docs/REPO-CONVENTIONS.md`.
2. Author `schemas/agent-contract.schema.json` off `AGENT-CONTRACT-TEMPLATE.md`, but make the following fields **mandatory**, not optional — every one of these was found missing from at least one reviewed candidate's first-pass design, and several of the omissions were flagged as safety-relevant rather than cosmetic:
   - `status` — Draft / Review / Approved.
   - `not_responsible_for` — an explicit exclusion list, not just a `responsible_for` list.
   - `permitted_tools` — a table of `{tool, purpose, access_mode}`, plus an explicit `prohibited_tools` deny-list. Prose assurances such as "has no write access" are not sufficient; the schema must force a tool-by-tool binding.
   - `authoritative_sources` — an enumerated list of named systems/documents, not a free-text description.
   - `output_schema` — what the agent actually hands downstream.
   - A handoff `receives` / `returns` block (`case_id`, `evidence_bundle`, `next_agent`), consistent with `schemas/agent-handoff.schema.json`.
   - A bounded confidence/status enum on every material conclusion: `Supported / Partially supported / Unsupported / Contradictory / Unable to determine` (this is already `HANDOFF.md`'s Confidence Policy — the schema should make it structurally unavoidable rather than a convention agents can silently skip).
3. Author `schemas/agent-handoff.schema.json` and `schemas/evidence.schema.json` per BUILD-BACKLOG P2-02/P2-03, unchanged.

**Exit criteria:** schemas exist, validate against a hand-written example contract, and are themselves reviewed by a human before any real Agent Contract is drafted against them.

### Phase 0b — Governance prerequisites not in the original backlog
*(new)*

Two blocking prerequisites surfaced repeatedly across the reviews and are not satisfied by anything currently in this repository:

1. **Name the accountable human roles.** Several reviewed contracts referred to an implicit "human governance owner" (Factory-tier sign-off after Architect + Risk Reviewer) or an unbound "correct human owner" (operational-tier approval gates) without ever naming who that is. Before Phase 1 begins, the project owner should confirm: who holds Factory-tier design sign-off; whether that is the same person as the Data Steward for operational-tier sign-off; and who holds override authority when a Risk Reviewer or Assurance Reviewer finding is contested.
2. **Approve a Data-Quality-Dimension taxonomy** (completeness, accuracy, timeliness, consistency, validity, uniqueness, or whatever the organisation's own set is) as a standalone, versioned governance document. This is a hard blocking dependency for the Data Quality Agent (Phase 7) — without it, that agent has nothing authoritative to classify against and will default to general industry knowledge presented as if it were internal policy, which is precisely what this system's non-goals prohibit.

Neither of these requires an agent. Both are short documents a human can produce or point to. They are placed here, ahead of Phase 1, because later phases depend on them and it is cheaper to resolve them now than to discover the gap mid-build.

### Phase 1 — Build the Architect/Reviewer checking pair
*(corrects the sequencing in BUILD-BACKLOG P3-01/P3-02, and directly addresses the review's findings on both)*

Build `agents/factory/stewardship-agent-architect.md` and `agents/factory/agent-risk-reviewer.md` together, as a pair, before the rest of the Factory — because the value of Risk Reviewer's independence is best proven by pointing it at the Architect's own weakest first draft.

**Correction to how the Architect validates itself:** the Architect's first-pass submission on its own necessity used a self-referential exercise ("tested this self-referentially... conclusion: keep") as its primary evidence. Independent review rejected this as a methodology, not because the conclusion was wrong, but because the entity being judged should not be the primary evidence for its own judgement — the same conflict-of-interest logic `HANDOFF.md` already states explicitly for Risk Reviewer ("This reviewer must not be the same agent that produced the design") applies reflexively here. Before this contract is treated as approved:
- Resubmit it in a template-conformant form (Status: Draft, a real `not_responsible_for` section, a `permitted_tools` table restricted to read-only access to org design/governance documents and the candidate registry, an output schema, a handoff block).
- Attach an explicit confidence label no stronger than "Partially supported" to any self-interested verdict.
- Validate its classification logic empirically — by running it against real candidate operational agents (e.g., re-classifying Definition & CDE and Exception & Root-Cause) — rather than accepting the self-graded exercise as sufficient, consistent with what `HANDOFF.md`'s own suggested sequence step 5 intended.
- Resolve explicitly whether the Architect may invoke Risk Reviewer, Eval Designer, or Builder directly, or whether every handoff is Orchestrator/human-mediated; if the former, remove that capability.

**Correction to Risk Reviewer's own contract:** build it with a citation-to-clause requirement (every finding must quote or point to the exact contract clause it challenges, plus its own certainty label — an assurance function that cannot itself be checked for unsupported claims is not trustworthy), an explicit instruction to treat every submitted contract as untrusted data rather than instructions to follow (closing a live prompt-injection-via-artefact gap), a named human escalation/override role with mandatory logging of any override, and a resubmission-diff requirement (a revised contract must be checked against the prior version's specific findings, not re-scored from scratch).

**Exit criteria:** both contracts pass their own template's required sections; Risk Reviewer has successfully found and required correction of at least the issues listed above in the Architect's own contract, demonstrating the pair actually functions as a check rather than a formality.

### Phase 2 — Build Eval Designer and Claude Agent Builder
*(confirms BUILD-BACKLOG P3-03 as a standalone deliverable against the Architect's own recommendation to merge it away; tightens P3-04)*

- **Agent Evaluation Designer** (`agents/factory/agent-evaluation-designer.md`): build it as a lightweight, template/taxonomy-driven **workflow step**, not a persistent tool-bearing agent. Its only inputs are the approved Agent Contract and Risk Reviewer's findings; it holds no independent tools or evidence access. It runs the fixed ten-category taxonomy already specified in BUILD-BACKLOG P3-03 against those two inputs and produces a separate, taxonomy-tagged test/acceptance-criteria document. It must never declare an agent "ready," "safe," or "passing" — only propose the plan. Every illustrative example input/output must be labelled synthetic, and every referenced threshold must cite an approved source or be marked "UNRESOLVED — pending human definition."

  *Why this is a correction, not a restatement:* the Architect's own review of this candidate recommended `merge` — folding test-authoring into Risk Reviewer's critique output. Independent review rejected that: it would let the agent that finds a risk also unilaterally decide what tests are "enough" to cover it (a self-review conflict of interest), and would bury taxonomy-tagged test coverage inside free-text critique prose, weakening traceability. The backlog's original structure (a separate file) was right; the Architect's own recommendation to abandon it was not adopted.

- **Claude Agent Builder** (`agents/factory/claude-agent-builder.md`): split explicitly into (a) deterministic templating of structural fields (schemas, tool lists, permission policy) rendered directly off the approved contract, and (b) a narrow, bounded generative-drafting pass for prompt wording and failure-behaviour prose, which **consumes** Eval Designer's test specification rather than regenerating its own. Its own write permissions are scoped to a staging/drafts path only — never directly into `agents/operational/` or `contracts/`, which `docs/REPO-CONVENTIONS.md` reserves for artefacts that have already passed the Factory and been approved. Every generated artefact set must ship with a field-to-prompt coverage trace (each contract field mapped to the prompt passage implementing it) so scope creep beyond the approved contract is machine-checkable, not dependent on a reviewer noticing it unaided.

  *Why this is a correction:* the Architect's first-pass review named "architect" itself as a merge/overlap target for Builder. Independent review rejected this outright — merging Builder into Architect would let the same actor that writes a contract also write the deployed prompt implementing it, destroying the one independent checkpoint between "what was approved" and "what actually ships," and directly contradicting `HANDOFF.md`'s statement that "The Architect must not implement an agent automatically."

**Exit criteria:** both artefacts exist, template-conformant; Builder's output includes a coverage trace on a test run; nothing in Builder's permission list touches `agents/operational/` or `contracts/`.

### Phase 3 — Test the Factory end to end
*(extends BUILD-BACKLOG P4-01/P4-02/P4-03 with sharper, falsifiable acceptance criteria)*

Run the full Architect → Risk Reviewer → Eval Designer → Builder pipeline against the same three scenarios BUILD-BACKLOG already specifies, with concrete pass conditions added:

- **P4-01, Definition & CDE capability:** the Factory's output must, on its own, produce the tool allow/deny-list this review found missing — specifically, it must flag and exclude the real write/delete/status-change Qlik glossary tools (`qlik_create_glossary_term`, `qlik_update_glossary_term`, `qlik_delete_glossary_term`, `qlik_update_term_status`, `qlik_create_glossary_term_links`, and related create-glossary/category tools) from the permitted set, restricting it to the read-only search/get tools. If the Factory does not catch this unaided, it is not ready.
- **P4-02, "Settlement Date null for settled transactions":** the Factory must recommend a deterministic process, not an agent — confirming it is not reflexively agent-happy.
- **P4-03, six-month exception root-cause analysis:** the Factory's output must match the reconciled design for Exception & Root-Cause (Phase 7 below): a thin hypothesis-synthesis agent consuming a curated evidence packet, not a standalone agent with independent multi-system read access.

**Exit criteria:** all three pass; any miss is fed back into Phase 1/2 contract fixes before proceeding, not patched ad hoc in Phase 4.

### Phase 4 — Build the first operational agent: Definition & CDE Agent
*(resolves BUILD-BACKLOG Phase 5's "Assurance Reviewer or Definition & CDE Agent" — see the dedicated recommendation section below for the full reasoning)*

Build `agents/operational/definition-and-cde-agent.md` with the concrete fixes review identified applied at build time, not deferred:

- An explicit `permitted_tools` allow-list: `qlik_search_glossary_terms`, `qlik_get_glossary_term`, `qlik_get_glossary_categories`, `qlik_get_glossary_term_links`, `qlik_get_full_glossary_export` — and an explicit deny-list naming every write/delete/status-change glossary tool in the connected toolset.
- An enumerated `authoritative_sources` list (named glossary/catalog systems, named policy repositories), explicitly excluding unstructured email/Teams/chat content unless promoted into a named register.
- The approved CDE-criteria policy document (from Phase 0b, or a placeholder pending it) named as a required input, never model-supplied.
- A source-attribution requirement on every AI-drafted candidate definition: which clauses are verbatim from a cited source versus model-paraphrased or added.
- The term-meaning boundary against the (not-yet-built) Context Agent and the definition-authority handoff to the (not-yet-built) Mapping & Lineage Agent written as binding handoff-contract fields, not deferred to prose.

Run it standalone first, with no Context Agent or Mapping & Lineage handoff wired, to isolate its evaluation.

### Phase 5 — Controlled evaluation of Definition & CDE Agent
*(BUILD-BACKLOG Phase 6, reordered to follow immediately after the agent it evaluates, using synthetic data only)*

Score against the seven dimensions BUILD-BACKLOG already specifies — evidence traceability, boundary adherence, false-inference rate, escalation behaviour, schema compliance, reproducibility, human usefulness — using the test cases Eval Designer authored for this capability in Phase 2. No confidential or production data.

### Phase 6 — Build the second operational agent: Assurance Reviewer
*(corrects `HANDOFF.md`'s suggested sequence step 8, which placed Assurance Reviewer before any producer agent)*

Only once Definition & CDE Agent (and ideally one more producer agent) has real, evaluated outputs to review — resolving Assurance Reviewer's own identified testability gap: its evidence requirements are entirely other agents' output packs, so it cannot be meaningfully evaluated against synthetic stubs alone in the way a producer agent can.

Apply Assurance Reviewer's required fixes at build time: default to static, read-only inspection of pre-assembled evidence packs (no live query/execute access without separate justification); a named case-status field write as its gating mechanism, with a named human override role and mandatory audit logging of every override; an explicit default coverage policy of 100% review of every material-conclusion pack (any sampling/triage rule requires separate, documented human approval — it is not something the agent may decide for itself); and adoption of the `CLAIM / STATUS / EVIDENCE / ASSUMPTIONS / RISK / ACTION REQUIRED` output schema already sketched in `ARCHITECTURE.md`, including an explicit "Unable to determine" status.

### Phase 7 — Build the remaining operational producer agents incrementally
*(BUILD-BACKLOG's Future Backlog and remaining Candidate Operational Agents, each passed through the now-proven Factory pipeline and evaluated by Assurance Reviewer before going live)*

Each of the following was reviewed as `redesign`, not a plain `keep` — the capability survives, but only with the fixes below applied in its contract before it is built:

- **Mapping & Lineage Agent:** a narrow, scoped evidence-retrieval interface rather than direct simultaneous read access to schema catalogs, mapping specs, code repositories, and lineage tooling; an explicit prohibition on querying or sampling underlying production data values; the deterministic lineage/graph tool named as a hard, owned dependency with a defined "Unable to determine" fallback if unavailable; and an explicit reconciliation with Assurance Reviewer's own "inspect lineage consistency" charter (Assurance Reviewer audits this agent's conclusions rather than duplicating the analysis independently).
- **Data Quality Agent:** build only once the Phase 0b taxonomy is approved; resolve the internal contradiction in the original design between "consume, don't re-derive Mapping & Lineage's evidence" and an independent schema/DDL evidence requirement by routing physical-field grounding exclusively through Mapping & Lineage's output; narrow "identify control owner" to surfacing an owner field already present verbatim in upstream evidence, never inferring a plausible name from role/domain pattern-matching; require any reference to exception history to come only from Exception & Root-Cause's output, never independently queried.
- **Investment Operations Context Agent:** kept as a single, bounded, zero-decision-authority capability — the Architect's own recommendation to split it three ways (into Orchestrator, Definition & CDE, and Mapping & Lineage) is **rejected**, because folding it into the Orchestrator would breach the Orchestrator's own charter to "route rather than dominate" and not become the primary expert. Scope it explicitly to operational/lifecycle/platform/process knowledge, excluded from governed term/CDE meaning (Definition & CDE's exclusive territory, via a binding handoff, not a prose recommendation); enforce the INTERNAL/GENERAL/INFERENCE/OPEN QUESTION labelling structurally via a required source-citation field; invoke it as a service call from whichever agent needs it, never absorb it into Orchestrator routing logic.
- **Exception & Root-Cause Agent:** neither the original design (independent simultaneous read access to exception logs, change logs, lineage metadata, and quality-control history) nor the Architect's alternative (dissolve it into an unnamed "workflow" coordinated by the Orchestrator) is adopted. Build a named, narrow, low-permission agent that performs hypothesis-synthesis only from a curated evidence packet assembled from Mapping & Lineage, Data Quality, and Context Agent outputs — no independent read access to raw logs. Before finalising the upstream clustering step as deterministic, confirm whether real exception records are structured codes or free text; if free text, add an explicit, tagged AI-assisted clustering sub-step rather than silently folding it into "deterministic."

Order these by the same criteria used to pick the first agent (scope narrowness, low production authority, testability without depending on unbuilt agents) — Mapping & Lineage before Data Quality and Exception & Root-Cause, since both of the latter depend on it.

### Phase 8 — Orchestration, last
*(corrects and gates BUILD-BACKLOG Phase 7 / `HANDOFF.md` step 12)*

Only after at least two operational agents (Definition & CDE plus Assurance Reviewer, at minimum) have independently passed evaluation. Before building anything:

1. Split the capability into (a) a deterministic Case Routing & State Engine and (b) a separately-governed, human-overridable AI-assisted Intake Classifier — do not build one combined "Orchestrator agent."
2. Resolve identity/role-binding for who may set `human_approval` or close a case (a convention is not an access control).
3. Define the case log's data-handling, retention, and access policy — preserving evidence for traceability means it will necessarily carry copies of sensitive Investment Operations content.
4. Check whether an existing enterprise case-management/ITSM platform should be system of record before building a bespoke case-state store — this environment has a connected ServiceNow surface, which is exactly the kind of existing infrastructure the project's own principle of avoiding unnecessary parallel build-out (keep the agent/system set minimal) argues for reusing rather than duplicating.

---

## First operational agent recommendation: Definition & CDE Agent

**Recommendation: build Definition & CDE Agent first, not Assurance Reviewer.** This resolves the either/or `BUILD-BACKLOG.md` left open in Phase 5, and corrects the ordering implied by `HANDOFF.md`'s suggested sequence (which listed "Build Assurance Reviewer" at step 8, ahead of "build one operational agent" at step 9).

**Why not Assurance Reviewer, despite `HANDOFF.md` naming it early:** Assurance Reviewer's entire function is to audit *other agents' outputs* — its evidence requirements are producer-agent output packs. Independent review of its own design explicitly noted it "cannot be meaningfully evaluated until stub/mock output packs in the eventual schema of [the producer agents] exist" — a chicken-and-egg problem that undermines the "strong testability" criterion BUILD-BACKLOG Phase 5 itself sets as a selection criterion. It also still carries open architectural questions (gating/override authority, coverage policy, output-schema adoption) rather than concrete, mechanical fixes — building it first would mean building against a moving target.

**Why Definition & CDE Agent satisfies BUILD-BACKLOG Phase 5's own stated criteria cleanly:**
- *Narrow scope:* locate, compare, and flag conflicts/gaps in business definitions and CDE evidence — a single, well-bounded evidence domain.
- *Low production authority:* read-only search/get tools only; every output is a labelled draft; no write, approve, or assign capability.
- *Useful early value:* glossary conflict/gap/CDE-evidence review is immediately useful in isolation — it does not need the Context Agent or Mapping & Lineage handoffs to produce value, so those can be deferred to later iterations without blocking it.
- *Strong testability:* fixtures for term-search/conflict/synonym/CDE-gap scenarios can be built now, without depending on any other unbuilt agent's schema.

**Additional reason specific to this review:** Definition & CDE Agent also doubles as the cleanest acceptance test for the Factory pipeline itself (see Phase 3, P4-01 above). The concrete permission fix it needs — blocking the real Qlik glossary write/delete/status-change tools this environment exposes alongside the read tools it needs — is a verifiable, unambiguous proof point that Architect + Risk Reviewer + Builder actually catch and remediate an excessive-permissions finding before build, rather than a subjective judgement about "does this feel narrow enough."

---

## Cut, merged, and deferred capabilities

No candidate capability was recommended for outright removal. One was deferred and restructured:

| Candidate | Disposition | Where addressed |
|---|---|---|
| Stewardship Orchestrator | **Deferred and split**, not cut. Both the Architect and the independent reviewer agreed this should not be a freestanding autonomous LLM agent — its rules are control-flow and guardrail behaviour, expressible as a routing table, a case-state log, and a hard status gate. Build deferred until the case-type taxonomy, routing table, and handoff/evidence schemas exist and are human-approved, and until at least two operational agents have independently passed evaluation. | Phase 8 |

All other reviewed candidates (Architect, Risk Reviewer, Eval Designer, Claude Agent Builder, Context Agent, Definition & CDE, Mapping & Lineage, Data Quality, Exception & Root-Cause, Assurance Reviewer) are kept, none merged into another — but every one carries a `redesign` verdict requiring the specific fixes described in its phase above before its contract is treated as build-ready. "Keep the capability" and "the submitted design is approvable as-is" were found, in every single case reviewed, to be two different questions with two different answers.

---

## System-wide risks carried into this sequence

These patterns recurred across multiple independently reviewed candidates and should be treated as standing constraints on every phase above, not just the phase where they were first noticed:

1. **Self-review / conflict-of-interest pattern.** The Architect grading its own necessity, and the original proposal to fold Eval Designer's test-authoring into Risk Reviewer, are two instances of the same failure mode: the entity producing a conclusion should not also be the entity certifying it. Check every Factory-tier and operational-tier boundary for this before approving a contract.
2. **Prompt-injection-via-artefact risk.** Risk Reviewer, Assurance Reviewer, and Claude Agent Builder all consume content authored by another agent or a case. Every one of their contracts must state that this content is untrusted data to evaluate, not instructions to follow.
3. **Unscoped tool/permission surfaces.** The single most concrete, recurring finding. None of the original candidate designs enumerated a permitted/prohibited tools table, and this environment's actual connected toolset (e.g., the Qlik glossary MCP's create/update/delete/status-change tools sitting alongside the read tools these agents need) makes this a live risk, not a hypothetical one. Phase 0's schema hardening exists specifically to close this gap structurally.
4. **Inconsistent confidence labelling.** Several reviewed agents — including the reviewers themselves — were not originally required to label their own conclusions' certainty, which is inconsistent with this system's non-goal of never hiding uncertainty.
5. **Undocumented or unnamed human accountability roles.** Recurs across nearly every contract. Phase 0b exists to close this before it propagates further.
6. **Evidence-preservation vs. data-handling.** Preserving evidence for traceability means case logs and stewardship packs will carry copies of sensitive Investment Operations content. No reviewed contract yet specifies retention, access control, or redaction rules for that stored evidence — this must be resolved no later than Phase 8, and ideally before Phase 4.
7. **Sequencing/dependency risk.** Several agents assume prerequisite artefacts that don't yet exist (the DQ taxonomy, real producer-agent outputs, an approved routing table). Building out of dependency order risks hard-coding assumptions against a system that doesn't yet exist in documented form — which is the specific reason for the phase ordering above.
8. **Duplicated-responsibility / divergent-answer risk at agent boundaries** (Context Agent vs. Definition & CDE on term meaning; Mapping & Lineage vs. Assurance Reviewer on lineage consistency; Data Quality vs. Exception & Root-Cause on exception-history evidence). Each of these is resolved above as a binding handoff-contract requirement, not a prose recommendation — prose recommendations were exactly what the first-pass designs relied on, and exactly what review found insufficient.

---

## Open questions for the human Data Steward / project owner

These are left open deliberately rather than decided unilaterally in this document, because they are governance decisions, not design details:

1. Should Risk & Governance Reviewer (build-time) and Assurance Reviewer (run-time) remain two separately built agents indefinitely, or should a single capability parameterised by evidence-access mode be required to be seriously costed and rejected in writing first?
2. Who, by name or title, holds Factory-tier governance sign-off, and who holds override authority when a Risk Reviewer or Assurance Reviewer finding is contested?
3. What is the case-log and evidence-pack data-handling policy — what may be persisted, who may read a given case's stored evidence, and what is the retention/redaction rule?
4. Should the eventual case-routing function be built as a bespoke store, or should an existing enterprise case-management/ITSM platform serve as system of record?
5. Does an approved, versioned Data-Quality-Dimension taxonomy already exist anywhere in the organisation's governance documentation, or does one need to be authored now?
6. What is the actual structure of exception/control-failure records — structured codes or free text? This determines whether Exception & Root-Cause's upstream clustering step can remain purely deterministic.
7. What coverage policy should Assurance Reviewer operate under in practice — unconditional 100% review, or a documented, human-approved sampling rule for high-volume periods — and who may approve a deviation from full coverage?

---

## Approval record

| Field | Value |
|---|---|
| Prepared by | Claude Code, synthesising the independent per-candidate classification and review pass |
| Reviewed by | *(pending — Data Steward / project owner)* |
| Approval status | **Not approved.** No agent contract files exist yet. |
| Effect of approval | Authorises Phase 0/0b scaffolding to proceed in earnest and the Factory build (Phase 1) to be scheduled. Does **not** pre-approve any individual Agent Contract — each still requires its own Architect → Risk Reviewer → Eval Designer → Builder pass and its own human sign-off. |
