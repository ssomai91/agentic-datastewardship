# DMBOK2 Alignment — Design Spec

**Status:** Draft for owner review (not approved, not committed)
**Date:** 2026-10-01
**Path:** Architectural (touches shared vocabulary, schema fields and contracts that other artefacts depend on)

## 1. Request and decisions already taken

Request: review `DAMA-DMBOK-2nd-Edition.md` (repo root) and align this project to it.

Decisions made with the owner during brainstorming:

| # | Decision | Consequence |
|---|---|---|
| D-1 | Direction: **align the project to the DMBOK2**; the DMBOK file is only read, never edited | The deliverable is a mapping plus targeted edits to the project |
| D-2 | Status of the DMBOK2 in the organisation: **industry reference only** | Every DMBOK2 citation is labelled `GENERAL INDUSTRY CONTEXT`; adopting any specific element is a **proposal needing human governance approval**; internal policy (if any) outranks it (project principle 3) |
| D-3 | Owner's original handoff files (`README.md`, `HANDOFF.md`, `ARCHITECTURE.md`, `BUILD-BACKLOG.md`, `AGENT-CONTRACT-TEMPLATE.md`): **pointer notes plus minimal wording edits** | Everything derived from them is fully aligned; the originals change only where DMBOK2 terminology genuinely differs |
| D-4 | Approach **A: mapping-led and targeted** (~30 concepts, ~10 chapters, verified citations) | Not an exhaustive 17-chapter walk, not a terminology-only crosswalk |

## 2. Scope

**In scope**

- ~30 project concepts, derived from the repo itself (Step 0, section 5): stewardship roles and decision rights, business definitions and critical data elements, glossary / data dictionary / documentation, lineage and source-to-target mapping, data-quality dimensions / rules / controls / issue management / root cause, reference and master data, classification / security / ethics, governance reporting and forums.
- DMBOK2 chapters **2** (Data Handling Ethics), **3** (Data Governance), **4** (Data Architecture), **7** (Data Security), **8** (Data Integration and Interoperability), **10** (Reference and Master Data), **12** (Metadata Management), **13** (Data Quality), **15** (Data Management Maturity Assessment), **16** (Data Management Organization and Role Expectations).

**Out of scope**

- DMBOK2 chapters 1, 5, 6, 9, 11, 14, 17 (read only where a cross-reference requires it).
- Unrelated defects found in the earlier project review (wrapper tool grants, approval-record schema, test-suite depth, etc.). They are tracked separately and are not touched here unless a DMBOK2 alignment item directly depends on them.
- Creating new agents or changing the factory process.

## 3. Deliverables

**D1. `docs/DMBOK-ALIGNMENT.md`** (new, Draft). Four parts:

1. *Source note* — the DMBOK2 as supplied (PDF-derived, figures missing, 2017 edition), its status (`GENERAL INDUSTRY CONTEXT`, adoption pending), citation format.
2. *Conformance matrix* (~30 rows) — columns: `ID`, `Area`, `Project concept`, `Where it lives in the repo`, `DMBOK2 term and citations` (each shown as `ID (ch.N §x.y, p.NNN)`, checked against the index by a test), `Status`, `Action`, `Decision owner`.
3. *Deviations register* — where the project intentionally goes beyond or differs from DMBOK2 (mainly AI-specific controls: the human-approval model, the evidence and five-label confidence policy, agent contracts), each with a rationale.
4. *Proposals for human approval* — each structural adoption written as a proposal with options (e.g. steward-role vocabulary, a DQ-dimension set to close Open Question 5, CDE criteria, a classification scheme, a DQ issue lifecycle), with an owner. Nothing here is applied until approved item by item.

**D2. Edits to the project** (only after D1 is approved), in tiers:

| Tier | What | Rule |
|---|---|---|
| 1 | Wording and citations in `docs/`, contract text (markdown **and** JSON kept in step), `.claude/agents/` wrappers, `evals/` | Low risk. Terminology aligned; DMBOK2 listed as a `GENERAL INDUSTRY CONTEXT` source, never as internal truth |
| 2 | Structural: optional schema fields or enums (e.g. steward role, DQ dimension), small new docs | Only items approved in D1 part 4. Each change updates schema, contracts and tests together |
| 3 | Deviations | Recorded in D1 part 3; no change |
| Originals | Pointer note (“aligned with DMBOK2 as general industry context, see `docs/DMBOK-ALIGNMENT.md`”) plus minimal wording | Per decision D-3 |

**D3. Citation index and tests.** `docs/dmbok2-citations.json` is the single registry of DMBOK2 citations: `id` (e.g. `DMBOK2-C13-01`), `chapter`, `section`, `pdf_page`, `quote` (≤ 25 words). All other files cite by ID. Tests are described in section 7.

**D4. `.gitignore` entry** for `DAMA-DMBOK-2nd-Edition.md` and its assets folder (default; the owner can ask for the file to be committed instead). The file is a full copy of a copyrighted book; only ≤ 25-word quotes enter the repo.

## 4. Rules

**Status vocabulary (matrix)**

