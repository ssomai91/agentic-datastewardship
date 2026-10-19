"""Write .dmbok-work/prompts/verifier-unit-N.md for every reading unit."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "tests"))
from dmbok_citations import ALLOWED_ACTIONS  # noqa: E402
from promptlib import DMBOK, WORK, concept_block, describe_ranges, load_concepts, load_units  # noqa: E402

TEMPLATE = """You are an independent VERIFIER. You did not write the rows you are checking, and your job is to try to refute them.

RULES OF THE ROAD
- READ-ONLY except for the single output file named at the end. Work only from text you read yourself.
- The DMBOK2 is an INDUSTRY REFERENCE ONLY for this organisation ("GENERAL INDUSTRY CONTEXT"); internal policy outranks it.

WHAT YOU ARE CHECKING
A reader produced .dmbok-work/rows/unit-__UNIT__.json for unit __UNIT__ - __TITLE__ (citations plus one row per assigned concept). Read that file first. The DMBOK2 text (a PDF-to-markdown conversion with `<!-- PDF page N -->` markers) is at __DMBOK_PATH__. Read the reader's assigned ranges yourself, with the Read tool, at most 400 lines per call: __RANGES__.

CONCEPTS (what the project says, and where)
__CONCEPTS__

TASKS
1. For EVERY citation: open the passage (find the marker for its pdf_page and read at least 15 lines either side) and judge whether the quote, in context, supports what the reader's rows say the DMBOK2 position is. Answer yes (supports), partly (supports only in part, or the surrounding text qualifies it), or no (it does not support it, or the surrounding text contradicts or limits it).
2. For EVERY row: read the project files for the concept and the relevant DMBOK2 passages yourself, and judge whether the proposed status and action are fair. Use agree; too_generous (the status hides a gap the evidence shows); too_harsh (the status overstates a gap); or unsure. When not agree, give suggested_status (and suggested_action if the action must change). Status: Aligned | Partial | Divergent | Missing | Out of DMBOK scope. Action: none | citation | wording | structural-proposal | record-deviation. Allowed combinations: __ALLOWED__.
3. List anything in your range the reader missed that would change a grade (missing_findings), with the pdf_page and a short note.
Be adversarial but fair: do not answer yes or agree just because a quote exists on the page.

OUTPUT
Write ONE JSON file, .dmbok-work/verify/unit-__UNIT__.json (the only file you may create), then reply with the single line: WROTE .dmbok-work/verify/unit-__UNIT__.json
{
  "unit": __UNIT__,
  "citation_verdicts": [{"id": "DMBOK2-C03-01", "supports_claim": "yes", "note": ""}],
  "row_verdicts": [{"concept_id": "A-01", "status_fair": "agree", "suggested_status": null, "suggested_action": null, "note": ""}],
  "missing_findings": [{"concept_id": "A-01", "pdf_page": 152, "note": "what the reader missed"}]
}
Exactly one citation_verdict per citation and exactly one row_verdict per row in the reader's file.
"""


def main():
    concepts = load_concepts()
    allowed = "; ".join(f"{status} -> {' | '.join(actions)}" for status, actions in ALLOWED_ACTIONS.items())
    out = WORK / "prompts"
    out.mkdir(exist_ok=True)
    for unit in load_units():
        text = (
            TEMPLATE.replace("__UNIT__", str(unit["unit"]))
            .replace("__TITLE__", unit["title"])
            .replace("__RANGES__", describe_ranges(unit))
            .replace("__DMBOK_PATH__", str(DMBOK))
            .replace("__CONCEPTS__", concept_block(concepts, unit["unit"]))
            .replace("__ALLOWED__", allowed)
        )
        target = out / f"verifier-unit-{unit['unit']}.md"
        target.write_text(text, encoding="utf-8")
        print("wrote", target)


main()
