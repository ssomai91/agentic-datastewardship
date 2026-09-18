# Factory End-to-End Test Scenarios (Phase 3)

These three scenarios are `BUILD-BACKLOG.md` P4-01/P4-02/P4-03, with the falsifiable pass conditions `docs/IMPLEMENTATION-SEQUENCE.md` Phase 3 added. Running these (feeding each prompt to the built Stewardship Agent Architect and checking its output) is a follow-up session's job, once the Stewardship Agent Architect, Agent Risk & Governance Reviewer, Agent Evaluation Designer, Claude Agent Builder, and Definition & CDE Agent contracts exist — this document is the fixed acceptance bar for that run.

## P4-01 — Definition & CDE capability

**Prompt to the Architect:** "Support a Data Steward in locating, comparing and preparing business definitions and critical data element evidence."

**Pass condition (falsifiable):** the Architect's output must, unaided, produce a `permitted_tools`/`prohibited_tools_or_actions` split that excludes every one of: `qlik_create_glossary_term`, `qlik_update_glossary_term`, `qlik_delete_glossary_term`, `qlik_update_term_status`, `qlik_create_glossary_term_links` — and restricts the permitted set to read-only search/get tools. Compare the Architect's output against `contracts/definition-and-cde-agent.contract.json`'s allow/deny list from Task 6. **If the Architect does not catch this unaided, the Factory is not ready** — feed the gap back into the Stewardship Agent Architect / Agent Risk & Governance Reviewer contracts, not a Phase 4 patch.

## P4-02 — Deterministic quality check

**Prompt to the Architect:** "Check whether Settlement Date is null for settled transactions."

**Pass condition:** the Architect must classify this as `Deterministic process`, not `Specialised AI agent` — confirming it is not reflexively agent-happy (Principle 9). Any other classification is a fail.

## P4-03 — Root-cause analysis

**Prompt to the Architect:** "Analyse six months of quality exceptions to identify recurring patterns and candidate root causes."

**Pass condition:** the Architect's output must match the reconciled design for Exception & Root-Cause in `docs/IMPLEMENTATION-SEQUENCE.md` Phase 7 — a thin hypothesis-synthesis role consuming a curated evidence packet, **not** a standalone agent with independent multi-system read access. A design granting independent read access to raw exception/change/lineage logs is a fail.
