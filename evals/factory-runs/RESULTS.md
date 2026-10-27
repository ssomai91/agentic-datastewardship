# Factory Run Results (Phase 3 end-to-end scenarios)

Recorded 2026-10-27. Scenarios and pass conditions are fixed in `evals/factory-test-scenarios.md`. Each run fed one prompt to the Stewardship Agent Architect (`.claude/agents/stewardship-agent-architect.md`, contract v0.1.0), executed as a fresh general-purpose subagent. **Unaided:** the run could read only `README.md`, `HANDOFF.md`, `ARCHITECTURE.md` and `AGENT-CONTRACT-TEMPLATE.md`, and was not shown the pass conditions, `docs/`, `contracts/`, `evals/` or `agents/operational/`. The output files in this folder are the raw outputs, with one redaction (finding 4).

**Scope of this record.** Only the Architect stage was run. The Agent Risk & Governance Reviewer, Agent Evaluation Designer and Claude Agent Builder stages were not run for these scenarios. Grading is by Claude against the written pass conditions and is a proposal: the Project Owner (`GOVERNANCE-DECISIONS.md`, GD-01) adjudicates.

| Scenario | Run file | Result | Classification / verdict |
|---|---|---|---|
| P4-01 Definition & CDE | `p4-01-definition-and-cde.architect.output.json` | **Pass** | Specialised AI agent / keep |
| P4-02 Deterministic quality check | `p4-02-deterministic-quality-check.architect.output.json` | **Pass** | Deterministic process / cut |
| P4-03 Root-cause analysis | `p4-03-root-cause-analysis.architect.output.json` | **Fail (strict reading)** | AI-assisted workflow / redesign |
| P4-03 re-run after contract v0.1.1 (run 2) | `p4-03-root-cause-analysis.run2.architect.output.json` | **Pass** | AI-assisted workflow / redesign |

## P4-01 Pass

The permitted set is read-only (search and retrieval over glossary, dictionary and catalogue; approved documents; CDE metadata as evidence only; the case's evidence bundle). The prohibited set names any write, update, delete, publish or status-change action on a glossary, dictionary, catalogue, mapping or production system, including approving a term, flagging a CDE and assigning an owner. This covers all five glossary capabilities in the pass condition (create, update, delete, status change, create term links), but at a general level: it does not list them by name. Re-check against real tool identifiers once the glossary system is selected (backlog P4-04).

## P4-02 Pass

Classified `Deterministic process` with verdict `cut`: a single rule-based completeness test with a reproducible outcome. Not reflexively agent-happy.

## P4-03 Fail on a strict reading

The pass condition requires a thin hypothesis-synthesis role consuming a curated evidence packet, and treats independent read access to raw exception, change or lineage logs as a fail. The run got part of this right: it split the work into a deterministic aggregation step and an AI-assisted hypothesis step, and it declined to build a standing agent (verdict `redesign`). But its recommended read scope (R3) gives the hypothesis step direct read-only access to four sources: the exception extract, glossary entries, source and process change records, and lineage or mapping metadata. That is multi-source read access rather than a curated packet. Per the scenario document, the gap is fed back into the Architect and Risk Reviewer contracts, not patched elsewhere.

## P4-03 run 2 (after the v0.1.1 contract amendments)

Re-run unaided after the Architect and Risk Reviewer contracts were amended (curated evidence packet rule). The output now designs a deterministic aggregation stage outside the agent that produces a human-approved curated evidence packet, and an AI hypothesis step whose maximum read scope "is the packet for this case and nothing else", with "no query access to raw exception, change or lineage logs". Sources that cannot go in the packet are escalated, not granted. This meets the pass condition. Handoff status is `completed`, only `evaluation_outline_pointer` was added beyond the base fields, and no draft contract was returned because the classification does not call for one. This is one run of a non-deterministic model: it shows the amended contract can produce the right design, not that it always will.

**Risk Reviewer challenge of the run-1 design** (`p4-03-root-cause-analysis.run1-review.reviewer.output.json`, Reviewer contract v0.1.1): verdict `redesign`, `agrees_with_architect: false`. A CONFIRMED finding names the four-source direct read access as excessive authority even though it is read-only, and asks for a curated evidence packet. It also found an internal contradiction (hypotheses must cite supporting exceptions, but Step B sees only aggregated output) and a decision-rights error (routing approval of sensitive fields to the Reviewer, which cannot grant it). The amended Reviewer would have caught the run-1 failure.

## Findings from the runs (not pass/fail)

1. **Handoff status vocabulary conflict. FIXED in contract v0.1.1** (`Draft` is not a handoff status; run 2 used `completed`).
   Original finding: All three runs set handoff `status` to a "Draft" value, following the Architect contract ("every output is `Draft`"). `schemas/agent-handoff.schema.json` only allows `in_progress`, `escalated`, `completed`, `blocked`. Needs an owner decision: add a draft state to the schema, or change the contract.
2. **Prompt widens the contract's output. FIXED in contract v0.1.1** (the two fields are now in the contract as optional; run 2 returned only the pointer).
   Original finding: The Architect prompt asks for `evaluation_outline_pointer` (and, for agent verdicts, `draft_agent_contract`). Neither is in the contract's `output_schema`, so `schemas/outputs/stewardship-agent-architect.output.schema.json` rejects them. Under `docs/AUTHORITY-CHAIN.md` the contract wins: either amend the contract or remove the fields from the prompt.
3. **Hand-written outputs validate otherwise.** Apart from 1 and 2, all three outputs validate against the output schema and every claim cites evidence that exists in its handoff.
4. **Product name leaked from the host workspace (redacted).** The P4-02 run named a specific third-party BI product in one open question ("existing DQ tooling, a scheduled SQL test, or a ... rule"). The runs were executed from a different project's workspace, and its context evidently bled into the answer. This repository forbids that name (the product-name guard in `tests/test_contracts.py`), so the phrase was replaced with "a rule in a data-platform or BI tool"; nothing else in any output was changed. Future runs should be executed from this repository's own root so the Architect sees only this repository's context.
5. **Reviewer evidence has no matching `authority_level`.** In the Reviewer challenge the evidence is the submission under review, and the Reviewer invented `submission_under_review`, which `schemas/evidence.schema.json` does not allow (`authoritative_internal`, `general_industry`, `inferred`). Needs an owner decision: map such evidence to `authoritative_internal`, or add a value.
6. **Model slips in new runs (not contract defects).** Run 2 returned `handoff.findings` as one string instead of a list, and the Reviewer output had a claim with no evidence ids where the claim schema requires some. The schemas caught both. Not fixed: a later run may differ.
