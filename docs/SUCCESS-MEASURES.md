# Success Measures

**Status:** Draft, pending owner review. Applies proposal P-14 (option C). The ten success criteria in `HANDOFF.md` stay as the **target state**. Each is rated against a stated baseline on a review schedule, without a formal maturity scale [DMBOK2-C15-14, DMBOK2-C15-23, DMBOK2-C15-16].

**Baseline date:** 2026-10-27. **Baseline ratings are Claude's proposal from repository evidence; the Project Owner confirms or changes them.**
**Review schedule:** quarterly (proposed; the owner sets and publishes the real schedule).
**Rating scale:** Not met / Partly met / Met.

| # | Success criterion (HANDOFF.md) | Baseline | Evidence for the baseline |
|---|---|---|---|
| 1 | Agents know their boundaries | Partly met | All five contracts have Not Responsible For and prohibited actions, enforced by `tests/test_contracts.py` and `tests/test_agent_consistency.py`. Boundary behaviour is tested by one harness (Definition & CDE) and three Factory runs only. |
| 2 | Humans know where accountability sits | Partly met | Roles and escalation are defined in `docs/STEWARDSHIP-FRAMEWORK.md` section 2, but the holders' names are blank. |
| 3 | Claims are traceable | Partly met | `schemas/material-claim.schema.json` and the handoff cross-reference check exist. Validated on synthetic and recorded outputs only. |
| 4 | Unsupported assumptions are visible | Partly met | Every output has an `assumptions` field, and contracts list assumptions pending confirmation. Nothing checks that assumptions are actually surfaced. |
| 5 | Quality controls can be linked back to definitions | Not met | No quality agent or approved rules exist; coverage is defined (`docs/DATA-QUALITY-FRAMEWORK.md` section 3) but empty. |
| 6 | Mappings can be linked back to meaning | Not met | The Mapping & Lineage Agent is not built. |
| 7 | Lineage can be linked to downstream impact | Not met | Not built. |
| 8 | Exceptions can be analysed as recurring patterns | Not met | Design only. The root-cause design passed on its second unaided run (`evals/factory-runs/RESULTS.md`); nothing is built. |
| 9 | Agents can be evaluated independently | Partly met | A ten-scenario harness exists for the Definition & CDE Agent and has been proven only against a rule-based agent, not the LLM agent. |
| 10 | Governance can be applied to the agents themselves | Partly met | The Factory (Architect, Risk Reviewer) has run on three scenarios and caught a real design defect. The named governance owner is not yet filled in. |

**How a review works.** At each review the Data Steward re-rates every row with the evidence for the new rating, and the change is recorded here with the date. A rating moves up only on evidence, never on intent.
