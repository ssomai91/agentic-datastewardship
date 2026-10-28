# Governance Decisions

Register of project-level decisions that the Agent Contracts and Factory agents depend on. Each decision names who owns it, what was decided, and what it changes.

**Status values:** `Decided` (recorded by the project owner), `Open` (not yet decided), `Superseded`.
**Rule:** A decision is only `Decided` when the project owner has said so. Claude proposals stay `Proposed` until then.
**Recorded:** 2026-10-27 from the project owner's answers in chat.

| ID | Decision | Status | Decided |
|---|---|---|---|
| GD-01 | Factory approval and override roles | Decided (names pending) | 2026-10-27 |
| GD-02 | Evidence retention and redaction | Decided | 2026-10-27 |
| GD-03 | DMBOK alignment scope | Decided | 2026-10-27 |
| GD-04 | Data-quality taxonomy | Decided (proposal; owner to confirm in org policy) | 2026-10-27 |
| GD-05 | Glossary / catalogue system for the Definition & CDE Agent | **Open** | - |
| GD-06 | DMBOK alignment proposals P-01 to P-14 | Decided and applied as drafts | 2026-10-27 |
| GD-07 | Assurance Reviewer v0 scope and hold semantics | Decided (scope); hold semantics deferred | 2026-10-28 |

---

## GD-01 Factory approval and override roles (P1-02)

**Question.** Who is the named human governance owner for Factory sign-off, and who may override a Risk Reviewer `cut` / `redesign` finding?

**Surfaced in.** `docs/ARCHITECTURE-RISKS.md` (unnamed accountable role); *Assumptions Pending Human Confirmation* in the Architect, Risk Reviewer and Builder contracts.

**Decision.** Two roles are defined by title. People's names are left blank for the project owner to fill in.

| Role | Holder | Authority |
|---|---|---|
| Project Owner (Factory governance owner) | _name to be added_ | Final sign-off on every Factory-tier output (design, review, evaluation, build). Adjudicates contested `cut` / `redesign` findings. |
| Data Steward | _name to be added_ | Reviews Factory outputs for stewardship fit; recommends but does not approve. |

**Override rule.** A `cut` / `redesign` finding may be overridden only by the Project Owner, and the override must be logged with: finding ID, reason, date, and the owner's name. A Factory agent never overrides its own or another agent's finding.

**Still open.** Holders' names. Whether an unresolved `cut` / `redesign` is a hard gate or advisory (see the Risk Reviewer contract's assumptions).

## GD-02 Evidence retention and redaction (P1-03)

**Question.** How long are agent evidence and outputs kept, and what is redacted?

**Decision.** This repository holds **synthetic data only** (`docs/REPO-CONVENTIONS.md`, *No production connectivity*). Evidence and outputs here are kept in git as part of the project record. No real client, position or personal data is stored in this repository.

**Consequence.** Retention and redaction rules for real data are **not** set here. They must be decided, by the Project Owner with the relevant Data Owner, before any operational agent is connected to real data. Until then, a real-data request is an escalation, not a default.

## GD-03 DMBOK alignment scope (P1-04)

**Question.** Does aligning the project to DAMA-DMBOK 2nd edition remain in scope?

**Decision.** **In scope: finish it.** The DMBOK is an industry reference only; the project is aligned to it, not the reverse (`docs/superpowers/specs/2026-10-01-dmbok-alignment-design.md`).

**Current state (2026-10-27).** Pipeline complete. `docs/DMBOK-ALIGNMENT.md` exists as a **draft pending owner review** (32 concepts, 5 deviations, 14 proposals all Pending). `docs/dmbok2-citations.json` holds 374 citations, each checked against its PDF page marker. All concepts were graded by a reader and checked by an independent verifier. The previously skipped tests now run.

**Next.** The owner reviews the proposals in section 4 of the alignment doc and records a decision on each. Nothing in the doc is applied until then.

**Note.** The book text is a full copy of copyrighted material, kept in this private repository at the owner's request. Do not make the repository public or share it without removing it first.

