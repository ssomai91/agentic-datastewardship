# Phase 6: Assurance Reviewer build record

Recorded 2026-10-28. This is the first end-to-end use of the Factory (Architect, Risk Reviewer, Evaluation Designer, Builder) to build a new agent. **The contract is `Draft` (v0.1.5). The Project Owner has not approved it, and nothing here is approved.** All runs were fresh subagents following the agents' own prompts and contracts. Unlike the Phase 3 and Phase 5 runs these were guided builds, not unaided tests.

## What happened

| Stage | Output | Result |
|---|---|---|
| Architect, v0 | `p6-assurance-reviewer.architect.output.json` | Clean output, full 27-section draft contract (25k characters) |
| Risk Reviewer, pass 1 | `...review-v0.reviewer.output.json` | `redesign`, 18 findings (12 confirmed) |
| Architect, v1 | `...architect-v1.output.json` | Claimed all 18 resolved; contract grew to 42k characters |
| Risk Reviewer, pass 2 | `...review-v1.reviewer.output.json` | `redesign`: 15 of 18 confirmed resolved; 8 findings (5 introduced by the revision) |
| Architect, v2 | `...architect-v2.output.json` | Claimed all 8 resolved; size unchanged (41.5k) |
| Owner decision | `GOVERNANCE-DECISIONS.md` GD-07 | Full v0 scope; hold semantics deferred |
| Stopping rule | `...STOPPING-RULE.md` | Fixed before pass 3, after the advisor noted the loop was not converging |
| Risk Reviewer, pass 3 | `...review-v2.reviewer.output.json` | `redesign`: 2 blocking, 1 non-blocking |
| Architect, v3 (narrow) | `...architect-v3.output.json` | 37 of 455 lines changed; both blocking defects fixed |
| Risk Reviewer, pass 4 (final) | `...review-v3.reviewer.output.json` | **`keep`**: no blocking finding, 1 non-blocking (recorded in Known Risks) |
| Evaluation Designer | `evals/assurance-reviewer.eval.output.json`, `evals/assurance-reviewer.eval.md` | 66 cases, all ten categories, 20 open points |
| Builder (dry run) | `p6-assurance-reviewer.builder.output.json`, `prompts/assurance-reviewer.md` | 24 of 26 contract fields traced, 2 uncovered with reasons; escalated with notes |
| Coverage-trace validator | `tools/validate_coverage_trace.py` | **0 problems** on the real Builder output (first time on real output) |

## What this shows

- The Factory works as a loop: review caught real contradictions in every design round (a hold that was advisory yet had an override regime, an agent that could clear its own hold, decision rights that did not match GD-01).
- The Evaluation Designer and Builder each worked on real input for the first time, and each produced schema-valid output.
- The deterministic validator accepted the Builder's trace, so a field could not be silently dropped.

## What it does not show

- **"Keep" is not approval, and it is not proof of correctness.** It means no CONFIRMED drafting defect was found by a model reviewer applying a rule fixed in advance. Four review passes found something each time until the rule narrowed what counts as blocking.
- **The contract is large** (about 46k characters against 19k for the Definition & CDE contract) and **cannot run**: it depends on eight components (DC-1 to DC-8) that do not exist. The owner chose this scope (GD-07); the Risk Reviewer noted the agent is not deployable until they exist.
- **No test case has been run.** The 66 cases are a specification. Real evaluated Definition & CDE output does not yet exist in the form the agent would review.
- **The prompt is an unrun draft.** It has not been exercised against any case.
- The Builder's coverage trace is checked for completeness and verbatim passages, not for whether the prompt *behaves* as the contract says.

## Open items for the Project Owner

1. The 20 points the Evaluation Designer found ambiguous or unthresholded (`evals/assurance-reviewer.eval.md`, *Open points*).
2. Hold semantics (advisory or hard gate): deferred (GD-01, GD-07).
3. Names for the human roles, the case store, the sampling rule, the evidence-request timeout (all marked as assumptions in the contract).
4. Whether to approve the contract at all, and in what order to build DC-1 to DC-8.
5. The Builder's own notes: the contract is silent on the form of a refusal, on schema-required agent-set strings, and on the rank 1 stop record.