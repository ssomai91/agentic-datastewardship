"""Write .dmbok-work/prompts/reader-unit-N.md for every reading unit."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from promptlib import DMBOK, WORK, concept_block, describe_ranges, load_concepts, load_units  # noqa: E402

TEMPLATE = """You are a READER on a review of how a data-stewardship project aligns with the DAMA-DMBOK (2nd edition).

RULES OF THE ROAD
- READ-ONLY. Do not modify, create or delete any file except the single output file named at the end. Do not run shell commands that write anywhere.
- Work only from text you read. Do not rely on memory of the book: every claim about what the DMBOK2 says must be backed by a passage you read in your assigned range.
- The DMBOK2 is an INDUSTRY REFERENCE ONLY for this organisation: every DMBOK2 statement is "GENERAL INDUSTRY CONTEXT"; adopting any element is a proposal needing human approval; internal policy outranks it.

CONTEXT
The repository (your working directory) designs an AI-augmented stewardship capability for an Investment Operations Data Steward. Its principle: "AI proposes, evidence supports, the Data Steward evaluates, the appropriate human owner approves." The DMBOK2 text is a PDF-to-markdown conversion at __DMBOK_PATH__. Every PDF page starts with a marker line like `<!-- PDF page 152 -->`. Figures are missing (their image links are dead). Section headings carry numbers, for example `#### _1.3.5 Types of Data Stewards_`.

YOUR READING UNIT: unit __UNIT__ - __TITLE__
Read ONLY these line ranges of the DMBOK file, with the Read tool, at most 400 lines per call (use offset and limit): __RANGES__. You may also read lines 1-1004 (the table of contents) if you need chapter or section numbers. Read your whole range; do not skim and then generalise.

CONCEPTS ASSIGNED TO YOU
__CONCEPTS__
Open the listed repo files and read the passage around each anchor phrase so you know exactly what the project says before comparing.

TASK
For EACH assigned concept (one row each, no more and no fewer):
1. Find what the DMBOK2 says that is relevant: its terminology, definitions, roles, practices, deliverables.
2. Compare it with the project's position.
3. Propose a status and an action.
STATUS (exactly one): Aligned | Partial | Divergent | Missing | Out of DMBOK scope
- Aligned: concept and wording match DMBOK2 guidance.
- Partial: the concept is present but misses elements the DMBOK2 treats as essential, or uses different terms.
- Divergent: contradicts or conflicts with DMBOK2 guidance (needs a decision).
- Missing: the DMBOK2 treats it as part of stewardship in scope and the project has no artefact.
- Out of DMBOK scope: project-specific (for example AI-agent controls); the DMBOK2 is silent.
ACTION (exactly one): none | citation | wording | structural-proposal | record-deviation
- structural-proposal = adopting a DMBOK2 construct (a role vocabulary, a dimension set, a lifecycle, a field). Give at least two options when the DMBOK2 itself offers alternatives, and say which citation backs each.
- Allowed combinations: Aligned -> none | citation | wording; Partial -> wording | structural-proposal | record-deviation; Divergent -> structural-proposal | record-deviation; Missing -> structural-proposal | record-deviation; Out of DMBOK scope -> none | record-deviation.

CITATION RULES (machine-checked; a failing citation is dropped)
- Each citation is {"id", "chapter", "section", "pdf_page", "quote"}.
- id = DMBOK2-Cnn-nn, where nn counts 01, 02, ... separately for each chapter in your unit; chapter is the number in the id.
- section = the nearest heading ABOVE the quote, starting with its number, for example "1.3.5 Types of Data Stewards".
- pdf_page = the number in the nearest `<!-- PDF page N -->` marker ABOVE the quoted text.
- quote = contiguous text copied from the file: at most 25 words, entirely within one page, no ellipses, no bracketed edits. Plain words are fine (the check ignores markdown emphasis, HTML tags and curly versus straight quotes).
- Never reproduce more than 25 consecutive words. Everything else is your own paraphrase and must read as paraphrase.
- If a claim depends on a figure, add "unverifiable from text" to the row's caveats.
- If the DMBOK2 in your range does not address a concept, say so in dmbok_position and use status Out of DMBOK scope or Missing as the facts warrant.

OUTPUT
Write ONE JSON file, .dmbok-work/rows/unit-__UNIT__.json (the only file you may create), with exactly this shape, then reply with the single line: WROTE .dmbok-work/rows/unit-__UNIT__.json
{
  "unit": __UNIT__,
  "citations": [{"id": "DMBOK2-C03-01", "chapter": 3, "section": "1.3.5 Types of Data Stewards", "pdf_page": 152, "quote": "text copied from the file"}],
  "rows": [{
    "concept_id": "A-01",
    "dmbok_terms": ["DMBOK2 term for the concept"],
    "citation_ids": ["DMBOK2-C03-01"],
    "dmbok_position": "one or two sentences in your own words",
    "caveats": [],
    "proposed_status": "Partial",
    "status_rationale": "why, naming the project artefact you compared",
    "proposed_action": "wording",
    "proposal_options": []
  }],
  "additional_content": [{"topic": "short topic", "citation_ids": ["DMBOK2-C03-01"], "why_relevant": "one sentence"}],
  "source_caveats": ["anything about the converted text that limits what can be concluded"]
}
proposal_options is [] unless proposed_action is structural-proposal. additional_content lists at most 6 DMBOK2 topics in your range that matter for stewardship in this project but are covered by no assigned concept. Every status other than Out of DMBOK scope needs at least one citation id.
"""


def main():
    concepts = load_concepts()
    out = WORK / "prompts"
    out.mkdir(exist_ok=True)
    for unit in load_units():
        text = (
            TEMPLATE.replace("__UNIT__", str(unit["unit"]))
            .replace("__TITLE__", unit["title"])
            .replace("__RANGES__", describe_ranges(unit))
            .replace("__DMBOK_PATH__", str(DMBOK))
            .replace("__CONCEPTS__", concept_block(concepts, unit["unit"]))
        )
        target = out / f"reader-unit-{unit['unit']}.md"
        target.write_text(text, encoding="utf-8")
        print("wrote", target)


main()
