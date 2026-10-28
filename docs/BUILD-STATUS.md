# Build Status

**As of 2026-10-28.** What has been built, what has been tested, what is open, and what comes next. Every agent contract is `Draft`; **nothing is approved** (approval is the Project Owner's, `GOVERNANCE-DECISIONS.md` GD-01). The test suite passes locally at the time of writing (run `python -m pytest -q`).

## Phases (`docs/IMPLEMENTATION-SEQUENCE.md`)

| Phase | What | State |
|---|---|---|
| 0 Scaffolding and schemas | Repository structure; contract, handoff, evidence, material-claim and quality-issue schemas; one output schema per agent | Done |
| 0b Governance prerequisites | Accountable roles; data-quality taxonomy | Roles defined by title, names blank (GD-01). Taxonomy proposed (GD-04), awaiting confirmation |
| 1 Architect and Risk Reviewer | Contracts, JSON, prompts (v0.1.3) | Done, Draft |
| 2 Evaluation Designer and Builder | Contracts, JSON, prompts (v0.1.2) | Done, Draft. First real runs happened in Phase 6 |
| 3 Factory end to end | Three scenarios through the Architect | Two passed first time. Root-cause failed, was fixed in the contracts and passed on re-run (`evals/factory-runs/RESULTS.md`) |
| 4 Definition & CDE Agent | Contract, JSON, prompt (v0.1.3), mock glossary, 10-scenario harness | Done, Draft. **Not connected to any real glossary** (GD-05 open) |
| 5 Controlled evaluation | Real agent through the 10 scenarios, three passes | 8/10, 10/10, then 10/10 with frozen assertions. Synthetic data only; tool-call assertions skipped; human usefulness not assessed (`evals/definition-and-cde-runs/RESULTS.md`) |
| 6 Assurance Reviewer | Contract v0.1.5, JSON, output schema, 66-case test spec, draft prompt | Done as Draft. **Cannot run:** eight build preconditions do not exist; no case has been run (`evals/factory-runs/p6-assurance-reviewer.RESULTS.md`) |
| 7 Remaining producers | Context, Mapping & Lineage, Data Quality, Exception & Root-Cause | Not started |
| 8 Orchestration | Routing and case state | Not started; depends on the case-store decision |

## Governance decisions (`GOVERNANCE-DECISIONS.md`)

GD-01 approval and override roles (decided; names pending) · GD-02 evidence retention (synthetic only) · GD-03 DMBOK alignment in scope (done) · GD-04 data-quality taxonomy (proposed default) · GD-05 glossary system (**open**) · GD-06 14 DMBOK proposals (accepted, applied as drafts) · GD-07 Assurance Reviewer scope (full v0; hold semantics deferred).

## Documents added during the build

| Document | Purpose | Status |
|---|---|---|
| `docs/AUTHORITY-CHAIN.md` | Markdown contract, then JSON, then prompt; what the tests enforce | Current |
| `docs/DMBOK-ALIGNMENT.md` | 32-concept conformance matrix, 5 deviations, 14 proposals (all accepted) | Draft |
| `docs/STEWARDSHIP-FRAMEWORK.md` | Roles, escalation, metrics deferral, metadata model, operating model | Draft, names blank |
| `docs/CDE-CRITERIA-POLICY.md` | Criticality drivers checklist | Draft |
| `docs/DATA-QUALITY-FRAMEWORK.md` | Taxonomy, rule checklist, coverage, issue record | Draft |
| `docs/DATA-CLASSIFICATION.md` | Provisional confidentiality labels | Draft |
| `docs/SUCCESS-MEASURES.md` | Success criteria as rated measures with a baseline | Draft, baseline is a proposal |
| `docs/GLOSSARY-TOOL-MAPPING.md` | Capability map, real tool column empty | Draft, waits on GD-05 |

## Code and tooling (`tools/`, `tests/`)

Schema registry and cross-reference checks; the Definition & CDE harness, mock read-only glossary and a rule-based reference agent (a positive control, not the real agent); the Builder coverage-trace validator (first run on real output in Phase 6: 0 problems); guard tests for contracts, prompts, outputs, recorded runs and applied proposals. GitHub Actions runs the suite (`.github/workflows/tests.yml`).

## What is not true yet

- No agent is approved, and none runs against real data or a real system.
- The Assurance Reviewer has never run. The Definition & CDE Agent has run only against a synthetic glossary file, read as a file.
- The harness assertions were adjusted three times after seeing Phase 5 results (disclosed there); only the third pass is a clean measurement.

## Open items for the Project Owner

1. Approve `docs/IMPLEMENTATION-SEQUENCE.md` or record an exception: it is still `DRAFT`, and the build went past that gate.
2. Name the Project Owner, deputy, Data Steward and executive sponsor; name the collaboration forum.
3. Choose the glossary system (GD-05) and the case store; set the sampling rule and evidence-request timeout.
4. Decide hold semantics (advisory or hard gate) and the 20 open points in `evals/assurance-reviewer.eval.md`.
5. Review and approve, amend or reject each Draft contract and document.
6. Decide the data-quality taxonomy and the Reviewer's evidence-authority value (`evals/factory-runs/RESULTS.md`, finding 5).

## Next

Build the minimal deterministic components the Assurance Reviewer needs (packet assembly, packet-scoped read, a contract validator, the status recorder) so it can run for the first time on the recorded Definition & CDE outputs. Further producer agents and orchestration wait on that result and on the owner decisions above.