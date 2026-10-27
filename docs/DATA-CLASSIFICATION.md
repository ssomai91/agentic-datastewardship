# Data Confidentiality Labels

**Status:** Draft, pending owner review. Applies proposal P-12 (option 1). The scale is **provisional**: the DMBOK2 says each organisation should create or adopt its own classification scheme [DMBOK2-C07-09], and this scale is replaced by the organisation's scheme once it is found. The DMBOK2 example levels are GENERAL INDUSTRY CONTEXT [DMBOK2-C07-06].

## 1. Provisional scale

| Label (`confidentiality_label`) | Working meaning |
|---|---|
| `unassigned` | No level has been assigned by the Data Steward. The default. |
| `internal_use_only` | Limited to employees or members; minimal risk if shared inside the organisation. |
| `confidential` | Not to be shared outside the organisation without a proper agreement in place. |
| `restricted_confidential` | Limited to people with a need to know for their role. |

The DMBOK2 lists five example levels. Two of them, general audiences and registered confidential, are not used here: nothing in this repository is public, and no data here is of the registered kind.

## 2. Labelling rules

1. **Agents may propose** a label. They never assign one.
2. **The Data Steward assigns** the label, based on the organisation's scheme [DMBOK2-C07-10].
3. The label is **recorded as metadata** on the evidence record, in the optional `confidentiality_label` field of `schemas/evidence.schema.json` [DMBOK2-C07-16]. A record with no label is read as `unassigned`.
4. A confidentiality label says nothing about **regulatory restrictions**. Those are a separate question and need their own handling.
5. This repository holds synthetic data only (`GOVERNANCE-DECISIONS.md`, GD-02), so every record here is illustrative. The scale matters once an agent is connected to real data, which needs a separate approval.

## 3. Naming

The field is `confidentiality_label`, deliberately different from the `classification` field in `schemas/agent-contract.schema.json`, which classifies a *capability* (human responsibility, deterministic process, and so on), not data.
