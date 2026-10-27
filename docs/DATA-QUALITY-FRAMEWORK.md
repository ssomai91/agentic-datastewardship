# Data Quality Framework

**Status:** Draft, pending owner review. Applies proposals P-07 to P-10. The DMBOK2 is GENERAL INDUSTRY CONTEXT; the organisation's own policy outranks it.

## 1. Taxonomy (P-07, option 1)

**Taxonomy version 0.1 (proposed).** The six core dimensions published by DAMA UK in 2013 are the starting set for the organisation's own versioned taxonomy [DMBOK2-C13-12]. This matches decision GD-04 in `GOVERNANCE-DECISIONS.md`. If the organisation has its own taxonomy, that replaces this one.

| Dimension | Working meaning |
|---|---|
| Completeness | How much of the data that should be present is present. |
| Uniqueness | Whether each thing is recorded only once. |
| Timeliness | Whether the data reflects reality at the time it is needed. |
| Validity | Whether values conform to the syntax of their definition (format, type, range). |
| Accuracy | Whether the data correctly describes the real-world thing or event. |
| Consistency | Whether representations of the same thing agree. |

**Characteristics outside the six.** DAMA UK also describes characteristics that affect quality but are not among the six [DMBOK2-C13-13]: usability, timing issues beyond timeliness, and flexibility. They are not dimensions in this taxonomy. A rule may carry them as a note, and they cannot be the only dimension a rule is expressed in.

## 2. Candidate rule pre-approval checklist (P-08, option 2)

Before a candidate quality rule reaches the Data Steward it must carry all four attributes below [DMBOK2-C13-30, DMBOK2-C13-31, DMBOK2-C13-32, DMBOK2-C13-49]. A rule missing any attribute is returned to its author, not reviewed.

| # | Attribute | Evidence required |
|---|---|---|
| 1 | Documented consistently from the rule template | The completed template: rule text, data element, dimension, threshold or `UNRESOLVED - pending human definition`. |
| 2 | Expressed through one approved dimension | The dimension, from the taxonomy in section 1. |
| 3 | Tested against actual data | A test result on an approved extract, or on synthetic data while no real data is connected, stated as such. |
| 4 | Confirmed by a subject-matter expert | The SME's name and the date, recorded by a human. An agent never records this itself. |

An agent may prepare a candidate rule and attach attributes 1 to 3. Attribute 4 is human only. A threshold with no approved source stays `UNRESOLVED - pending human definition`; it is never invented.

## 3. Quality coverage (P-09, option 1)

**Coverage is defined as a matrix.** For each Critical Data Element, which dimensions have an approved rule and threshold, in which systems of the data value chain. This mirrors the DMBOK2 service-level scoping list of covered elements with per-element, per-dimension, per-system expectations [DMBOK2-C13-46, DMBOK2-C13-33].

| CDE | System in the data value chain | Dimension | Approved rule | Approved threshold | Status |
|---|---|---|---|---|---|
| _one row per CDE, system and dimension_ | | | rule id or none | value, or `UNRESOLVED - pending human definition` | covered / gap / not applicable |

A cell is **covered** only when both a rule and a threshold have human approval. **Coverage** for a CDE is the share of its (system, dimension) cells that are covered; a cell marked gap is reported, never filled by inference. No coverage figure exists yet: there are no approved rules or thresholds in this repository.

## 4. Minimum quality issue record (P-10, option 1)

An issue routed to a human carries at least the fields the DMBOK2 lists for tracked issues: a description of the issue, its root causes, options for remediation, and the decision on how to resolve it [DMBOK2-C13-41]. The decision owner is a business data owner [DMBOK2-C13-40]. The machine-readable form is `schemas/quality-issue.schema.json`.

| Field | Meaning |
|---|---|
| `issue_id` | Unique id. |
| `description` | What is wrong, stated from evidence. |
| `root_causes` | Candidate causes, labelled as hypotheses until a human confirms. May be empty if unknown. |
| `remediation_options` | The options for resolving it. |
| `decision` | `Pending` until a human decides. An agent never records a decision. |
| `decision_owner` | The business data owner who decides. |
| `evidence_ids` | Optional `source_id` values of the evidence records behind the issue. |
