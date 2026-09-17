# Architecture Risks

This document consolidates the independent-review findings raised against each agent in the `minimum_viable_set`, states the specific mitigation each risk requires before that agent can be built, and then covers cross-agent risks that no single agent's contract can resolve on its own. It closes with the open questions that require explicit human-steward input before implementation proceeds.

Every agent below carries a `redesign` verdict from independent review, not a clean `keep`. None of the findings argue for cutting a capability — they argue that the *contract* for each capability is not yet safe to hand to Claude Agent Builder. "Keep the capability, fix the contract" is the pattern that repeats across all ten entries.

---

## 1. Stewardship Agent Architect (`architect`)

**Layer:** Factory · **Verdict:** redesign

### Risks raised

- **Authority issue — self-approval / self-grading.** The Architect determined its own necessity by running its own classification checklist on itself ("tested this self-referentially"), which is the exact self-review conflict of interest the project's own separation-of-duties rule (stated for the Risk Reviewer) exists to prevent. A confidently-argued "keep" on a self-interested question could be mistaken for a settled position rather than an unreviewed draft, since no `Status` (Draft/Review/Approved) field was attached.
- **Authority issue — unnamed accountable role.** The "human governance owner" who must sign off on any Architect output is referenced but never named as an actual role/title.
- **Authority issue — unclear autonomy boundary.** It is not stated whether the Architect may invoke Risk Reviewer, Eval Designer, or Claude Agent Builder directly, versus every handoff being Orchestrator- or human-mediated. If it can invoke them directly, that is unsafe autonomy at the meta layer.
- **Evidence issue — missing mandatory contract sections.** Measured against `AGENT-CONTRACT-TEMPLATE.md`, the submission has no `Not Responsible For` section, no `Permitted Tools` table (tool / purpose / access mode), no `Output Schema`, and no `Handoff Contract` Receives/Returns block (`case_id`, `evidence_bundle`, `next_agent`). The missing Permitted Tools table directly contradicts the Architect's own charter to answer "what tools are needed."
- **Evidence issue — no confidence label.** The repo's Confidence policy (Supported / Partially supported / Unsupported / Contradictory / Unable to determine) was not applied to the self-interested "keep" verdict, which is precisely the kind of material claim that policy exists to guard against.
- **Hallucination / explainability risk.** The tier-selection argument ("Specialised AI agent" over "AI-assisted workflow") substitutes a persuasive analogy to the Operational agents' "shape" for verifiable evidence about the Architect's actual runtime needs (persistent state, multi-turn tool use) — a plausible-sounding inference presented as a settled conclusion.
- **Overlap issue.** The boundary between the Architect's "lightweight evaluation outline" and Eval Designer's fixed test taxonomy is asserted, not defined, risking duplication or a gap where neither agent authors the contract's mandatory Evaluation Scenarios section.

### Required mitigations

- Resubmit as a template-conformant Agent Contract: `Status: Draft`, a `Not Responsible For` section, a `Permitted Tools` table restricted to **read-only** access to org design/governance documents and the candidate registry (explicitly no production data, no write, no execute), an `Output Schema`, and a `Handoff Contract` Receives/Returns block with `case_id`.
- Attach an explicit Confidence/Status label — no stronger than "Partially supported" — to any necessity verdict about the Architect's own existence.
- **Escalation condition:** re-validate the necessity/classification method by running the Architect against real candidate operational agents (the project's own prescribed validation), not a self-referential exercise; or have Risk Reviewer/a human independently re-run the classification.
- **Tool permission limit:** the Architect must never be granted production or operational-data access; its evidence domain is limited to org design principles, non-goals, decision model, and the candidate registry.
- State explicitly whether the Architect may invoke Risk Reviewer / Eval Designer / Claude Agent Builder directly; if so, remove that capability so all handoffs are Orchestrator- or human-mediated.
- Name the actual human governance owner role/title responsible for final sign-off.
- Define precisely what the "lightweight evaluation outline" pointer contains so it cannot pre-empt Eval Designer's Evaluation Scenarios section.

---

## 2. Agent Risk & Governance Reviewer (`risk-reviewer`)

**Layer:** Factory · **Verdict:** redesign

### Risks raised

- **Authority issue — internally inconsistent decision rights.** `decision_authority` states the reviewer has no power to block anything, yet the agent's own risk list warns that without enforcement the review "becomes a rubber stamp." Whether a `cut`/`redesign` finding is a hard gate on downstream Builder/Eval Designer work, or purely advisory and silently ignorable, is never resolved — which is itself the "unclear decision rights" failure mode this reviewer exists to catch in others.
- **Authority issue — undefined escalation role.** The escalation path names an unspecified "human governance/architecture reviewer" with no defined authority, accountability, or seniority — an undocumented assumption, unlike the operational domain's named "Data Steward."
- **Authority issue — no override/audit trail.** No stated authority for who can override a risk-reviewer finding and let a design proceed anyway, nor any requirement to record that override.
- **Evidence issue — no citation requirement.** Findings are not required to cite the exact contract clause/field being challenged, so the reviewer's own conclusions could be exactly as unsupported/untraceable as the failures it exists to catch in others.
- **Evidence issue — no integrity check on input, no diffing on resubmission.** Nothing detects a truncated/summarized handoff before it reaches the reviewer, and there is no mechanism to verify that a revised contract actually addressed prior findings rather than superficially rewording them.
- **Overlap issue.** The claim that build-time (Risk Reviewer) and run-time (Assurance Reviewer) evidence corpora justify two separate agents is a plausibility argument, not a rigorous test of a cheaper parameterized single-capability alternative, which Principle 10 requires be considered before two agents are built independently. Division of labor with Eval Designer over "unsupported inference" / "unauthorised decision attempt" territory is also unresolved.
- **Hallucination / explainability risk.** No requirement to label its own findings' certainty (e.g., CONFIRMED vs. PLAUSIBLE), and no instruction that the artifact under review is untrusted data rather than instructions to follow — a live prompt-injection-via-artifact risk (a proposed contract's free-text justification could contain text engineered to steer the reviewer toward a favorable verdict).

