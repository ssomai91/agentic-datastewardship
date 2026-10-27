"""Render docs/DMBOK-ALIGNMENT.md and docs/dmbok2-citations.json from the working files."""
import datetime
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".dmbok-work"
OUT_DOC = ROOT / "docs" / "DMBOK-ALIGNMENT.md"
OUT_INDEX = ROOT / "docs" / "dmbok2-citations.json"
OWNER = "Data Steward / project owner"


def load(name):
    return json.loads((WORK / name).read_text(encoding="utf-8"))


def cell(value):
    return " ".join(str(value).split()).replace("|", "/")


def ref(citation):
    number = citation["section"].split()[0]
    return f"{citation['id']} (ch.{citation['chapter']} §{number}, p.{citation['pdf_page']})"


def main():
    concepts = {c["id"]: c for c in load("concepts.json")}
    merged = load("merged.json")
    deviations = load("deviations.json")
    proposals = load("proposals.json")
    citations = {c["id"]: c for c in merged["citations"]}

    problems = [f"{p['id']}: no recommendation" for p in proposals if not p.get("recommendation")]
    problems += [f"{p['id']}: no options" for p in proposals if not p.get("options")]
    for p in proposals:
        for option in p["options"]:
            for cid in option["citation_ids"]:
                if cid not in citations:
                    problems.append(f"{p['id']}: option cites unknown or dropped {cid}")
    if merged["unverified_concepts"]:
        problems.append(f"concepts without a verified row: {merged['unverified_concepts']}")
    if problems:
        sys.exit("cannot render:\n - " + "\n - ".join(problems))

    stats = merged["stats"]
    out = []
    out.append("# DMBOK2 Alignment")
    out.append("")
    out.append("**Status:** Draft, pending owner review (not approved)  ")
    out.append(f"**Date:** {datetime.date.today().isoformat()}  ")
    out.append("**Spec:** docs/superpowers/specs/2026-10-01-dmbok-alignment-design.md  ")
    out.append("**Framing decisions:** the DMBOK2 is an industry reference only (GENERAL INDUSTRY CONTEXT); the project is aligned to it, not the reverse; the owner's original handoff files get pointer notes and minimal edits only.")
    out.append("")
    out.append("## 1. Source note")
    out.append("")
    out.append("- **Source:** DAMA-DMBOK (2nd Edition), DAMA International, supplied as a PDF-derived text conversion (`DAMA-DMBOK-2nd-Edition.md`, 1,050 PDF pages). The file is tracked in this private repository; citations in the docs use quotes of 25 words or fewer.")
    out.append("- **Status in the organisation:** industry reference only. Every DMBOK2 statement here is `GENERAL INDUSTRY CONTEXT`. ASSUMPTION - pending Data Steward / project owner confirmation: the organisation has not formally adopted the DMBOK2; adopting any element below is a proposal for human governance approval, and internal policy outranks it.")
    out.append("- **Citations:** referenced by ID and defined once in `docs/dmbok2-citations.json` (chapter, section, PDF page, quote). Each citation below is shown as `ID (ch.N §x.y, p.NNN)`. Page numbers are PDF pages (the `<!-- PDF page N -->` markers in the supplied file), not printed book pages.")
    out.append("- **Limits:** figures are missing from the conversion (209 image links point at a folder that does not exist), so figure-dependent claims are marked \"unverifiable from text\"; the text is from 2017 and predates LLM agents; it says \"critical data\" (Ch 13 §1.3.2 and §2.3) where this project says \"critical data element\", so terms are mapped, not renamed.")
    out.append("- **Status vocabulary:** Aligned · Partial · Divergent · Missing · Out of DMBOK scope. **Action vocabulary:** none · citation · wording · structural-proposal · record-deviation.")
    out.append("")
    out.append("## 2. Conformance matrix")
    out.append("")
    out.append("| ID | Area | Project concept | Where it lives in the repo | DMBOK2 term and citations | Status | Action | Decision owner |")
    out.append("|---|---|---|---|---|---|---|---|")
    for row in merged["rows"]:
        concept = concepts[row["concept_id"]]
        where = "; ".join(f"{loc['file']} ({loc['anchor']})" for loc in concept["repo_locations"])
        refs = "; ".join(ref(citations[i]) for i in row["citation_ids"]) or "no citation"
        terms = "; ".join(row["dmbok_terms"]) or "no DMBOK2 term"
        out.append("| " + " | ".join(cell(v) for v in (
            row["concept_id"], concept["area"], concept["name"], where, f"{terms} — {refs}",
            row["status"], row["action"], OWNER)) + " |")
    out.append("")
    out.append("## 3. Deviations register")
    out.append("")
    out.append("| ID | Deviation | Where it lives in the repo | Rationale | DMBOK2 position |")
    out.append("|---|---|---|---|---|")
    for d in deviations:
        out.append("| " + " | ".join(cell(d[k]) for k in ("id", "deviation", "location", "rationale", "dmbok_position")) + " |")
    out.append("")
    out.append("## 4. Proposals for human approval")
    out.append("")
    out.append("Nothing in this section is applied until the owner approves it item by item. Each proposal is a recommendation drawn from the DMBOK2 as general industry context, not a decision.")
    out.append("")
    out.append("| ID | Concept | Proposal | Options | Recommendation | Decision owner | Decision |")
    out.append("|---|---|---|---|---|---|---|")
    for p in proposals:
        options = "; ".join(f"({i}) {o['label']}: {o['description']}" for i, o in enumerate(p["options"], start=1))
        out.append("| " + " | ".join(cell(v) for v in (
            p["id"], p["concept_id"], p["title"], options, p["recommendation"], p["decision_owner"], p["decision"])) + " |")
    out.append("")
    out.append("## Appendix A — DMBOK2 content flagged by readers but not in the concept list")
    out.append("")
    out.append("Not added to the matrix automatically; the owner decides whether to accept any of it.")
    out.append("")
    out.append("| Topic | Citations | Why it may matter | Reader unit |")
    out.append("|---|---|---|---|")
    for item in merged["additional_content"]:
        shown = "; ".join(ref(citations[i]) for i in item["citation_ids"])
        out.append("| " + " | ".join(cell(v) for v in (item["topic"], shown, item["why_relevant"], item["unit"])) + " |")
    out.append("")
    out.append("## Appendix B — Verification record")
    out.append("")
    out.append(f"- Citations proposed by readers: {stats['citations_proposed']}; failed the page-marker check: {stats['citations_failed_script']}; not supported according to the independent verifier: {stats['citations_unsupported']}; indexed: {len(citations)}.")
    out.append(f"- Concept-unit rows read: {stats['rows_read']}; graded as proposed: {stats['rows_agreed']}; regraded by the verifier: {stats['rows_regraded']}; excluded as unverified: {stats['rows_unverified']}.")
    out.append(f"- Concepts with a verified row: {stats['concepts_with_verified_row']} of {stats['concepts_total']}.")
    out.append("")
    out.append("## Appendix C — Source caveats reported by readers")
    out.append("")
    for caveat in merged["source_caveats"]:
        out.append(f"- {cell(caveat)}")
    out.append("")
    OUT_DOC.write_text("\n".join(out), encoding="utf-8")
    index = [{k: c[k] for k in ("id", "chapter", "section", "pdf_page", "quote")}
             for c in sorted(citations.values(), key=lambda c: c["id"])]
    OUT_INDEX.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT_DOC} ({len(merged['rows'])} matrix rows) and {OUT_INDEX} ({len(index)} citations)")


if __name__ == "__main__":
    main()
