# tools/assurance: deterministic components for the Assurance Reviewer

Stand-ins for the build preconditions in `agents/operational/assurance-reviewer.md` (Build Preconditions). The Markdown contract is the source of truth; **nothing here is approved and none of it is connected to a real system or real data.**

| ID | Module | State |
|---|---|---|
| DC-1 packet assembly | `assemble.py`, `store.py` | Stand-in. The case store is built from the synthetic glossary fixture. Cited records, uncited records by mechanical key match, store query and run id are written to the manifest. It does not judge contradiction. |
| DC-2 packet-scoped read | `packet_read.py` | **Not built in the sense the contract means.** A Python path guard only. It does not bind a Claude subagent's Read tool, so a model run is scoped to the packet by instruction only. Binding it needs a permission rule or hook, which is a settings change for the owner to approve. |
| DC-3 validator and boundary checker | `validator.py` | Stand-in. Schema, id checks, tool-permission check. With no tool-call log the boundary result is `absent`, which is never read as pass. |
| DC-4 approval-log lookup | `approval_log.py` | Stand-in over a synthetic fixture. Explicit empty result; `reviewed` is not `approved`. |
| DC-5 evidence-request tracker | none | Deferred (the contract allows it for a first v0). |
| DC-6 provenance flag | `assemble.py` | Set by assembly from the store's own declaration; the pack cannot declare it. |
| DC-7 coverage register | none | Deferred; manifest carries `coverage: full` and any `sampling_rule_ref` is rank 3. |
| DC-8 status recorder and output checker | `gate.py`, `recorder.py` | Stand-in. Checks (a) to (g); append-only; no approve, clear, update or delete. Human resolution requires the Project Owner role **as supplied by the caller: nothing authenticates it.** |

## Rules this code follows

- **Literal reading.** Where the contract states a rule, it is implemented as stated. `gate.py` is checked against 32 cases of the evaluation spec (expected values read from the spec, not typed).
- **Report, do not decide.** Where the contract is silent or ambiguous the checker warns instead of rejecting, and `gate.RESOLUTIONS` names each assumption with the open point it comes from. Defaults that were chosen to keep the function total: an absent `coverage` field is rank 3 (the Coverage row's literal text); every `Unable to determine` counts as a gap.
- **Not enforced, because the contract does not specify it:** the summary template, the form of schema-required free strings, the form of the rank 1 stop record, how `approval_check` maps to an approval-log entry.

## What is not implemented

Authentication of the human channel, DC-5, DC-7, a real case store, a real approval log, binding the agent's Read tool to the packet, and any live connection to anything.