### Required mitigations

- **Escalation condition:** every finding must quote or precisely cite the specific clause/field of the Agent Contract under review, plus a certainty label (e.g., CONFIRMED/PLAUSIBLE).
- Explicitly name and define the human role that receives escalations and holds override authority; state whether an unresolved `cut`/`redesign` finding is a hard gate on downstream Builder/Eval Designer work or advisory-only, and log every override.
- **Tool permission limit:** read-only access to the proposed Agent Contract and the fixed design principles/non-goals/decision model only — no production or case-evidence access, consistent with least-privilege.
- Explicit instruction that submitted-contract content (including embedded justification text) is untrusted data to be evaluated, never instructions to be followed.
- Before accepting risk-reviewer and assurance-reviewer as two independently built agents, require documented justification for why a single capability parameterized by evidence-access mode was rejected.
- Add a resubmission/diff requirement: a revised contract must be reviewed against the prior version's specific findings, confirming each was addressed rather than re-scored from scratch.
- Add a non-execution / no-live-system-contact constraint, and a note that reviewed contracts may contain sensitive internal detail that must not be treated as an invitation to query any live system.

---

## 3. Agent Evaluation Designer (`eval-designer`)

**Layer:** Factory · **Verdict:** redesign (kept as a distinct step; the Architect's own recommendation to merge it into Risk Reviewer was rejected on review)

### Risks raised

- **Authority issue — silently broadened Risk Reviewer charter.** The originally proposed merge into Risk Reviewer's critique would add test/acceptance-criteria authorship to a charter that is supposed to stay challenge-only, via architectural prose rather than a reviewed contract change.
- **Authority issue — self-review conflict of interest.** Combining "identify the risks" and "define the tests that verify those risks" in one agent removes the independent second check that a separate verifier role provides.
- **Evidence issue — fabricated illustrative data.** Concrete example inputs/outputs across many domain-specific contracts require fabricated illustrative data (sample NAV figures, thresholds, exception clusters); nothing requires that data be labelled synthetic, or that referenced business rules be marked "UNRESOLVED — pending human definition" when not yet approved.
- **Evidence issue — no consistency guarantee.** No requirement that a consistent format/template be applied uniformly across all candidate agents' contracts if test-plan authorship is done ad hoc inside each critique.
- **Overlap issue.** "Same taxonomy" (with Risk Reviewer) does not mean "same task" — Risk Reviewer produces a design-time diagnostic critique of a static document; Eval Designer produces a generative, pre-deployment behavioral-verification artifact. Collapsing them removes a distinct, auditable, taxonomy-tagged artifact and buries test coverage inside free-text critique prose.
- **Hallucination / explainability risk.** Embedding taxonomy-tagged test coverage inside another agent's narrative critique weakens 1:1 traceability from "which of the 10 fixed categories is covered" to an auditable line item.

### Required mitigations

- Keep this as a **distinct, template-driven AI-assisted workflow step** (not a persistent, tool-bearing agent) that runs after Risk Reviewer's findings exist, consuming both the Architect's contract and Risk Reviewer's findings, producing a separate, taxonomy-tagged test/acceptance-criteria document.
- **Tool permission limit:** no tools, no evidence access beyond the approved contract and Risk Reviewer's findings — no production data, no live tool access, regardless of where the function is hosted.
- **Escalation condition:** no deterministic pass/fail criterion can be written for a proposed test case → flag the underlying contract as not yet testable/approvable, rather than inventing one.
- Require every example input/output to be explicitly labelled illustrative/synthetic, and every referenced business threshold to cite an approved source or be marked "UNRESOLVED — pending human definition."
- Explicitly state it may never declare an agent "ready," "safe," "tested," or "passing" — only propose the plan; execution/gating stays a deterministic, human-interpreted process.

---

## 4. Claude Agent Builder (`claude-builder`)

**Layer:** Factory · **Verdict:** redesign

### Risks raised

- **Authority issue — proposed merge with Architect rejected.** `HANDOFF.md` explicitly states the Architect "must not implement an agent automatically." Folding Builder into Architect would let the same actor that wrote the contract also write the deployed prompt implementing it, destroying the one independent check between "what was approved" and "what actually ships."
- **Authority issue — "transcription only" overstates the task.** Turning a bullet-point contract into governing system-prompt prose (refusal wording, tone, handling of unanticipated phrasing) is inherently interpretive, not mechanical transcription. Framing it as pure transcription removes the incentive to add a machine-checkable safeguard against drift.
- **Authority issue — unscoped write permissions.** No concrete tool/permission list for Builder itself is specified, and it is never stated whether Builder may write directly into the approval-gated `agents/operational/` or `contracts/` directories versus only into a drafts/staging path.
- **Evidence issue — templating assumption is unverified.** "Structural artefacts are directly derivable via templating" assumes `schemas/agent-contract.schema.json` and `schemas/agent-handoff.schema.json` already exist in stable form; as of this review, `schemas/`, `contracts/`, `evals/`, `examples/`, and `prompts/` are all empty and the schema-definition backlog items are still open.
- **Overlap issue.** Duplicates "evaluation cases / example outputs" with Eval Designer unless Builder explicitly consumes Eval Designer's scenarios rather than generating its own.
- **Hallucination / explainability risk.** Relying on "transcription only + human review" as the sole safeguard against scope creep is weaker than it looks: a generated prompt can read as faithful while containing a phrase or permission with no corresponding contract field, and a human skimming polished output is the exact "false assurance" failure mode named elsewhere in this review set.

### Required mitigations

- Drop `architect` from `merge_or_overlap_with`; keep Builder strictly downstream of Risk Reviewer + Eval Designer sign-off.
- **Tool permission limit:** write only to a `prompts/` drafts/staging path; never write directly into the approval-gated `agents/operational/` or `contracts/` directories — promotion into those is a human/engineering action.
- Replace "pure transcription" framing with an honest statement that prompt drafting is interpretive, and require a machine-checkable **field-to-prompt coverage map** (each contract field → the prompt passage implementing it, flagging prompt content with no traceable source field) delivered alongside every generated artefact set.
- Split the deterministic-templating half and the AI-assisted-drafting half into two separately-classified items rather than one hybrid label, to keep the audit trail legible.
- State explicitly whether cross-contract (fleet-wide) permission/tool conflict detection is in scope for Builder or belongs to Assurance Reviewer.
- Consume Eval Designer's scenarios instead of generating independent ones; label all example inputs/outputs synthetic.

---

## 5. Investment Operations Context Agent (`context-agent`)

**Layer:** Operational · **Verdict:** redesign (kept as a single bounded capability; the Architect's proposed three-way merge was rejected on review)

### Risks raised

- **Authority issue — role-blurring in the rejected remedy.** Folding this capability into the Orchestrator (as originally proposed) would give the Orchestrator an analytical/explanatory role that conflicts with its own charter ("route rather than dominate"; must not become "the primary expert").
- **Authority issue — escalation is itself a judgment call.** Distinguishing "no source found" vs. "conflicting sources" vs. "sufficient-but-general" has real false-positive/false-negative failure modes; dissolving the agent into an ad hoc "priming step" removes the dedicated contract and escalation triggers that currently bound that judgment without removing the judgment itself.
- **Evidence issue — overstated overlap.** The claim that Definition & CDE Agent is "the heaviest content overlap" is not well supported: Definition & CDE is scoped to formal term/CDE definitions, while most of Context Agent's stated remit (trading/settlement lifecycle, TBOR/IBOR/ABOR, NAV computation, reconciliation, source-platform architecture) has no documented home there.
- **Evidence issue — unspecified enforcement.** The INTERNAL-vs-GENERAL boundary is asserted as needing "tooling enforcement" without specifying what that enforcement mechanism actually is.
- **Overlap issue.** Splitting the capability three ways (orchestrator, definition-cde, mapping-lineage) risks the exact "two independently-tagged, divergent answers" problem cited as the reason to eliminate the standalone agent in the first place — e.g., a term-meaning question could be answered independently by an Orchestrator priming step and by Definition & CDE.
- **Hallucination / explainability risk.** A diffuse, ownerless "context-priming step" is more likely, not less, to drift into a generic "ask-anything" failure mode. If folded into the Orchestrator, an OPEN QUESTION or GENERAL-vs-INTERNAL flag risks becoming invisible routing scaffolding rather than a first-class, human-visible artefact in case state — hiding uncertainty.

### Required mitigations

- Keep this as a **single, bounded, zero-decision-authority capability** — thin agent or shared callable service — with a documented, mutually exclusive scope boundary against Definition & CDE (governed term/CDE meaning stays with Definition & CDE; operational/lifecycle/platform/process knowledge stays here), enforced via a **binding Handoff Contract**, not prose.
- Do **not** implement this as logic embedded in the Orchestrator.
- **Tool permission limit:** enforce the INTERNAL DOCUMENTED / GENERAL INDUSTRY / INFERENCE / OPEN QUESTION labelling structurally (a required citation/source-location field), not by prompt instruction alone, so absence of a valid internal citation forces the GENERAL/INFERENCE/OPEN QUESTION label.
- **Escalation condition:** no authoritative internal source exists → return OPEN QUESTION, never substitute general knowledge presented as fact; internal documentation conflicts → route to Definition & CDE / human steward rather than picking a source.
- Preserve a single, durable, human-visible evidence record for every domain-context answer so escalation triggers remain auditable in case state rather than silently absorbed into routing.

---

## 6. Definition & CDE Agent (`definition-cde`)

**Layer:** Operational · **Verdict:** redesign

### Risks raised

- **Authority issue — permission boundary exists only in prose.** `decision_authority` states "no write access... to the production glossary, CDE register, or ownership records," but this is a narrative promise, not an enumerated tool-level allow/deny list. This environment's connected Qlik glossary MCP surface exposes both read tools and destructive/write tools (`qlik_create_glossary_term`, `qlik_update_glossary_term`, `qlik_delete_glossary_term`, `qlik_update_term_status`, `qlik_create_glossary_term_links`) on the exact object this agent is prohibited from touching — a prose promise does not stop a builder from wiring the full toolset.
- **Authority issue — undefined "implicit approval request."** The escalation trigger for a request that "implicitly asks the agent to approve, finalise, or assign ownership" has no working definition or worked examples, so detection depends entirely on undocumented model judgment.
- **Authority issue — no named source for CDE criteria.** The agent is authorised to assemble CDE evidence against "recognised CDE criteria" but no approved internal policy/register is named as the source of that criteria list; if supplied from general knowledge, that is inventing policy.
- **Evidence issue — no enumerated Authoritative Sources list**, and no grounding/verification mechanism against fabricated-but-plausible citations.
- **Evidence issue — no source-attribution rationale on drafted definitions.** A Steward reviewing a "DRAFT — NOT APPROVED" candidate definition cannot tell which clauses are verbatim from a source versus model-paraphrased or model-added.
- **Overlap issue.** Overlap with Context Agent ("what does X mean") and with Mapping & Lineage ("mapping-definition consistency") is resolved only as a prose recommendation, not a binding Handoff Contract rule — nothing currently stops two agents reaching the Steward with different provenance framing for the same term.
- **Hallucination / explainability risk.** Fabricated-citation risk is named but has no concrete mitigation; there is no separation, in process or output schema, between low-risk retrieval (comparing existing definitions) and higher-risk generative drafting (synthesising a new candidate) — the point where policy-inventing hallucination is most likely.

### Required mitigations

- **Tool permission limit:** add an explicit Permitted Tools table naming real tools — permit `qlik_search_glossary_terms`, `qlik_get_glossary_term`, `qlik_get_glossary_categories`, `qlik_get_glossary_term_links`, `qlik_get_full_glossary_export` (read-only); explicitly **deny** `qlik_create_glossary_term`, `qlik_update_glossary_term`, `qlik_delete_glossary_term`, `qlik_update_term_status`, `qlik_create_glossary_term_links`, `qlik_create_glossary`, `qlik_create_glossary_category`.
- Enumerate a bounded Authoritative Sources list (named glossary/catalog systems, named policy repositories); exclude unstructured email/Teams/chat content as a source unless promoted into a named register.
- Name the source-of-truth artefact for CDE criteria as a required input, not agent-supplied knowledge.
- **Escalation condition:** add a concrete detection rule or worked examples for "implicit approval/ownership-assignment request"; split "definition gap with no fallback" into "no authoritative register exists at all" vs. "register exists but has no entry for this term" (different Steward remediation paths).
- Convert overlap resolution with Context Agent and Mapping & Lineage into a binding Handoff Contract specifying who queries whom first and what provenance label each agent uses.
- Require every AI-drafted candidate definition to include a source-attribution rationale (which clauses are cited vs. paraphrased/added), in addition to the DRAFT label.
- State explicitly that boundary compliance is checked externally by Assurance Reviewer, not self-certified by this agent's own escalation logic.

---

## 7. Mapping & Lineage Agent (`mapping-lineage`)

**Layer:** Operational · **Verdict:** redesign

### Risks raised

- **Authority issue — unscoped, multi-system read footprint.** `decision_authority` grants direct read access across five distinct systems (schema catalog, mapping-spec repo, ETL/SQL/pipeline code, lineage/catalog tool, definitions repo) with no least-privilege interface — broader than any other candidate's footprint.
- **Authority issue — no prohibition on production data content.** Nothing stops the agent from querying or sampling underlying production data values (as opposed to schema, code, and metadata) to empirically test "did the meaning survive the transformation," unnecessarily exposing client/position-level data.
- **Authority issue — unnamed hard dependency.** The fix for the overlap with Exception & Root-Cause (a shared deterministic lineage/graph tool) is asserted but never named as an owned dependency, with no fallback/escalation behaviour defined if that tool is unavailable.
- **Evidence issue — ambiguous definition source.** Evidence may come "from Definition & CDE Agent output OR the governance/glossary repository" — conflating an unapproved candidate source with an approved authoritative one, leaving unclear whether a consistency check may run against a not-yet-approved definition, and at what confidence.
- **Evidence issue — no multi-hop lineage rule**, and no mechanism to detect code/lineage-vs-runtime drift (retrieved artefact may not reflect what is actually deployed).
- **Evidence issue — confidence language not bound to the org's mandated taxonomy** (Supported/Partially supported/Unsupported/Contradictory/Unable to determine).
- **Overlap issue.** Assurance Reviewer's own charter explicitly includes "inspect lineage consistency" — the same subject matter — with no stated reconciliation mechanism (second-order review of this agent's findings, vs. independent duplicate analysis).
- **Hallucination / explainability risk.** The design addresses the false-negative direction (treating undocumented transformation as benign) but not the false-positive direction (misreading complex SQL/ETL logic and asserting a false inconsistency). No required output structure binds each finding to the cited definition text, the cited code excerpt, and the stated semantic gap between them.

### Required mitigations

- **Tool permission limit:** replace open multi-system browsing with a narrow, scoped evidence-retrieval interface (e.g., a single "get mapping evidence bundle" call returning pre-scoped excerpts for a given mapping id) rather than direct agent access to code repositories and catalogs; explicitly prohibit querying/sampling underlying production data values.
- **Escalation condition:** name the deterministic lineage/graph tool as a hard, owned dependency; if unavailable, do not compute graph reachability from raw exports — flag "Unable to determine" and escalate.
- Label any comparison made against a not-yet-approved candidate definition as such, and route through escalation rather than presenting it at full confidence.
- Bind all confidence language to the org's five-value taxonomy.
- Explicitly reconcile with Assurance Reviewer: state that Assurance Reviewer audits this agent's conclusions rather than performing an independent, potentially conflicting lineage-consistency analysis.
- Require every finding to cite the specific definition version/text and the specific code/logic excerpt compared, plus the stated semantic gap, for auditability.
- Add a minimum-hop-coverage rule for multi-hop lineage (require "Unable to determine" when intermediate stages are inaccessible) and an escalation trigger for suspected code/lineage-vs-runtime drift.

---

## 8. Data Quality Agent (`data-quality`)

**Layer:** Operational · **Verdict:** redesign

### Risks raised

- **Authority issue — "identify control owner" edges into human-only territory.** Even framed as propose-not-assign, nothing prevents a proposed owner name from being treated by a rushed reviewer as already-vetted fact.
- **Authority issue — "is the expectation approved" is an undocumented judgment call.** Determining whether a referenced business expectation is "actually approved" is left to agent judgment rather than a deterministic status-field check; no such field is defined anywhere.
- **Authority issue — undefined duplicate-vs-near-duplicate judgment.** The agent may "check for duplicates" but nothing says what happens when it judges something a near-duplicate rather than a true duplicate.
- **Evidence issue — the DQ-dimension taxonomy does not exist.** "A documented data-quality dimension taxonomy" is listed as an evidence requirement but is not an approved artefact anywhere in the repository; absent it, the agent will likely fall back to general industry knowledge (e.g., DAMA's six dimensions) presented as the firm's own framework.
- **Evidence issue — internal contradiction.** Mitigation requires the agent to "consume rather than re-derive Mapping & Lineage's evidence," yet `evidence_requirements` separately lists direct Schema/DDL access as a first-class input — those two statements conflict.
- **Overlap issue.** If the agent has independent schema/DDL access, it duplicates Mapping & Lineage's remit. If Definition & CDE surfaces multiple competing definitions, nothing stops this agent from silently choosing one to build a rule against — that is Definition & CDE's decision territory. Overlap with Exception & Root-Cause (using historical exception patterns to justify a threshold) is listed but never actually defined or bounded.
- **Hallucination / explainability risk.** Candidate SQL naming real-looking but unverified table/column identifiers when schema evidence is incomplete; "DRAFT, unexecuted" labelling does not stop a steward from copy-pasting a syntactically plausible but subtly wrong query; quality-dimension classification may silently pick one dimension when evidence plausibly supports more than one, with no requirement to surface the ambiguity.

### Required mitigations

- Remove or sharply narrow "identify control owner": restrict it to surfacing an owner field already present verbatim in upstream evidence, or returning an open question — never synthesising a plausible owner from role/domain inference.
- **Tool permission limit:** resolve the schema/DDL contradiction by routing physical-field grounding exclusively through Mapping & Lineage's output; if direct DDL read access is kept for SQL precision, scope it narrowly to the field(s) Mapping & Lineage already identified, with no independent schema exploration.
- **Escalation condition:** add explicit triggers for (a) the referenced business definition is not singular/unambiguous, (b) schema/DDL evidence does not match what Mapping & Lineage stated, (c) the control-inventory or schema source is unreachable (tool-unavailable case).
- Make "is the business expectation approved" a deterministic status-field check with a documented location — treat this as a blocking gap until that field exists.
- **Blocking prerequisite:** confirm the DQ-dimension taxonomy exists as an approved, versioned, internal artefact before building this agent; if it does not exist, add it to the backlog as a blocker rather than an assumed input.
- Require every table/column identifier in generated SQL to carry an explicit evidence citation back to Mapping & Lineage or schema/DDL evidence; absent one, output "insufficient schema evidence" instead of guessing.
- Require any reference to historical exception data to come from Exception & Root-Cause Agent's output only, never independently queried or clustered.

---

## 9. Exception & Root-Cause Agent (`exception-rootcause`)

**Layer:** Operational · **Verdict:** redesign (reconciled design: a thin, low-permission synthesis agent — neither the original standalone-agent design nor the Architect's "dissolve into an unnamed workflow" redesign was accepted as-is)

### Risks raised

- **Authority issue — accountability vacuum in the first redesign.** The Architect's redesign implicitly assigned hypothesis-drafting to the Stewardship Orchestrator via "workflow coordination," but the Orchestrator's own charter explicitly bars it from becoming "the primary expert" or dominating — drafting causal hypotheses from synthesized evidence is expert reasoning, not routing. No agent or role was named as the accountable author of the hypothesis text reaching the stewardship pack.
- **Authority issue — Assurance Reviewer scope blur.** Folding "evidence required to confirm root cause" into Assurance Reviewer's charter would turn a pure auditor into a co-generator of diagnostic content, undermining the independence that makes an audit role trustworthy.
- **Evidence issue — unverified determinism assumption.** The claim that exception clustering/correlation is "a deterministic query problem" is asserted, not evidenced — no source document specifies whether exception records are structured fields or free text. If free-text, "identify recurring characteristics" needs semantic clustering, and labelling that step "deterministic" would hide an inference step from the evidence-tagging discipline the whole system exists to enforce.
- **Evidence issue — misattributed citation.** The original justification's citation ("per HANDOFF.md's own framing, clusters quality failures") actually describes the Exception & Root-Cause Agent itself, not Data Quality Agent, undermining the claim that exception records are Data Quality's output.
- **Overlap issue.** "Identify common upstream dependencies" genuinely duplicates Mapping & Lineage's "dependency mapping." No production execution pipeline is named as the owner of actually running approved quality tests and persisting exception/control-failure records — the redesign implicitly assumes this exists.
- **Hallucination / explainability risk.** With no named identity authoring the synthesized hypothesis, Assurance Reviewer's challenge output has no clear author to attribute unsupported claims to. If the "deterministic" clustering step is actually a naive SQL group-by over semi-structured exception messages, patterns will be under-detected or mis-clustered without ever receiving INTERNAL/INFERENCE/OPEN-QUESTION tagging — a false sense of certainty.

### Required mitigations

- **Tool permission limit:** name a single, narrowly-scoped identity responsible for synthesizing already-assembled evidence (from the deterministic clustering step, Mapping & Lineage, Data Quality, Context Agent) into candidate hypothesis text with citations. It has read access **only** to the evidence packet assembled for it (by the Orchestrator or a direct evidence-bundle handoff) — no independent read access to raw exception logs, change logs, or lineage stores.
- **Blocking prerequisite:** before finalizing "deterministic" for the clustering step, confirm the actual schema of exception records (structured codes vs. free text) against real Data Quality Agent test output; if free-text, add an explicit, narrow AI-assisted clustering step and tag its outputs per the INTERNAL/INFERENCE distinction.
- Keep "identify evidence required to confirm/refute hypothesis H" with whichever role drafts H (forward-looking, generative); keep Assurance Reviewer strictly to "was H adequately supported when it reached the human" (backward-looking, audit) — do not merge these two functions.
- **Escalation condition:** no plausible correlated change event found within the lookback window → escalate as an unexplained recurring exception rather than guessing; a hypothesis implicates a production mapping/threshold/definition change → stop and escalate to Data Owner/Steward, never propose a fix; lineage evidence and quality-control history conflict for the same cluster → escalate to Assurance Reviewer/Data Steward for adjudication; an active, currently-unfolding incident → escalate immediately to Operations (this agent is diagnostic-support only, never incident response).
- Every hypothesis must cite the specific evidence item(s) backing it; a hypothesis lacking corroborating evidence must be labelled "Unsupported — requires further evidence," never presented as likely.
- Reconfirm that the Orchestrator's "route rather than dominate" rule is not violated by any implicit assignment of hypothesis synthesis to it.

---

## 10. Assurance Reviewer (`assurance-reviewer`)

**Layer:** Operational · **Verdict:** redesign

### Risks raised

- **Authority issue — "procedurally gate a case pack" is a real control action, underspecified.** This is a workflow-control action (blocking progress to the Data Steward), not a passive recommendation, yet nothing specifies whether it is implemented as a case-status write, who may override or acknowledge a gate, or how an override is logged.
- **Authority issue — unresolved evidence-request loop.** "May request additional evidence before a pack proceeds" does not name who it requests from, or what happens if the request is not fulfilled (no timeout/escalation path).
- **Authority issue — no defined handoff for contested findings.** Only "the Data Steward can adjudicate" is stated, with no mechanics for getting a contested finding in front of that steward promptly.
- **Evidence issue — no fallback for informal/incomplete upstream packs.** Every evidence requirement assumes structured, queryable producer-agent output packs and audit trails exist; no fallback is specified for the (likely common, early-stage) case where they are informal or incomplete.
- **Evidence issue — no "Unable to determine" status defined**, and no committed output schema (the repo already has a candidate CLAIM/STATUS/EVIDENCE/ASSUMPTIONS/RISK/ACTION-REQUIRED template that was never adopted or reconciled with).
- **Overlap issue.** The design addresses overlap with Risk Reviewer (design-time) and the Orchestrator (routing) but not the more direct overlap with each producer agent's own mandatory self-escalation logic — the contract should explicitly frame this agent as defense-in-depth over agents that already self-police, not duplicated responsibility.
- **Hallucination / explainability risk.** The reviewer inspects heterogeneous artefact types (natural language, SQL/code, lineage graphs, approval logs) with a single generalized judgment process; without artefact-specific deterministic tooling (a SQL diff/lint step, a lineage-graph query, an approval-log lookup) feeding it structured facts, its own conclusions are themselves LLM inferences needing the same evidence-citation discipline as any other agent. No stated review-coverage policy (100% vs. risk-based sampling) means the reliability guarantee the Data Steward can rely on is undefined.

### Required mitigations

- Specify the gating mechanism precisely: a named case-pack status field write (not a hard block), a named override role, and mandatory audit logging of every override.
- **Tool permission limit:** default to **static, read-only** inspection of pre-assembled evidence packs; require separate justification before granting any live-query or execute access to lineage graphs, catalogs, or SQL execution environments.
- **Escalation condition:** commit to a coverage policy — either 100% review of every material-conclusion pack before it reaches the Data Steward, or an explicitly human-approved, documented sampling/triage rule; do not leave this unresolved.
- Adopt (or explicitly extend) the CLAIM/STATUS/EVIDENCE/ASSUMPTIONS/RISK/ACTION-REQUIRED output schema, including an explicit "Unable to determine" status.
- State the build-sequencing dependency explicitly: this agent cannot be meaningfully evaluated until stub/mock output packs exist for the producer agents it reviews — build it only after at least one producer agent (Definition & CDE) has real evaluated output.
- Reframe the classification note to record this agent as one that **consumes deterministic policy/schema validators as required inputs**, so Claude Agent Builder does not implement boundary/approval checking as free-form LLM reasoning.

---

# System-Wide Risks

These risks recur across the pipeline as a whole and cannot be resolved inside any single agent's contract — they require pipeline-level or governance-level controls.

- **Self-review / conflict-of-interest pattern recurs structurally.** The Architect graded its own necessity; the original proposal to fold Eval Designer's test-authoring into Risk Reviewer would have let the same agent that finds a risk also decide what tests are "enough" to cover it. Every Factory-tier and Operational-tier boundary must be checked for whether the entity producing a conclusion is also the entity certifying it.
- **Prompt-injection-via-artefact ("hidden handoffs" of instructions).** Risk Reviewer, Assurance Reviewer, and Claude Agent Builder all consume content authored by another agent, a submitter, or a case (proposed contracts, evidence packs, case narratives). None of the original submissions explicitly instructed that this content is untrusted data to evaluate rather than instructions to follow. This must be a standing, pipeline-wide requirement.
- **Cumulative authority creep via unscoped tool permissions.** Permission/tool-scoping is the most concrete, recurring finding across multiple agents (Definition & CDE, Mapping & Lineage, Data Quality, Claude Agent Builder): none of the original submissions enumerated a Permitted Tools allow/deny list, and this environment's actual connected tool surface (e.g., the Qlik glossary MCP's create/update/delete/status-change tools sitting alongside the read tools these agents need) makes unscoped permissions a live risk, not a hypothetical one. Left unchecked across the pipeline, narrative-only "no write access" promises accumulate into a system where several agents are one wiring mistake away from write/delete authority nothing in their contract text intended.
- **Inconsistent confidence/status labelling.** Several agents, including the reviewers themselves (Risk Reviewer, Assurance Reviewer), were not originally required to label their own conclusions' certainty — inconsistent with the system's core non-goal of never hiding uncertainty or presenting inference as fact. A pipeline that is rigorous about producer-agent confidence but silent about reviewer-agent confidence has a blind spot at exactly the layer meant to catch blind spots.
- **Undocumented or unnamed human accountability roles.** An implicit "human governance owner" for Factory sign-off, an unbound "correct human owner" for the Orchestrator's approval gate, and unclear override authority for Assurance Reviewer's gating recur across the design. The system currently depends on named, accountable human roles that do not yet exist in any governing document — a single point of governance failure if left unresolved before build.
- **Case-state loss and evidence-preservation / data-handling risk.** Preserving evidence for traceability (a core design principle) means case logs and stewardship packs will necessarily carry copies of sensitive Investment Operations content (positions, valuations, mappings, quality findings). No reviewed contract specifies retention, access control, or redaction rules for that stored evidence — and the Orchestrator (where case state formally lives) is deferred, meaning this risk currently has no owner at all.
- **Sequencing/dependency risk.** Several agents assume prerequisite artefacts or precedent agents that do not yet exist: Data Quality's DQ-dimension taxonomy, Assurance Reviewer's need for real producer outputs, the Orchestrator's need for an approved routing table and schemas. Building out of dependency order risks hard-coding assumptions against a workflow that doesn't yet exist in documented form.
- **Duplicated-responsibility / divergent-answer risk at natural boundaries.** Context Agent vs. Definition & CDE on term meaning; Mapping & Lineage vs. Assurance Reviewer on lineage consistency; Data Quality vs. Exception & Root-Cause on exception-history evidence — each of these is currently resolved only by prose recommendation in the original submissions, not by binding Handoff Contracts. Left as prose, two agents can independently reach a Data Steward with contradictory conclusions about the same evidence, and nothing in the pipeline would surface the contradiction before a human sees it.
- **Hidden handoffs at the meta (Factory) layer.** Whether the Architect, Risk Reviewer, or Eval Designer may invoke each other or downstream agents directly — versus every handoff being Orchestrator- or human-mediated — is unresolved in every Factory-tier contract reviewed. An unnamed, implicit handoff at the design layer is as much a "hidden handoff" risk as one at the case-processing layer, and is currently undocumented in all four Factory agents.

---

# Open Questions for Human Steward

The following require explicit human-steward decisions before implementation proceeds. None of them can be resolved by an agent contract alone.

1. Should Risk & Governance Reviewer (Factory, build-time challenge of agent designs) and Assurance Reviewer (Operational, run-time challenge of case evidence) remain two separately-built agents indefinitely, or should the governance board require and document a rigorous cost/risk comparison against a single capability parameterised by evidence-access mode, before approving continued investment in two independently-built agents?
2. Who, by name or specific title, holds Factory-tier governance sign-off authority for approving an agent design after Architect and Risk Reviewer have completed their pass, and who holds override authority when a Risk Reviewer or Assurance Reviewer finding is contested by a project team?
3. What is the case-log and evidence-pack data-handling policy — what content may be persisted for traceability, who may read a given case's stored evidence, and what is the retention/redaction rule — given that preserving evidence per design principle 5 means Investment Operations content will be copied into these stores by default?
4. Should the eventual Orchestrator's case-state and routing function be built as a bespoke store, or should an existing enterprise case-management/ITSM platform (this environment has a connected ServiceNow MCP server) serve as the system of record, with the Orchestrator reduced to a thin deterministic integration/routing layer on top of it?
5. Does an approved, versioned Data-Quality-Dimension taxonomy already exist anywhere in the organisation's governance documentation, or does one need to be authored and formally approved as a new artefact before the Data Quality Agent can be built at all?
6. What is the actual structure of exception / control-failure records in the systems this will draw from — structured rule/field codes, or free-text descriptions? This determines whether the Exception & Root-Cause Agent's upstream clustering step can remain purely deterministic or needs its own narrow, explicitly-tagged AI-assisted clustering sub-step.
7. What coverage policy should Assurance Reviewer operate under in practice — unconditional 100% review of every material-conclusion pack before it reaches the Data Steward, or a documented, explicitly human-approved sampling/triage rule for high-volume periods — and who is authorised to approve any deviation from full coverage?
