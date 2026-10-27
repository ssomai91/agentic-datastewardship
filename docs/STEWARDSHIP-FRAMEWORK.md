# Stewardship Framework

**Status:** Draft, pending owner review. This document records how the accepted DMBOK2 alignment proposals (`GOVERNANCE-DECISIONS.md`, GD-06) are applied. The DMBOK2 is GENERAL INDUSTRY CONTEXT only; internal policy outranks it. Each section names the proposal it applies.

## 1. Steward title (P-01, option 3)

The project keeps the neutral title **Data Steward**. The DMBOK2 definition of stewardship and its focus areas are general industry context [DMBOK2-C03-14]. It says stewards may be differentiated by place or focus, and that steward-like functions go by other names such as custodian or trustee [DMBOK2-C03-20, DMBOK2-C03-15], so no single label is required. No steward type (business, enterprise or other) is adopted.

## 2. Governance owner and escalation (P-02, option 1)

One accountable owner is the approval and escalation endpoint, with a deputy. There is no layered escalation. The DMBOK2 says a governance team may be virtual, with specific accountabilities [DMBOK2-C03-04], and expects an executive sponsor [DMBOK2-C03-02]. This follows decision GD-01 in `GOVERNANCE-DECISIONS.md`.

| Role | Holder | Accountability |
|---|---|---|
| Project Owner (human governance owner) | _name to be added_ | Final approval of Factory outputs and of any agent design; adjudicates contested `cut` / `redesign` findings; logs every override. |
| Deputy | _name to be added_ | Acts for the Project Owner as escalation and approval endpoint when the owner is unavailable. |
| Data Steward | _name to be added_ | Reviews Factory and agent outputs for stewardship fit; recommends, does not approve. |
| Executive sponsor | _to be identified_ | Sponsors the capability and removes blockers; not a day-to-day approver. |

**Escalation path.** Agent, then Data Steward, then Project Owner (or deputy). A finding or question that the Data Steward cannot settle goes to the Project Owner, and the decision is recorded in `GOVERNANCE-DECISIONS.md`.

**Not adopted.** The optional title "Chief Data Steward" [DMBOK2-C03-21] is not used. This section is the short operating framework and accountabilities statement the DMBOK2 recommends [DMBOK2-C03-32].

## 3. Governance metrics (P-03, option 3)

**Deferred.** The success criteria in `HANDOFF.md` remain system-level criteria only. Programme-level stewardship metrics are deferred to the organisation's own governance metrics, and are revisited as the programme matures, since the DMBOK2 expects metrics to change with maturity [DMBOK2-C03-64]. See `docs/SUCCESS-MEASURES.md` for how the system-level criteria are measured.