## GD-04 Data-quality taxonomy (P1-05)

**Question.** Which data-quality taxonomy do the Definition & CDE agent and any later quality agents use?

**Decision.** Use the **six core dimensions published by DAMA UK (2013)**, as described in DMBOK2 Chapter 13: completeness, uniqueness, timeliness, validity, accuracy, consistency.

**Status.** `Proposed` taxonomy, accepted by the project owner as the working default. It is a general industry reference, not an organisation-approved standard. If the organisation has its own taxonomy, that one replaces this and this entry is marked `Superseded`.

**Source.** DMBOK2 Chapter 13, section 1.3.3, in `DAMA-DMBOK-Summary.md` (search "six core dimensions").

## GD-05 Glossary / catalogue system (P4-04)

**Question.** Which glossary or catalogue system will the Definition & CDE Agent read from?

**Status.** **Open.** Not decided, and not Claude's to decide.

**What exists meanwhile.** A mocked read-only glossary over synthetic data (`tools/mock_glossary.py`) and the capability-level mapping in `docs/GLOSSARY-TOOL-MAPPING.md`, with the real-tool column empty. Until this is decided the agent can reason only over glossary content given to it, and must answer `Unable to determine` otherwise.

**Needed from the owner.** The system, a read-only access route, and who may approve connecting it. See `docs/GLOSSARY-TOOL-MAPPING.md` section 4 for the steps that follow.

## GD-06 DMBOK alignment proposals (P-01 to P-14)

**Question.** Which option does the project adopt for each of the 14 proposals in section 4 of `docs/DMBOK-ALIGNMENT.md`?

**Decision.** The project owner accepted **all 14 recommendations as written** on 2026-10-27. Each proposal's Decision column in the alignment doc now records the accepted option.

**Where this connects to earlier decisions.** P-02 (single accountable owner) matches GD-01, P-07 (DAMA UK six dimensions) matches GD-04, and P-04 (keep the single draft gate until a glossary system is chosen) waits on GD-05.

**Applied (2026-10-27).** All 14 are applied as drafts, one commit each, with a guard test (`tests/test_applied_proposals.py`) checking each is present and cites real DMBOK2 ids. Where each landed is shown in the Decision column of `docs/DMBOK-ALIGNMENT.md` section 4. The new documents are `docs/STEWARDSHIP-FRAMEWORK.md`, `docs/CDE-CRITERIA-POLICY.md`, `docs/DATA-QUALITY-FRAMEWORK.md`, `docs/DATA-CLASSIFICATION.md` and `docs/SUCCESS-MEASURES.md`, plus `schemas/quality-issue.schema.json` and an optional `confidentiality_label` on `schemas/evidence.schema.json`. Edits to the owner's original files are pointer notes only (a README note, and two bullets in `ARCHITECTURE.md`).

**Still for the owner.** The names of the Project Owner, deputy and Data Steward; the executive sponsor; the collaboration forum; the real review schedule and baseline confirmation; tailoring the CDE criteria; and whether to approve each new document. P-04's later lifecycle states wait on GD-05.

## GD-07 Assurance Reviewer v0 scope and hold semantics (Phase 6)

**Question.** How much does the first version of the Assurance Reviewer cover, and is a hold advisory or a hard gate?

**Decision (project owner, 2026-10-28).**
- **Scope: the full v0 as drafted.** All eight build preconditions (packet assembly, packet-scoped read, validator and boundary checker, approval-log lookup, evidence-request tracker, provenance flag, coverage register, status recorder) are specified now. The Risk Reviewer noted that none of them exists yet and that the agent is not deployable until they do; that stays true.
- **Hold semantics: deferred.** Whether a hold blocks progress remains open under GD-01. The contract recommends a gate value and does not decide whether it blocks.

**Review stopping rule.** Fixed before the third review pass in `evals/factory-runs/p6-assurance-reviewer.STOPPING-RULE.md`.

**Status of the contract.** `Draft`. Approval by the Project Owner is not given.
