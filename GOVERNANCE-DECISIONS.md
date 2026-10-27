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

**Current state (2026-10-27).**
- `docs/DMBOK-ALIGNMENT.md` has not been generated. The pipeline in `.dmbok-work/` stopped before the merge step (`merged.json` does not exist).
- `docs/dmbok2-citations.json` is empty, so the citation tests verify nothing.
- Four related tests are skipped, with the reason shown in the test output.

**Done when.** The pipeline has been run to completion, `docs/DMBOK-ALIGNMENT.md` exists as a draft pending owner review, the citation index is populated and verified against `DAMA-DMBOK-Summary.md`, and the four skipped tests run and pass.

**Note.** The book text is a full copy of copyrighted material, kept in this private repository at the owner's request. Do not make the repository public or share it without removing it first.

## GD-04 Data-quality taxonomy (P1-05)

**Question.** Which data-quality taxonomy do the Definition & CDE agent and any later quality agents use?

**Decision.** Use the **six core dimensions published by DAMA UK (2013)**, as described in DMBOK2 Chapter 13: completeness, uniqueness, timeliness, validity, accuracy, consistency.

**Status.** `Proposed` taxonomy, accepted by the project owner as the working default. It is a general industry reference, not an organisation-approved standard. If the organisation has its own taxonomy, that one replaces this and this entry is marked `Superseded`.

**Source.** DMBOK2 Chapter 13, section 1.3.3, in `DAMA-DMBOK-Summary.md` (search "six core dimensions").