| Status | Meaning |
|---|---|
| Aligned | Concept and wording match DMBOK2 guidance; action is at most a citation |
| Partial | Concept is present but misses elements DMBOK2 treats as essential, or uses different terms |
| Divergent | Project contradicts or conflicts with DMBOK2 guidance; needs a decision |
| Missing | DMBOK2 treats it as part of stewardship in scope and the project has no artefact |
| Out of DMBOK scope | Project-specific (e.g. AI-agent controls); DMBOK2 is silent |

**Action vocabulary:** `none` · `citation` · `wording` · `structural-proposal` · `record-deviation`.

**Conflict rule.** DMBOK2 wins where the project merely uses different words for data-management concepts, roles or practices. The AI-specific controls stay (DMBOK2 is silent on them). Any other conflict is surfaced as a decision for the owner and is never silently changed. Internal policy outranks DMBOK2.

**Labelling and quoting.** Every DMBOK2-derived statement carries `GENERAL INDUSTRY CONTEXT` where it appears in agent-facing text. Verbatim quotes are ≤ 25 words; paraphrase is marked as paraphrase. Citation format in prose: `DMBOK2 ch.N §x.y, PDF p.NNN`. Page numbers are **PDF pages** (the `<!-- PDF page N -->` markers), not printed book pages.

## 5. Method

- **Step 0 — concept list.** Derived from the repo: README scope list, HANDOFF decision and evidence policies, architecture and risk docs, contract `responsible_for` lists, schemas. Recorded in D1.
- **Step 1 — seven read-only reading units** (about 8,800 of the file's 17,653 lines), run as plain subagents: (1) ethics and security (Ch 2, 7); (2) governance, roles and operating models (Ch 3); (3) architecture and integration, lineage and source-to-target mapping (Ch 4, 8); (4) reference and master data (Ch 10); (5) metadata — glossary, dictionary, lineage (Ch 12); (6) data quality (Ch 13); (7) maturity and organisation roles (Ch 15, 16).
  Each reader returns, per concept: DMBOK2's own terminology, the passage (`chapter`, `section`, `pdf_page`, quote ≤ 25 words), the DMBOK2's own caveats (e.g. no agreement on a single DQ dimension set), a proposed status and action; plus relevant DMBOK2 content missing from the concept list, and source caveats (missing figures, conversion noise).
- **Step 2 — two-layer verification** before anything enters D1: (a) a script confirms each quote exists in the file and lies under the cited `PDF page` marker; (b) an independent verifier per unit re-reads each passage and checks that it supports the claim and that the status grade is fair. Rows that fail are corrected, marked `unverified`, or dropped.
- **Step 3 — synthesis.** The orchestrating session assembles D1 from verified rows and drafts the deviations and proposals. DMBOK2 content that readers flag as relevant but absent from the concept list goes into an appendix to D1 for the owner to accept into the matrix or discard; the matrix is never extended automatically.
- **Step 4 — owner review gate** on D1. **Step 5 — apply** approved D2 items; the implementation plan for Tiers 1 and 2 is written only after D1 is approved, because the specific edits depend on the matrix contents and on which proposals are approved. The plan written now covers Steps 0–4 (through the owner review gate), D3 (tests) and D4 (`.gitignore`). **Step 6 — tests green and owner sign-off.**
- **Cost.** About 7 readers + 7 verifiers + synthesis; estimate 1–2 million subagent tokens. No multi-agent workflow framework; the DMBOK file is only read.

## 6. Source limits (stated in D1)

- The supplied file is a text conversion: 209 image links point at a non-existent assets folder, so figure-dependent claims are marked “unverifiable from text”.
- The DMBOK2 (2017) predates LLM agents; the deviations register is expected to be non-empty.
- The text says “critical data” (Ch 13 §1.3.2 and §2.3); the literal phrase “critical data element” occurs only once. The project’s term is mapped, not renamed, unless the owner approves.

## 7. Tests (small)

1. **Citation resolution.** Every `DMBOK2-…` ID used anywhere in the repo exists in `docs/dmbok2-citations.json`. When `DAMA-DMBOK-2nd-Edition.md` is present, each indexed quote is found in the file under its stated PDF page marker; this part is **skipped** when the file is absent (fresh clones).
2. **Vocabulary.** Matrix `Status` and `Action` values use the allowed vocabularies; any vocabulary introduced by an approved Tier 2 change is identical in the schema, the contracts and the docs.
3. All existing tests (37) remain green.

## 8. Risks

| Risk | Mitigation |
|---|---|
| Over-adopting DMBOK2 structure and adding specification the project does not need | Tier 2 is item-by-item and owner-approved; the matrix is capped at ~30 rows |
| Misaligned page markers give false precision | Quote-presence check against the marker (section 5, Step 2a) |
| A reader misstates what DMBOK2 says | Independent verifier per unit (Step 2b); ≤ 25-word quotes only |
| Alignment silently overrides internal policy | Conflict rule; D-2 labelling; proposals need approval |
| The DMBOK file is committed by accident | D4 `.gitignore` default |

## 9. Done when

1. Every in-scope concept has a **verified** matrix row.
2. Every structural proposal is decided (approved, rejected or deferred) by the owner.
3. Approved Tier 1 / Tier 2 edits and the pointer notes are applied; markdown and JSON contract twins remain in step.
4. The two new tests pass and the 37 existing tests stay green.
5. The owner has signed off D1.
