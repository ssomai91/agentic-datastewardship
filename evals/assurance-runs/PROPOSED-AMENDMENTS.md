# Proposed contract amendments (for the Project Owner; NOT applied)

From the first Assurance Reviewer run (`RESULTS.md`) and the Evaluation Designer's open points (`evals/assurance-reviewer.eval.md`). The contract is `agents/operational/assurance-reviewer.md` (v0.1.5, Draft). Each proposal is written Markdown-first so it can be adopted, changed or rejected. **Nothing here is applied, and none is decided.** Under `docs/AUTHORITY-CHAIN.md` an adopted change goes into the Markdown contract first, then the JSON, then the prompt, with a version bump.

## A. Deterministic results are authoritative inputs (finding 1)

**Evidence.** All six agents set `boundary_check` to `unable_to_determine` while the validator report said `pass`, after reading a stand-in caveat inside the report. Process step 1 already says the agent "does not recompute" deterministic results, but does not say what happens when a result carries a caveat.

**Proposal.** Add to Process step 1: *The agent copies the result of each deterministic check into the matching output field (`boundary_check`, `approval_check`, `deterministic_checks_consumed`) exactly as supplied. If it doubts a result's provenance it records an `evidence_gap` finding that names the result; it never changes the field.* Rationale: a reviewer that overrides the deterministic layer makes the layer pointless and makes the output unreproducible.

**Alternative.** Let the agent downgrade to `unable_to_determine` when a result carries a caveat, and say so in a closed form. This is more cautious and less checkable.

## B. The form of the gate claim (finding 2)

**Evidence.** One agent's `AR-C-GATE` statement did not state the gate value.

**Proposal.** In Output Schema, Mapping to the handoff, state the form: *the statement of `AR-C-GATE` is exactly `<gate value> | recommendation, not a clearance`.* Then DC-8 can check equality instead of containment.

## C. Producer open-question claims and rank 3 (found while freezing the second pass)

**Evidence.** Step 9 rank 3 counts "any claim `Unable to determine` because of a gap". A producer's own claims of type `open_question` or `human_decision_required` are `Unable to determine` by design, not because evidence is missing (eval open point AR-T32, UNRESOLVED). In pass 1, A2 reached `INCOMPLETE` partly for this reason, and a real pack with such claims may never reach `NO_BLOCKING_FINDINGS_IDENTIFIED`.

**Proposal.** Reword rank 3: *... or any producer claim that is `Unable to determine` because required evidence is missing. A producer claim of type `open_question` or `human_decision_required` is not a gap.* The Confidence Rules already say such claims are not assertions about the evidence.

**Alternative.** Keep the text. Then `NO_BLOCKING_FINDINGS_IDENTIFIED` is reachable only for packs with no such claims, which excludes most real Definition & CDE output.

## Not proposed here

Hold semantics (advisory or hard gate), the case store, the sampling rule, the timeout and role names are decisions for you, not drafting changes (GD-01, GD-07).