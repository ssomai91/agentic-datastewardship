# Assurance Reviewer contract: review stopping rule

**Fixed 2026-10-28, before the third Risk Reviewer pass.** Written down first so that "clean enough" is not judged after seeing the result.

## Why

Pass 1 found 18 issues. Pass 2 confirmed 15 resolved and found 8, five of them introduced by the revision. Pass 3 on the same pattern would find defects in the new checks, because a model reviewing a model always finds something. "Another clean pass" is not a reachable exit, so the exit is defined here.

## Decisions already made by the Project Owner (2026-10-28)

- **Scope: full v0 as drafted** (all eight build preconditions DC-1 to DC-8). Size is therefore not a reason to block.
- **Hold semantics: deferred.** Whether a hold is advisory or a hard gate stays open (`GOVERNANCE-DECISIONS.md`, GD-01, GD-07). The contract must not decide it.

## The rule

A Risk Reviewer finding on version 0.1.2 **blocks** the contract only if it is both:
1. **CONFIRMED**, and
2. a **drafting defect**: an internal contradiction, a missing or unsound mandatory template section, a mismatch with `schemas/`, `GOVERNANCE-DECISIONS.md` or the Phase 6 required mitigations in `docs/ARCHITECTURE-RISKS.md`, or a decision made that belongs to the owner.

Everything else does **not** block:
- PLAUSIBLE findings are copied into the contract's Known Risks (and Assumptions where an owner decision is involved).
- Findings about size, complexity or the build order of the preconditions are noted in Assumptions Pending Human Confirmation. The owner has decided scope.
- Findings that restate a limit the contract already states plainly are closed.

**Exit.** If no finding blocks, the contract is written out (Markdown first, then JSON, output schema and prompt) and goes to the Evaluation Designer. If any finding blocks, one more Architect revision is made for those findings only, then one more review. After that second round the remaining findings go to the Project Owner as open items. There is no third automatic round.

The contract stays `Draft`. Only the Project Owner approves it.