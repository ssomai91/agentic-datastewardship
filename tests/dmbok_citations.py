"""Helpers for checking DMBOK2 citations against the supplied markdown conversion.

The conversion marks every PDF page with ``<!-- PDF page N -->``. A citation is valid when
its quote (25 words or fewer) occurs in the text of the cited PDF page after whitespace and
markup normalisation.

Command line (run from the repository root):

    python tests/dmbok_citations.py path/to/citations.json

The JSON file is either a list of citations or an object with a ``citations`` list.
Set DMBOK_MD to point at the DMBOK file if it is not in the repository root.
"""
from __future__ import annotations

import functools
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DMBOK_PATH = Path(os.environ.get("DMBOK_MD", ROOT / "DAMA-DMBOK-SUMMARY.md"))
INDEX_PATH = ROOT / "docs" / "dmbok2-citations.json"

PAGE_MARKER = re.compile(r"<!--\s*PDF page (\d+)\s*-->")
ID_PATTERN = re.compile(r"^DMBOK2-C(\d{2})-(\d{2})$")
SECTION_PATTERN = re.compile(r"^\d+(?:\.\d+)*(?:\s|$)")
REQUIRED_KEYS = ("id", "chapter", "section", "pdf_page", "quote")
MAX_QUOTE_WORDS = 25

# Vocabulary of the conformance matrix in docs/DMBOK-ALIGNMENT.md (single source of truth).
STATUS_VALUES = {"Aligned", "Partial", "Divergent", "Missing", "Out of DMBOK scope"}
ACTION_VALUES = {"none", "citation", "wording", "structural-proposal", "record-deviation"}
ALLOWED_ACTIONS = {
    "Aligned": ["none", "citation", "wording"],
    "Partial": ["wording", "structural-proposal", "record-deviation"],
    "Divergent": ["structural-proposal", "record-deviation"],
    "Missing": ["structural-proposal", "record-deviation"],
    "Out of DMBOK scope": ["none", "record-deviation"],
}
DEFAULT_ACTION = {
    "Aligned": "citation",
    "Partial": "wording",
    "Divergent": "structural-proposal",
    "Missing": "structural-proposal",
    "Out of DMBOK scope": "record-deviation",
}

_CHAR_MAP = str.maketrans({
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", " ": " ",
})


def normalise(text: str) -> str:
    """Make a quote comparable with converted text: quotes, dashes, markup, whitespace, case."""
    text = text.translate(_CHAR_MAP)
    text = re.sub(r"<sup>[^<]*</sup>", "", text)                   # footnote numbers
    text = re.sub(r"</?(?:u|sup|sub|b|i|em|strong)>", "", text)    # other inline html
    text = re.sub(r"[*_`#>]+", "", text)                           # markdown emphasis / heading marks
    return re.sub(r"\s+", " ", text).strip().lower()


@functools.lru_cache(maxsize=4)
def load_pages(path: Path = DMBOK_PATH) -> dict[int, str]:
    """Return {pdf_page: normalised page text} for the DMBOK conversion at *path*."""
    parts = PAGE_MARKER.split(Path(path).read_text(encoding="utf-8"))
    return {int(parts[i]): normalise(parts[i + 1]) for i in range(1, len(parts), 2)}


def find_quote_pages(pages: dict[int, str], quote: str) -> list[int]:
    needle = normalise(quote)
    return sorted(number for number, text in pages.items() if needle in text)


def validate_citation(citation: dict, pages: dict[int, str] | None = None) -> list[str]:
    """Return a list of problems (empty when the citation is valid).

    Structural checks always run; the quote-on-page check runs when *pages* is given.
    """
    missing = [key for key in REQUIRED_KEYS if key not in citation]
    if missing:
        return [f"missing keys: {missing}"]
    cid = citation["id"]
    problems: list[str] = []
    match = ID_PATTERN.match(cid)
    if not match:
        problems.append(f"{cid}: id must match DMBOK2-Cnn-nn")
    elif int(match.group(1)) != citation["chapter"]:
        problems.append(f"{cid}: id chapter {match.group(1)} != chapter {citation['chapter']}")
    if not (isinstance(citation["chapter"], int) and 1 <= citation["chapter"] <= 17):
        problems.append(f"{cid}: chapter must be an int from 1 to 17")
    if not (isinstance(citation["pdf_page"], int) and citation["pdf_page"] >= 1):
        problems.append(f"{cid}: pdf_page must be a positive int")
    if not SECTION_PATTERN.match(str(citation["section"])):
        problems.append(f"{cid}: section must start with the heading number, e.g. '1.3.5 Types of Data Stewards'")
    words = len(str(citation["quote"]).split())
    if words == 0:
        problems.append(f"{cid}: quote is empty")
    elif words > MAX_QUOTE_WORDS:
        problems.append(f"{cid}: quote exceeds {MAX_QUOTE_WORDS} words ({words})")
    if pages is not None and not problems:
        page_text = pages.get(citation["pdf_page"])
        if page_text is None:
            problems.append(f"{cid}: PDF page {citation['pdf_page']} does not exist in the DMBOK file")
        elif normalise(citation["quote"]) not in page_text:
            found = find_quote_pages(pages, citation["quote"])
            hint = f"; found on page(s) {found}" if found else "; quote not found anywhere"
            problems.append(f"{cid}: quote not found on PDF page {citation['pdf_page']}{hint}")
    return problems


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    data = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    citations = data["citations"] if isinstance(data, dict) else data
    pages = load_pages()
    problems = [problem for citation in citations for problem in validate_citation(citation, pages)]
    for problem in problems:
        print(problem)
    print(f"{len(citations)} citations checked, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
