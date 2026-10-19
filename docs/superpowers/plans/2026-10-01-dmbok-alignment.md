# DMBOK2 Alignment Implementation Plan (Analysis, Matrix and Guardrails)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. **Tasks 4 and 5 are orchestration tasks** (they fan out to seven reader and seven verifier subagents); run them from a session that holds the Agent tool, or do the reading inline (see the failure-mode notes in those tasks).

**Goal:** Produce a verified, citable mapping between this project's stewardship concepts and the DMBOK2 (`docs/DMBOK-ALIGNMENT.md` + `docs/dmbok2-citations.json`), with tests that keep every citation honest, and stop at the owner review gate.

**Architecture:** A concept list derived from the repo is split across seven read-only reading units (DMBOK2 chapters); each reader writes cited rows, a script checks every quote against its PDF page marker, an independent verifier per unit attacks the rows, and a merge script plus a render script produce the alignment document and the single citation registry. Two small pytest modules guard citation resolution and the matrix vocabulary.

**Tech Stack:** Python 3.12.8, pytest 9.0.3 (already installed; no new dependencies), Claude Code subagents (`general-purpose`) for reading and verification, Git Bash on Windows.

**Spec:** `docs/superpowers/specs/2026-10-01-dmbok-alignment-design.md` (read it first; the plan argues from it).

**Scope of this plan:** spec Steps 0–4 (concept list → readers → verification → synthesis → owner review gate) and deliverables D1 (alignment document), D3 (citation index + tests) and D4 (`.gitignore`). **Deliberately not here:** D2, the Tier 1 / Tier 2 edits and the pointer notes in the owner's original files. Their content depends on the approved matrix, so they get their own plan after the owner reviews D1 (spec Step 5). The "vocabulary introduced by an approved Tier 2 change is identical across schema, contracts and docs" test belongs to that plan.

## Global Constraints

- DMBOK2 status in the organisation: **industry reference only**. Every DMBOK2-derived statement is labelled `GENERAL INDUSTRY CONTEXT`; adopting any element is a **proposal needing human governance approval**; internal policy outranks it (project principle 3).
- Direction: the **project is aligned to the DMBOK2**. `DAMA-DMBOK-2nd-Edition.md` is only ever read, never edited, moved or committed.
- Verbatim quotes are **≤ 25 words**; everything else is paraphrase and must read as paraphrase.
- Citation format in prose: `DMBOK2 ch.N §x.y, PDF p.NNN`. Page numbers are **PDF pages** (the `<!-- PDF page N -->` markers), not printed book pages. Citation IDs are `DMBOK2-Cnn-nn` and are defined once in `docs/dmbok2-citations.json`.
- Status vocabulary: `Aligned` · `Partial` · `Divergent` · `Missing` · `Out of DMBOK scope`. Action vocabulary: `none` · `citation` · `wording` · `structural-proposal` · `record-deviation`.
- Conflict rule: the DMBOK2 wins where the project merely uses different words for data-management concepts, roles or practices; the AI-specific controls stay (the DMBOK2 is silent on them); any other conflict is surfaced as a decision for the owner, never silently changed.
- The 37 existing tests must stay green after every task. The existing vendor-name guard in `tests/test_contracts.py` (the test whose name starts `test_no_` and ends `_in_deliverable_content`) scans every file under `docs/`, including `docs/superpowers/`: the one product name it forbids must not appear in any new file there, and that includes this plan, so never quote that test's full name in a document.
- Run every Python helper from the repository root, from a script file (not a `python - <<EOF` heredoc). In this Git Bash, `grep -iF` aborts; use `grep -ci` (no `-F`) or the Grep tool.
- Working files live in `.dmbok-work/` (git-ignored, created in Task 3). If the plan is executed in a git worktree, the untracked DMBOK file is absent there: set the environment variable `DMBOK_MD` to its absolute path in the main tree.
- **Commits:** do not run `git commit` or `git push` unless the owner has explicitly authorised commits in the session. Each task ends with a commit step showing the exact commands; if commits are not authorised, skip that step and leave the changes in the working tree. Never `git add` the DMBOK file, `.dmbok-work/`, or the spec/plan files unless the owner says so.
- If a subagent returns an organisation "Token Efficiency Check" card instead of work, that is the organisation's first-turn rule firing inside the subagent. **Do not add a skip phrase on the owner's behalf.** Stop and ask the owner whether to (a) allow `/skip check` in subagent prompts, (b) do the reading inline in the main session, or (c) change the organisation rule.

## File Structure

| File | Status | Responsibility |
|---|---|---|
| `tests/dmbok_citations.py` | Create | Shared support module and CLI: page loading, quote normalisation, citation validation, matrix vocabulary constants |
| `tests/test_dmbok_citation_helpers.py` | Create | Hermetic unit tests for the support module (synthetic text, no DMBOK file needed) |
| `tests/test_dmbok_alignment.py` | Create | Repo-level guardrails: index well-formed, cited IDs resolve, quotes sit on their PDF page (skipped when the DMBOK file is absent), matrix vocabulary and index agreement |
| `docs/dmbok2-citations.json` | Create | The single registry of DMBOK2 citations (`id`, `chapter`, `section`, `pdf_page`, `quote`) |
| `docs/DMBOK-ALIGNMENT.md` | Create | D1: source note, conformance matrix, deviations register, proposals, appendices |
| `.gitignore` | Modify | Keep the DMBOK file, its assets folder and `.dmbok-work/` out of git |
| `.dmbok-work/` (ignored) | Create | `concepts.json`, `units.json`, `promptlib.py`, `check_concepts.py`, `check_unit.py`, prompt generators, `rows/`, `verify/`, `prompts/`, `merged.json`, `deviations.json`, `proposals.json`, `merge_rows.py`, `draft_proposals.py`, `render_alignment.py`, `summarise.py` |

---

### Task 1: Citation support module (TDD)

**Files:**
- Create: `tests/dmbok_citations.py`
- Test: `tests/test_dmbok_citation_helpers.py`

**Interfaces:**
- Produces (module `dmbok_citations`, importable from tests because `tests/` has no `__init__.py`):
  - constants: `ROOT: Path`, `DMBOK_PATH: Path` (env `DMBOK_MD` overrides), `INDEX_PATH: Path`, `MAX_QUOTE_WORDS = 25`, `ID_PATTERN`, `REQUIRED_KEYS`, `STATUS_VALUES: set[str]`, `ACTION_VALUES: set[str]`, `ALLOWED_ACTIONS: dict[str, list[str]]`, `DEFAULT_ACTION: dict[str, str]`
  - `normalise(text: str) -> str`
  - `load_pages(path: Path = DMBOK_PATH) -> dict[int, str]` (cached; values are normalised page text)
  - `find_quote_pages(pages: dict[int, str], quote: str) -> list[int]`
  - `validate_citation(citation: dict, pages: dict[int, str] | None = None) -> list[str]` (empty list = valid)
  - `main(argv: list[str]) -> int` (CLI: `python tests/dmbok_citations.py <file.json>`)

- [ ] **Step 1: Write the failing tests**

Create `tests/test_dmbok_citation_helpers.py`:

```python
import pytest

from dmbok_citations import (
    MAX_QUOTE_WORDS,
    find_quote_pages,
    load_pages,
    normalise,
    validate_citation,
)

SAMPLE = (
    "# Title\n\n"
    "<!-- PDF page 1 -->\n\n"
    "First page has a **bold** claim and a “curly quote”.\n\n"
    "<!-- PDF page 2 -->\n\n"
    "Second page says <u>Data</u> Stewards are accountable for\n"
    "data quality — always.\n"
)


@pytest.fixture()
def pages(tmp_path):
    path = tmp_path / "dmbok.md"
    path.write_text(SAMPLE, encoding="utf-8")
    return load_pages(path)


def _citation(**overrides):
    base = {
        "id": "DMBOK2-C03-01",
        "chapter": 3,
        "section": "1.3.5 Types of Data Stewards",
        "pdf_page": 2,
        "quote": "Data Stewards are accountable for data quality",
    }
    base.update(overrides)
    return base


def test_normalise_unifies_quotes_dashes_markup_and_whitespace():
    assert normalise("A  **B**\n<u>c</u> “d” —e") == 'a b c "d" -e'


def test_normalise_drops_footnote_numbers():
    assert normalise("stewardship<sup>12</sup> matters") == "stewardship matters"


def test_load_pages_splits_on_pdf_page_markers(pages):
    assert sorted(pages) == [1, 2]
    assert 'a "curly quote"' in pages[1]
    assert "bold claim" in pages[1]


def test_find_quote_pages_returns_only_pages_containing_the_quote(pages):
    assert find_quote_pages(pages, "Stewards are accountable for data quality") == [2]
    assert find_quote_pages(pages, "no such text anywhere") == []


def test_valid_citation_has_no_problems(pages):
    assert validate_citation(_citation(), pages) == []


def test_quote_on_wrong_page_is_reported_with_the_right_page(pages):
    problems = validate_citation(_citation(pdf_page=1), pages)
    assert len(problems) == 1
    assert "not found on PDF page 1" in problems[0]
    assert "found on page(s) [2]" in problems[0]


def test_nonexistent_page_is_reported(pages):
    assert validate_citation(_citation(pdf_page=99), pages) == [
        "DMBOK2-C03-01: PDF page 99 does not exist in the DMBOK file"
    ]


def test_quote_longer_than_limit_is_rejected():
    long_quote = " ".join(["word"] * (MAX_QUOTE_WORDS + 1))
    problems = validate_citation(_citation(quote=long_quote))
    assert any("exceeds 25 words" in p for p in problems)


def test_bad_id_and_chapter_mismatch_are_rejected():
    assert any("must match" in p for p in validate_citation(_citation(id="DMBOK2-3-1")))
    assert any("id chapter 03 != chapter 4" in p for p in validate_citation(_citation(chapter=4)))


def test_section_must_start_with_a_heading_number():
    problems = validate_citation(_citation(section="Types of Data Stewards"))
    assert any("section must start with the heading number" in p for p in problems)


def test_missing_keys_are_reported():
    assert validate_citation({"id": "DMBOK2-C03-01"}) == [
        "missing keys: ['chapter', 'section', 'pdf_page', 'quote']"
    ]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_dmbok_citation_helpers.py -v`
Expected: collection ERROR with `ModuleNotFoundError: No module named 'dmbok_citations'`.

- [ ] **Step 3: Write the minimal implementation**

Create `tests/dmbok_citations.py`:

```python
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
DMBOK_PATH = Path(os.environ.get("DMBOK_MD", ROOT / "DAMA-DMBOK-2nd-Edition.md"))
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_dmbok_citation_helpers.py -v`
Expected: `11 passed`.

- [ ] **Step 5: Run the whole suite**

Run: `python -m pytest -q`
Expected: `48 passed` (37 existing + 11 new).

- [ ] **Step 6: Commit (only if the owner has authorised commits)**

```bash
git switch -c feature/dmbok-alignment   # only if currently on main
git add tests/dmbok_citations.py tests/test_dmbok_citation_helpers.py
git commit -m "test: add DMBOK2 citation support module and unit tests"
```

---

### Task 2: Citation registry, repo-level guardrail tests, `.gitignore` (D3 part 1, D4)

**Files:**
- Create: `docs/dmbok2-citations.json`
- Create: `tests/test_dmbok_alignment.py`
- Modify: `.gitignore` (append three lines after line 5)

**Interfaces:**
- Consumes: `dmbok_citations.DMBOK_PATH`, `INDEX_PATH`, `ROOT`, `load_pages`, `validate_citation` (Task 1).
- Produces: `docs/dmbok2-citations.json` (JSON list of `{id, chapter, section, pdf_page, quote}`); tests that Task 6 extends; the ignore rules the later tasks rely on.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_dmbok_alignment.py`:

```python
import json
import re

import pytest

from dmbok_citations import DMBOK_PATH, INDEX_PATH, ROOT, load_pages, validate_citation

CITATION_ID = re.compile(r"DMBOK2-C\d{2}-\d{2}")
# Files that may cite DMBOK2 ids. docs/superpowers/ (specs and plans) is deliberately excluded.
SCAN_GLOBS = ["*.md", "docs/*.md", "agents/**/*.md", "contracts/*.json", "evals/*.md", ".claude/agents/*.md"]


def _index():
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


INDEX = _index()


def test_citation_index_entries_are_well_formed_and_unique():
    ids = [citation.get("id") for citation in INDEX]
    assert len(ids) == len(set(ids)), "duplicate citation ids in docs/dmbok2-citations.json"
    for citation in INDEX:
        assert validate_citation(citation) == [], citation.get("id")


def _scanned_files():
    files = set()
    for pattern in SCAN_GLOBS:
        for path in ROOT.glob(pattern):
            if path.is_file() and path.name != DMBOK_PATH.name:
                files.add(path)
    return sorted(files)


def test_every_dmbok2_id_cited_in_the_repo_exists_in_the_index():
    known = {citation["id"] for citation in INDEX}
    unknown = {}
    for path in _scanned_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for cid in CITATION_ID.findall(text):
            if cid not in known:
                unknown.setdefault(str(path.relative_to(ROOT)), set()).add(cid)
    assert not unknown, f"citation ids missing from docs/dmbok2-citations.json: {unknown}"


@pytest.mark.skipif(not DMBOK_PATH.exists(), reason="DMBOK file not present (kept out of git)")
@pytest.mark.parametrize("citation", INDEX, ids=[c["id"] for c in INDEX])
def test_quote_is_on_the_cited_pdf_page(citation):
    assert validate_citation(citation, load_pages(DMBOK_PATH)) == []
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_dmbok_alignment.py -v`
Expected: collection ERROR with `FileNotFoundError` for `docs/dmbok2-citations.json`.

- [ ] **Step 3: Create the empty registry**

Create `docs/dmbok2-citations.json` with exactly this content (a JSON list and a trailing newline):

```json
[]
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_dmbok_alignment.py -v`
Expected: `2 passed, 1 skipped` (the parametrised quote test has no citations yet).

- [ ] **Step 5: Add the ignore rules (D4)**

Append these three lines to the end of `.gitignore` (after `.claude/settings.local.json`):

```text
DAMA-DMBOK-2nd-Edition.md
DAMA-DMBOK-2nd-Edition-assets/
.dmbok-work/
```

Run: `git check-ignore -v DAMA-DMBOK-2nd-Edition.md .dmbok-work/x`
Expected: two lines, each starting `.gitignore:` and naming the matching pattern.

Run: `git status --short`
Expected: `DAMA-DMBOK-2nd-Edition.md` no longer listed as untracked; `.gitignore`, `docs/dmbok2-citations.json`, `tests/…` listed (plus the untracked spec/plan files).

- [ ] **Step 6: Run the whole suite**

Run: `python -m pytest -q`
Expected: `50 passed, 1 skipped`.

- [ ] **Step 7: Commit (only if the owner has authorised commits)**

```bash
git add .gitignore docs/dmbok2-citations.json tests/test_dmbok_alignment.py
git commit -m "test: add DMBOK2 citation registry guardrails; ignore the DMBOK source file"
```

---

### Task 3: Working directory, concept list and reading units (spec Step 0)

**Files (all git-ignored under `.dmbok-work/`):**
- Create: `.dmbok-work/units.json`
- Create: `.dmbok-work/concepts.json`
- Create: `.dmbok-work/check_concepts.py`
- Create: `.dmbok-work/promptlib.py`
- Create dirs: `.dmbok-work/rows`, `.dmbok-work/verify`, `.dmbok-work/prompts`

**Interfaces:**
- Produces:
  - `units.json`: `{"dmbok_file": str, "units": [{"unit": int, "title": str, "chapters": [int], "line_ranges": [[int, int]]}]}`
  - `concepts.json`: list of `{"id": "A-nn", "area": str, "name": str, "description": str, "repo_locations": [{"file": str, "anchor": str}], "units": [int]}`
  - `promptlib.py`: `ROOT`, `WORK`, `DMBOK` (paths); `load_concepts() -> list[dict]`; `load_units() -> list[dict]`; `describe_ranges(unit: dict) -> str`; `concept_block(concepts: list[dict], unit_number: int) -> str`

- [ ] **Step 1: Create the directories and the units file**

Run: `mkdir -p .dmbok-work/rows .dmbok-work/verify .dmbok-work/prompts`

Create `.dmbok-work/units.json` (line ranges are the chapter heading lines of `DAMA-DMBOK-2nd-Edition.md`; each range ends on the line before the next chapter heading):

```json
{
  "dmbok_file": "DAMA-DMBOK-2nd-Edition.md",
  "units": [
    {"unit": 1, "title": "Ethics and security", "chapters": [2, 7], "line_ranges": [[1875, 2324], [6533, 7946]]},
    {"unit": 2, "title": "Data governance, roles and operating models", "chapters": [3], "line_ranges": [[2325, 3213]]},
    {"unit": 3, "title": "Architecture and integration (lineage and mapping)", "chapters": [4, 8], "line_ranges": [[3214, 3877], [7947, 8826]]},
    {"unit": 4, "title": "Reference and master data", "chapters": [10], "line_ranges": [[10008, 10944]]},
    {"unit": 5, "title": "Metadata management (glossary, dictionary, lineage)", "chapters": [12], "line_ranges": [[11867, 12845]]},
    {"unit": 6, "title": "Data quality", "chapters": [13], "line_ranges": [[12846, 14254]]},
    {"unit": 7, "title": "Maturity assessment and organisation roles", "chapters": [15, 16], "line_ranges": [[15147, 16358]]}
  ]
}
```

- [ ] **Step 2: Write the check script (the failing test for this task)**

Create `.dmbok-work/check_concepts.py`:

```python
"""Validate .dmbok-work/concepts.json and units.json against the repo and the DMBOK file."""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".dmbok-work"
DMBOK = Path(os.environ.get("DMBOK_MD", ROOT / "DAMA-DMBOK-2nd-Edition.md"))

concepts = json.loads((WORK / "concepts.json").read_text(encoding="utf-8"))
units = json.loads((WORK / "units.json").read_text(encoding="utf-8"))["units"]
unit_numbers = {u["unit"] for u in units}

problems = []
ids = [c["id"] for c in concepts]
if len(ids) != len(set(ids)):
    problems.append("duplicate concept ids")
for c in concepts:
    if not re.fullmatch(r"A-\d{2}", c["id"]):
        problems.append(f"{c['id']}: bad id")
    if not c["units"] or not set(c["units"]) <= unit_numbers:
        problems.append(f"{c['id']}: units {c['units']} not within {sorted(unit_numbers)}")
    if not c["repo_locations"]:
        problems.append(f"{c['id']}: no repo_locations")
    for loc in c["repo_locations"]:
        path = ROOT / loc["file"]
        if not path.exists():
            problems.append(f"{c['id']}: missing file {loc['file']}")
        elif loc["anchor"].lower() not in path.read_text(encoding="utf-8", errors="ignore").lower():
            problems.append(f"{c['id']}: anchor {loc['anchor']!r} not found in {loc['file']}")
for u in units:
    if not [c for c in concepts if u["unit"] in c["units"]]:
        problems.append(f"unit {u['unit']}: no concepts assigned")

if DMBOK.exists():
    lines = DMBOK.read_text(encoding="utf-8").split("\n")  # not splitlines(): PDF text may contain form feeds
    for u in units:
        for (start, end), chapter in zip(u["line_ranges"], u["chapters"]):
            if not re.search(rf"CHAPTER {chapter}\b", lines[start - 1]):
                problems.append(f"unit {u['unit']}: line {start} is {lines[start - 1][:60]!r}, expected CHAPTER {chapter}")
            if end >= len(lines) or not re.search(r"CHAPTER \d+", lines[end]):
                problems.append(f"unit {u['unit']}: line {end + 1} should start the next chapter")
else:
    print("note: DMBOK file not found, skipping line-range checks")

print(f"{len(concepts)} concepts, {len(units)} units, {len(problems)} problems")
for problem in problems:
    print(" -", problem)
sys.exit(1 if problems else 0)
```

- [ ] **Step 3: Run the check against an empty concept list to verify it fails**

Create `.dmbok-work/concepts.json` containing exactly `[]`, then run: `python .dmbok-work/check_concepts.py`
Expected: exit code 1 and output beginning `0 concepts, 7 units, 7 problems` (one "no concepts assigned" per unit).

- [ ] **Step 4: Write the 32-concept list**

Create `.dmbok-work/concepts.json` (this replaces the empty list; every `anchor` was verified to exist in its file when this plan was written):

```json
[
 {"id":"A-01","area":"Governance","name":"Human decision rights: what AI may do versus what needs human approval","description":"AI proposes, evidence supports, the Data Steward evaluates, the appropriate human owner approves. HANDOFF lists what AI may do and what needs human approval.","repo_locations":[{"file":"HANDOFF.md","anchor":"Human approval required"},{"file":"README.md","anchor":"Human accountability remains explicit"}],"units":[2]},
 {"id":"A-02","area":"Governance","name":"Data Steward role and scope","description":"The target role is a data governance role rather than an operational incident-resolution role.","repo_locations":[{"file":"README.md","anchor":"data governance role rather than an operational incident-resolution role"}],"units":[2,7]},
 {"id":"A-03","area":"Governance","name":"Data Owner and ownership assignment, including ownership gaps","description":"Ownership assignment needs human approval; the Definition & CDE agent surfaces ownership gaps.","repo_locations":[{"file":"HANDOFF.md","anchor":"ownership assignment"},{"file":"contracts/definition-and-cde-agent.contract.json","anchor":"ownership gaps"}],"units":[2,4,7]},
 {"id":"A-04","area":"Governance","name":"Governance bodies, escalation path and the named human governance owner","description":"Escalations route to a named human governance owner who is not yet named (defaults to the project owner); Phase 0b requires roles to be named.","repo_locations":[{"file":"agents/factory/agent-risk-reviewer.md","anchor":"human governance owner"},{"file":"docs/IMPLEMENTATION-SEQUENCE.md","anchor":"Phase 0b"}],"units":[2,7]},
 {"id":"A-05","area":"Governance","name":"Governance policy, standards and policy interpretation","description":"Policy interpretation where material needs human approval; agents must not present inferred policy as fact.","repo_locations":[{"file":"HANDOFF.md","anchor":"policy interpretation where material"}],"units":[2]},
 {"id":"A-06","area":"Governance","name":"Governance reporting and metrics","description":"Governance reporting is in scope for the steward; the success criteria define what the system must demonstrate.","repo_locations":[{"file":"README.md","anchor":"governance reporting"},{"file":"HANDOFF.md","anchor":"Success criteria"}],"units":[2,7]},
 {"id":"A-07","area":"Governance","name":"Continuous improvement of stewardship practice","description":"Continuous improvement is a listed stewardship responsibility.","repo_locations":[{"file":"README.md","anchor":"continuous improvement"}],"units":[2,7]},
 {"id":"A-08","area":"Governance","name":"Stakeholder input: SMEs, Data Owners and operations teams","description":"Agents identify unresolved questions that need SME or Data Owner input.","repo_locations":[{"file":"HANDOFF.md","anchor":"SME or Data Owner input"}],"units":[2,7]},
 {"id":"A-09","area":"Definitions","name":"Business definitions and their approval lifecycle","description":"Agents draft candidate definitions; approving a business definition is a human decision.","repo_locations":[{"file":"HANDOFF.md","anchor":"business definition approval"}],"units":[2,5]},
 {"id":"A-10","area":"Definitions","name":"Business glossary: terms, synonyms and terminology conflicts","description":"Locate and compare existing definitions; identify synonyms, conflicts and missing definitions.","repo_locations":[{"file":"ARCHITECTURE.md","anchor":"identify synonyms"},{"file":"contracts/definition-and-cde-agent.contract.json","anchor":"synonyms"}],"units":[4,5]},
 {"id":"A-11","area":"Definitions","name":"Data dictionary, technical metadata and documentation","description":"Data dictionaries and documentation are listed stewardship responsibilities.","repo_locations":[{"file":"README.md","anchor":"data dictionaries"}],"units":[5]},
 {"id":"A-12","area":"Definitions","name":"Critical data elements: criteria, designation and evidence","description":"CDE designation is a human decision; the agent gathers CDE evidence; no CDE-criteria policy document is named yet.","repo_locations":[{"file":"HANDOFF.md","anchor":"CDE designation"},{"file":"contracts/definition-and-cde-agent.contract.json","anchor":"CDE-criteria"}],"units":[5,6]},
 {"id":"A-13","area":"Definitions","name":"Metadata management: repository, ownership and Stewardship as Code","description":"Governance artefacts held as versioned, machine-readable metadata where that improves traceability.","repo_locations":[{"file":"ARCHITECTURE.md","anchor":"Stewardship as Code"}],"units":[5]},
 {"id":"A-14","area":"Definitions","name":"Provenance and evidence trail for claims","description":"Every material claim separates authoritative internal evidence, general industry context, agent inference, open questions and human decisions.","repo_locations":[{"file":"HANDOFF.md","anchor":"Authoritative internal evidence"},{"file":"schemas/evidence.schema.json","anchor":"authority_level"}],"units":[5]},
 {"id":"A-15","area":"Lineage and mapping","name":"Data lineage and downstream impact","description":"Lineage completeness and downstream impact are examined by the Mapping & Lineage agent.","repo_locations":[{"file":"ARCHITECTURE.md","anchor":"lineage completeness"},{"file":"ARCHITECTURE.md","anchor":"downstream impact"}],"units":[3,5]},
 {"id":"A-16","area":"Lineage and mapping","name":"Source-to-target mappings and transformation semantics","description":"The key question is whether the meaning survived the transformation.","repo_locations":[{"file":"ARCHITECTURE.md","anchor":"Did the meaning survive the transformation"}],"units":[3,5]},
 {"id":"A-17","area":"Lineage and mapping","name":"Data contracts and upstream dependency management","description":"Data contracts and upstream dependency management are listed stewardship responsibilities.","repo_locations":[{"file":"README.md","anchor":"data contracts"},{"file":"README.md","anchor":"upstream dependency management"}],"units":[3,6]},
 {"id":"A-18","area":"Data quality","name":"Data quality dimensions (the taxonomy)","description":"No approved Data-Quality-Dimension taxonomy exists yet (Open Question 5; Phase 0b item 2).","repo_locations":[{"file":"docs/ARCHITECTURE-RISKS.md","anchor":"Data-Quality-Dimension"},{"file":"docs/IMPLEMENTATION-SEQUENCE.md","anchor":"Data-Quality-Dimension"}],"units":[6]},
 {"id":"A-19","area":"Data quality","name":"Quality rules, expectations and candidate controls and tests","description":"Translate approved business expectations into candidate rules, tests and controls.","repo_locations":[{"file":"ARCHITECTURE.md","anchor":"propose quality rule"}],"units":[6]},
 {"id":"A-20","area":"Data quality","name":"Quality thresholds and acceptance of data-quality risk","description":"Quality thresholds and acceptance of data-quality risk are human decisions.","repo_locations":[{"file":"HANDOFF.md","anchor":"quality thresholds"}],"units":[2,6]},
 {"id":"A-21","area":"Data quality","name":"Quality measurement, monitoring and control coverage","description":"Control coverage analysis is a future capability in the backlog.","repo_locations":[{"file":"BUILD-BACKLOG.md","anchor":"control coverage analysis"}],"units":[6]},
 {"id":"A-22","area":"Data quality","name":"Quality issue and exception management","description":"Cluster quality exceptions, recognise recurring characteristics, and route them for human decision.","repo_locations":[{"file":"ARCHITECTURE.md","anchor":"cluster exceptions"}],"units":[6]},
 {"id":"A-23","area":"Data quality","name":"Root-cause analysis and recurring quality patterns","description":"Root-cause hypotheses must be evidence-backed; the final root cause is a human decision where evidence is incomplete.","repo_locations":[{"file":"README.md","anchor":"root-cause analysis"}],"units":[6]},
 {"id":"A-24","area":"Data quality","name":"Fitness for purpose","description":"Data quality is judged as fitness-for-purpose.","repo_locations":[{"file":"README.md","anchor":"fitness-for-purpose"}],"units":[6]},
 {"id":"A-25","area":"Reference and master data","name":"Reference and master data stewardship","description":"The Context agent covers domain content such as transactions, positions, valuation, NAV and reconciliation; no reference or master data stewardship artefact exists.","repo_locations":[{"file":"ARCHITECTURE.md","anchor":"reconciliation"}],"units":[3,4]},
 {"id":"A-26","area":"Reference and master data","name":"Authoritative sources and systems of record","description":"Internal documented position outranks general knowledge; authoritative sources are named per agent.","repo_locations":[{"file":"ARCHITECTURE.md","anchor":"INTERNAL DOCUMENTED POSITION"},{"file":"contracts/definition-and-cde-agent.contract.json","anchor":"authoritative_sources"}],"units":[3,4,5]},
 {"id":"A-27","area":"Architecture","name":"Data architecture knowledge: source platforms and data flows","description":"Relevant source platforms and enterprise data products are part of the Context agent's content areas.","repo_locations":[{"file":"ARCHITECTURE.md","anchor":"relevant source platforms"}],"units":[3]},
 {"id":"A-28","area":"Security and privacy","name":"Data classification, confidentiality and permitted use, including AI processing","description":"No production connectivity or confidential data in the repo; the organisation's data-handling policy is an open question.","repo_locations":[{"file":"docs/REPO-CONVENTIONS.md","anchor":"No production connectivity"}],"units":[1]},
 {"id":"A-29","area":"Ethics","name":"Ethical handling of data and transparency","description":"Systems must not hide uncertainty or present inferred organisational policy as fact.","repo_locations":[{"file":"HANDOFF.md","anchor":"hides uncertainty"}],"units":[1]},
 {"id":"A-30","area":"Compliance","name":"Regulatory and audit traceability","description":"Regulatory reporting is a domain topic and every material conclusion must be traceable to evidence.","repo_locations":[{"file":"ARCHITECTURE.md","anchor":"regulatory reporting"}],"units":[1]},
 {"id":"A-31","area":"Operating model","name":"Stewardship operating model and organisation structure","description":"A single Data Steward supported by a Factory layer and an operational agent team; no business-versus-technical steward structure is defined.","repo_locations":[{"file":"docs/PROPOSED-ARCHITECTURE.md","anchor":"Layer 2"},{"file":"README.md","anchor":"Operational Stewardship Team"}],"units":[7]},
 {"id":"A-32","area":"Maturity","name":"Capability measurement and success criteria","description":"Success criteria define a governed, traceable stewardship capability; no maturity measure is defined.","repo_locations":[{"file":"HANDOFF.md","anchor":"Success criteria"}],"units":[7]}
]
```

- [ ] **Step 5: Run the check to verify it passes**

Run: `python .dmbok-work/check_concepts.py`
Expected: exit code 0 and `32 concepts, 7 units, 0 problems`. If an anchor is reported missing, open the named file, find the nearest exact phrase, and correct the `anchor` (the anchor must be a literal substring, case-insensitive).

- [ ] **Step 6: Write the shared prompt helpers**

Create `.dmbok-work/promptlib.py`:

```python
"""Shared helpers for building reader and verifier prompts (working files live in .dmbok-work/)."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".dmbok-work"
DMBOK = Path(os.environ.get("DMBOK_MD", ROOT / "DAMA-DMBOK-2nd-Edition.md"))


def load_concepts():
    return json.loads((WORK / "concepts.json").read_text(encoding="utf-8"))


def load_units():
    return json.loads((WORK / "units.json").read_text(encoding="utf-8"))["units"]


def describe_ranges(unit):
    pairs, chapters = unit["line_ranges"], unit["chapters"]
    if len(pairs) == len(chapters):
        return "; ".join(f"lines {a}-{b} (Chapter {c})" for (a, b), c in zip(pairs, chapters))
    names = " and ".join(str(c) for c in chapters)
    return "; ".join(f"lines {a}-{b} (Chapters {names})" for a, b in pairs)


def concept_block(concepts, unit_number):
    lines = []
    for c in concepts:
        if unit_number not in c["units"]:
            continue
        where = "; ".join(f'{loc["file"]} ("{loc["anchor"]}")' for loc in c["repo_locations"])
        lines.append(f'- {c["id"]} | {c["area"]} | {c["name"]}\n  Project says: {c["description"]}\n  Repo locations: {where}')
    return "\n".join(lines)
```

Run: `python -c "import sys; sys.path.insert(0, '.dmbok-work'); import promptlib as p; print(p.describe_ranges(p.load_units()[0])); print(p.concept_block(p.load_concepts(), 1)[:200])"`
Expected: first line `lines 1875-2324 (Chapter 2); lines 6533-7946 (Chapter 7)`, then the start of the A-28 block.

- [ ] **Step 7: Confirm nothing tracked changed**

Run: `git status --short`
Expected: no `.dmbok-work` entries (ignored); only the files from Tasks 1–2 plus the untracked spec and plan.

---

### Task 4: Reader prompts and the seven reading units (spec Step 1)

**Files (git-ignored):**
- Create: `.dmbok-work/make_reader_prompts.py`
- Create: `.dmbok-work/check_unit.py`
- Produces: `.dmbok-work/prompts/reader-unit-{1..7}.md`, `.dmbok-work/rows/unit-{1..7}.json`

**Interfaces:**
- Consumes: `promptlib.{DMBOK, WORK, concept_block, describe_ranges, load_concepts, load_units}`; `dmbok_citations.{STATUS_VALUES, ACTION_VALUES, validate_citation, load_pages}` (via `python tests/dmbok_citations.py`).
- Produces `rows/unit-N.json`: `{"unit": int, "citations": [{id, chapter, section, pdf_page, quote}], "rows": [{concept_id, dmbok_terms[str], citation_ids[str], dmbok_position str, caveats[str], proposed_status, status_rationale str, proposed_action, proposal_options[str]}], "additional_content": [{topic, citation_ids[str], why_relevant}], "source_caveats": [str]}`; `check_unit.py rows|verify N` returns exit code 0 when clean.

- [ ] **Step 1: Write the prompt generator**

Create `.dmbok-work/make_reader_prompts.py`:

```python
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
```

- [ ] **Step 2: Generate and sanity-check the prompts**

Run: `python .dmbok-work/make_reader_prompts.py`
Expected: seven `wrote …reader-unit-N.md` lines.

Run: `grep -c "__[A-Z_]*__" .dmbok-work/prompts/reader-unit-1.md .dmbok-work/prompts/reader-unit-7.md`
Expected: `…reader-unit-1.md:0` and `…reader-unit-7.md:0` (no unreplaced tokens). Open `reader-unit-7.md` and confirm it lists concepts A-02, A-03, A-04, A-06, A-07, A-08, A-31, A-32 and the range `lines 15147-16358 (Chapters 15 and 16)`.

- [ ] **Step 3: Write the structural checker for reader and verifier output**

Create `.dmbok-work/check_unit.py`:

```python
"""Structural check of reader or verifier output.

    python .dmbok-work/check_unit.py rows 3      # checks .dmbok-work/rows/unit-3.json
    python .dmbok-work/check_unit.py verify 3    # checks .dmbok-work/verify/unit-3.json
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from dmbok_citations import ACTION_VALUES, STATUS_VALUES  # noqa: E402

WORK = ROOT / ".dmbok-work"
FIT = {"agree", "too_generous", "too_harsh", "unsure"}
SUPPORT = {"yes", "partly", "no"}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def check_rows(n, concepts, unit):
    data = load(WORK / "rows" / f"unit-{n}.json")
    problems = []
    for key in ("unit", "citations", "rows", "additional_content", "source_caveats"):
        if key not in data:
            problems.append(f"missing top-level key {key!r}")
    if problems:
        return problems
    if data["unit"] != n:
        problems.append(f"unit is {data['unit']}, expected {n}")
    assigned = {c["id"] for c in concepts if n in c["units"]}
    got = [r.get("concept_id") for r in data["rows"]]
    if sorted(got) != sorted(assigned):
        problems.append(f"rows cover {sorted(got)}, expected exactly {sorted(assigned)}")
    ids = {c.get("id") for c in data["citations"]}
    for c in data["citations"]:
        if c.get("chapter") not in unit["chapters"]:
            problems.append(f"{c.get('id')}: chapter {c.get('chapter')} not in unit chapters {unit['chapters']}")
    for r in data["rows"]:
        cid = r.get("concept_id")
        for key in ("dmbok_terms", "citation_ids", "dmbok_position", "caveats", "proposed_status",
                    "status_rationale", "proposed_action", "proposal_options"):
            if key not in r:
                problems.append(f"{cid}: missing {key!r}")
        if r.get("proposed_status") not in STATUS_VALUES:
            problems.append(f"{cid}: bad status {r.get('proposed_status')!r}")
        if r.get("proposed_action") not in ACTION_VALUES:
            problems.append(f"{cid}: bad action {r.get('proposed_action')!r}")
        for ref in r.get("citation_ids", []):
            if ref not in ids:
                problems.append(f"{cid}: citation {ref} is not defined in this unit's citations")
        if r.get("proposed_action") != "structural-proposal" and r.get("proposal_options"):
            problems.append(f"{cid}: proposal_options only allowed with structural-proposal")
        if r.get("proposed_status") != "Out of DMBOK scope" and not r.get("citation_ids"):
            problems.append(f"{cid}: needs at least one citation unless Out of DMBOK scope")
    for item in data["additional_content"]:
        for ref in item.get("citation_ids", []):
            if ref not in ids:
                problems.append(f"additional_content {item.get('topic')!r}: unknown citation {ref}")
    return problems


def check_verify(n, rows):
    data = load(WORK / "verify" / f"unit-{n}.json")
    problems = []
    for key in ("unit", "citation_verdicts", "row_verdicts", "missing_findings"):
        if key not in data:
            problems.append(f"missing top-level key {key!r}")
    if problems:
        return problems
    cited = {c["id"] for c in rows["citations"]}
    judged = {v.get("id") for v in data["citation_verdicts"]}
    if cited != judged:
        problems.append(f"citation verdicts cover {sorted(judged)}, expected {sorted(cited)}")
    for v in data["citation_verdicts"]:
        if v.get("supports_claim") not in SUPPORT:
            problems.append(f"{v.get('id')}: bad supports_claim {v.get('supports_claim')!r}")
    concept_ids = {r["concept_id"] for r in rows["rows"]}
    judged_rows = {v.get("concept_id") for v in data["row_verdicts"]}
    if concept_ids != judged_rows:
        problems.append(f"row verdicts cover {sorted(judged_rows)}, expected {sorted(concept_ids)}")
    for v in data["row_verdicts"]:
        if v.get("status_fair") not in FIT:
            problems.append(f"{v.get('concept_id')}: bad status_fair {v.get('status_fair')!r}")
        if v.get("status_fair") in ("too_generous", "too_harsh") and v.get("suggested_status") not in STATUS_VALUES:
            problems.append(f"{v.get('concept_id')}: suggested_status required when the status is not fair")
    return problems


def main(argv):
    if len(argv) != 3 or argv[1] not in ("rows", "verify"):
        print(__doc__)
        return 2
    mode, n = argv[1], int(argv[2])
    concepts = load(WORK / "concepts.json")
    unit = next(u for u in load(WORK / "units.json")["units"] if u["unit"] == n)
    if mode == "rows":
        problems = check_rows(n, concepts, unit)
    else:
        problems = check_verify(n, load(WORK / "rows" / f"unit-{n}.json"))
    for problem in problems:
        print(" -", problem)
    print(f"unit {n} {mode}: {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 4: Dispatch the seven readers**

Use the Agent tool, `subagent_type: general-purpose`, **all seven in one message** so they run concurrently (they are independent). The prompt for unit N is exactly:

```text
Read the file .dmbok-work/prompts/reader-unit-N.md (repository-relative path; your working directory is the repository root) and follow it exactly. The only file you may create is .dmbok-work/rows/unit-N.json. When finished, reply with exactly one line: WROTE .dmbok-work/rows/unit-N.json
```

Replace `N` with 1 to 7. Wait for all seven completion notifications. **Failure mode:** if any reply is a "Token Efficiency Check" card, stop and follow the Global Constraints rule (ask the owner); the inline fallback is to read each prompt file yourself and produce `rows/unit-N.json` sequentially in the main session.

- [ ] **Step 5: Check every unit's output**

For each N in 1..7 run both checks:

```bash
python .dmbok-work/check_unit.py rows N
python tests/dmbok_citations.py .dmbok-work/rows/unit-N.json
```

Expected for a clean unit: `unit N rows: 0 problems` and `<k> citations checked, 0 problems`.

- [ ] **Step 6: Repair any failing unit (repeat until all seven are clean)**

Dispatch a fresh `general-purpose` subagent per failing unit with this prompt (fill in N and paste the checker output):

```text
Your previous output .dmbok-work/rows/unit-N.json failed machine checks. Problems:
<paste the full output of both check commands>
Read .dmbok-work/prompts/reader-unit-N.md again for the rules. Re-open the cited passages in the DMBOK file, correct ONLY the failing citations or rows (leave passing ones unchanged), rewrite .dmbok-work/rows/unit-N.json in full, and reply with exactly one line: WROTE .dmbok-work/rows/unit-N.json
```

Then re-run Step 5 for that unit.

- [ ] **Step 7: Confirm the repo is unchanged**

Run: `git status --short` and `python -m pytest -q`
Expected: no new tracked changes from this task; `50 passed, 1 skipped`.

---

### Task 5: Independent verifiers (spec Step 2)

**Files (git-ignored):**
- Create: `.dmbok-work/make_verifier_prompts.py`
- Produces: `.dmbok-work/prompts/verifier-unit-{1..7}.md`, `.dmbok-work/verify/unit-{1..7}.json`

**Interfaces:**
- Consumes: `rows/unit-N.json` (Task 4 shape), `promptlib.*`, `dmbok_citations.{ALLOWED_ACTIONS}`, `check_unit.py verify N`.
- Produces `verify/unit-N.json`: `{"unit": int, "citation_verdicts": [{"id", "supports_claim": "yes|partly|no", "note"}], "row_verdicts": [{"concept_id", "status_fair": "agree|too_generous|too_harsh|unsure", "suggested_status": str|null, "suggested_action": str|null, "note"}], "missing_findings": [{"concept_id", "pdf_page": int, "note"}]}`.

- [ ] **Step 1: Write the verifier prompt generator**

Create `.dmbok-work/make_verifier_prompts.py`:

```python
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
```

- [ ] **Step 2: Generate and sanity-check**

Run: `python .dmbok-work/make_verifier_prompts.py`
Expected: seven `wrote …verifier-unit-N.md` lines.

Run: `grep -c "__[A-Z_]*__" .dmbok-work/prompts/verifier-unit-3.md`
Expected: `0`.

- [ ] **Step 3: Dispatch the seven verifiers**

Only after **all seven** reader outputs are clean (Task 4 Step 5). Use the Agent tool, `subagent_type: general-purpose`, all seven in one message. The prompt for unit N is exactly:

```text
Read the file .dmbok-work/prompts/verifier-unit-N.md (repository-relative path; your working directory is the repository root) and follow it exactly. You did not write the rows you are checking. The only file you may create is .dmbok-work/verify/unit-N.json. When finished, reply with exactly one line: WROTE .dmbok-work/verify/unit-N.json
```

Use fresh subagents (never the reader of the same unit). Same failure mode as Task 4 Step 4.

- [ ] **Step 4: Check every verifier output**

For each N in 1..7: `python .dmbok-work/check_unit.py verify N`
Expected: `unit N verify: 0 problems`. For a failing unit, dispatch a fresh verifier with the checker output appended, using the same repair pattern as Task 4 Step 6 (file names `verify/unit-N.json`).

- [ ] **Step 5: Read the verifiers' headline findings**

Run: `grep -c '"supports_claim": "no"' .dmbok-work/verify/unit-*.json` and `grep -c '"status_fair": "too_' .dmbok-work/verify/unit-*.json`
Expected: seven counts for each (zeros are possible). Skim any `missing_findings` and any `no` verdict notes: they feed the owner summary in Task 8.

---

### Task 6: Matrix guardrail tests (TDD, written before the document exists)

**Files:**
- Modify: `tests/test_dmbok_alignment.py` (imports at the top; append tests)

**Interfaces:**
- Consumes: `dmbok_citations.{STATUS_VALUES, ACTION_VALUES, ALLOWED_ACTIONS}`; `INDEX` loaded in the test module (Task 2).
- Produces: the contract `docs/DMBOK-ALIGNMENT.md` must satisfy: a `## 2. Conformance matrix` section whose rows start `| A-nn |`, have exactly 8 cells (`ID, Area, Project concept, Where it lives in the repo, DMBOK2 term and citations, Status, Action, Decision owner`), and show every citation as `DMBOK2-Cnn-nn (ch.N §x.y, p.NNN)` matching `docs/dmbok2-citations.json`.

- [ ] **Step 1: Extend the imports**

In `tests/test_dmbok_alignment.py` replace the line

```python
from dmbok_citations import DMBOK_PATH, INDEX_PATH, ROOT, load_pages, validate_citation
```

with

```python
from dmbok_citations import (
    ACTION_VALUES,
    ALLOWED_ACTIONS,
    DMBOK_PATH,
    INDEX_PATH,
    ROOT,
    STATUS_VALUES,
    load_pages,
    validate_citation,
)
```

- [ ] **Step 2: Append the matrix tests**

Append to the end of `tests/test_dmbok_alignment.py`:

```python
ALIGNMENT_DOC = ROOT / "docs" / "DMBOK-ALIGNMENT.md"
REFERENCE = re.compile(r"(DMBOK2-C\d{2}-\d{2}) \(ch\.(\d+) §(\S+), p\.(\d+)\)")


def _matrix_rows():
    assert ALIGNMENT_DOC.exists(), "docs/DMBOK-ALIGNMENT.md has not been created"
    text = ALIGNMENT_DOC.read_text(encoding="utf-8")
    section = re.search(r"^## 2\. Conformance matrix\s*$(.*?)(?=^## )", text, re.M | re.S)
    assert section, "docs/DMBOK-ALIGNMENT.md needs a '## 2. Conformance matrix' section"
    rows = []
    for line in section.group(1).splitlines():
        if re.match(r"^\| A-\d{2} \|", line):
            rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])
    return rows


def test_matrix_has_a_plausible_number_of_rows():
    assert 25 <= len(_matrix_rows()) <= 40


def test_matrix_rows_use_allowed_vocabulary_and_consistent_actions():
    seen = set()
    for cells in _matrix_rows():
        assert len(cells) == 8, f"{cells[0]}: expected 8 cells, got {len(cells)}"
        cid, _area, _concept, _where, dmbok, status, action, owner = cells
        assert cid not in seen, f"{cid} appears twice"
        seen.add(cid)
        assert status in STATUS_VALUES, f"{cid}: bad status {status!r}"
        assert action in ACTION_VALUES, f"{cid}: bad action {action!r}"
        assert action in ALLOWED_ACTIONS[status], f"{cid}: action {action!r} not allowed for status {status!r}"
        assert owner, f"{cid}: decision owner is empty"
        if status != "Out of DMBOK scope":
            assert CITATION_ID.search(dmbok), f"{cid}: status {status} needs at least one DMBOK2 citation id"


def test_matrix_citation_references_match_the_index():
    index = {citation["id"]: citation for citation in INDEX}
    for cells in _matrix_rows():
        cid, dmbok = cells[0], cells[4]
        ids = CITATION_ID.findall(dmbok)
        references = REFERENCE.findall(dmbok)
        assert len(references) == len(ids), f"{cid}: every citation must be shown as 'ID (ch.N §x.y, p.NNN)'"
        for ref_id, chapter, section, page in references:
            assert ref_id in index, f"{cid}: {ref_id} is not in docs/dmbok2-citations.json"
            entry = index[ref_id]
            assert (int(chapter), section, int(page)) == (
                entry["chapter"], entry["section"].split()[0], entry["pdf_page"]
            ), f"{cid}: reference {ref_id} disagrees with the index"
```

- [ ] **Step 3: Run the new tests to verify they fail**

Run: `python -m pytest tests/test_dmbok_alignment.py -v`
Expected: the three matrix tests FAIL with `AssertionError: docs/DMBOK-ALIGNMENT.md has not been created`; the two Task 2 tests still pass; one skip.

- [ ] **Step 4: Commit (only if the owner has authorised commits)**

Leave the failing tests uncommitted until Task 7 makes them pass (do not commit a red suite).

---

### Task 7: Merge, synthesise and render the alignment document (spec Step 3)

**Files:**
- Create (ignored): `.dmbok-work/merge_rows.py`, `.dmbok-work/deviations.json`, `.dmbok-work/draft_proposals.py`, `.dmbok-work/proposals.json`, `.dmbok-work/render_alignment.py`, `.dmbok-work/merged.json` (generated)
- Create: `docs/DMBOK-ALIGNMENT.md`
- Modify: `docs/dmbok2-citations.json` (generated; replaces the empty list)

**Interfaces:**
- Consumes: `rows/unit-N.json` (Task 4 shape), `verify/unit-N.json` (Task 5 shape), `concepts.json`, `dmbok_citations.{ALLOWED_ACTIONS, DEFAULT_ACTION, load_pages, validate_citation}`.
- Produces:
  - `merged.json`: `{"rows": [{concept_id, status, action, dmbok_terms[], citation_ids[], positions[], rationales[], caveats[], proposal_options[], units[]}], "citations": [{id, chapter, section, pdf_page, quote}], "additional_content": [{topic, citation_ids[], why_relevant, unit}], "unverified_concepts": [str], "source_caveats": [str], "stats": {...}}`
  - `proposals.json`: list of `{id "P-nn", concept_id, title, options: [{label, description, citation_ids[]}], recommendation str, decision_owner str, decision "Pending"}`
  - `deviations.json`: list of `{id "DV-nn", deviation, location, rationale, dmbok_position}`
  - `docs/DMBOK-ALIGNMENT.md` satisfying the Task 6 contract; `docs/dmbok2-citations.json` containing exactly the surviving citations.

- [ ] **Step 1: Write the merge script**

Create `.dmbok-work/merge_rows.py`:

```python
"""Merge verified reader output into .dmbok-work/merged.json."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from dmbok_citations import ALLOWED_ACTIONS, DEFAULT_ACTION, load_pages, validate_citation  # noqa: E402

WORK = ROOT / ".dmbok-work"
UNITS = range(1, 8)
STATUS_PRECEDENCE = ["Divergent", "Missing", "Partial", "Aligned", "Out of DMBOK scope"]
ACTION_WEIGHT = ["none", "citation", "wording", "record-deviation", "structural-proposal"]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def merge_status(statuses):
    real = [s for s in statuses if s != "Out of DMBOK scope"]
    return min(real or statuses, key=STATUS_PRECEDENCE.index)


def merge_action(status, actions):
    candidates = [a for a in actions if a in ALLOWED_ACTIONS[status]]
    return max(candidates, key=ACTION_WEIGHT.index) if candidates else DEFAULT_ACTION[status]


def unique(items):
    seen, out = set(), []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def main():
    pages = load_pages()
    survivors, per_concept, additional, caveats = {}, {}, [], []
    stats = {"citations_proposed": 0, "citations_failed_script": 0, "citations_unsupported": 0,
             "rows_read": 0, "rows_agreed": 0, "rows_regraded": 0, "rows_unverified": 0}
    for n in UNITS:
        rows = load(WORK / "rows" / f"unit-{n}.json")
        verdict = load(WORK / "verify" / f"unit-{n}.json")
        support = {v["id"]: v["supports_claim"] for v in verdict["citation_verdicts"]}
        good = {}
        for c in rows["citations"]:
            stats["citations_proposed"] += 1
            if validate_citation(c, pages):
                stats["citations_failed_script"] += 1
            elif support.get(c["id"]) not in ("yes", "partly"):
                stats["citations_unsupported"] += 1
            else:
                good[c["id"]] = {k: c[k] for k in ("id", "chapter", "section", "pdf_page", "quote")}
        survivors.update(good)
        fair = {v["concept_id"]: v for v in verdict["row_verdicts"]}
        for r in rows["rows"]:
            stats["rows_read"] += 1
            v = fair[r["concept_id"]]
            status, action = r["proposed_status"], r["proposed_action"]
            if v["status_fair"] in ("too_generous", "too_harsh"):
                stats["rows_regraded"] += 1
                status = v["suggested_status"]
                action = v.get("suggested_action") or action
            else:
                stats["rows_agreed"] += 1
            ids = [i for i in r["citation_ids"] if i in good]
            if status != "Out of DMBOK scope" and not ids:
                stats["rows_unverified"] += 1
                continue
            per_concept.setdefault(r["concept_id"], []).append({
                "unit": n, "status": status, "action": action, "terms": r["dmbok_terms"],
                "citation_ids": ids, "position": r["dmbok_position"], "rationale": r["status_rationale"],
                "caveats": r["caveats"], "options": r["proposal_options"],
            })
        for item in rows["additional_content"]:
            ids = [i for i in item["citation_ids"] if i in good]
            if ids:
                additional.append({"topic": item["topic"], "citation_ids": ids,
                                   "why_relevant": item["why_relevant"], "unit": n})
        caveats.extend(rows["source_caveats"])
    merged_rows = []
    for cid in sorted(per_concept):
        entries = per_concept[cid]
        status = merge_status([e["status"] for e in entries])
        action = merge_action(status, [e["action"] for e in entries])
        merged_rows.append({
            "concept_id": cid, "status": status, "action": action,
            "dmbok_terms": unique(t for e in entries for t in e["terms"]),
            "citation_ids": unique(i for e in entries for i in e["citation_ids"]),
            "positions": [e["position"] for e in entries],
            "rationales": [e["rationale"] for e in entries],
            "caveats": unique(c for e in entries for c in e["caveats"]),
            "proposal_options": unique(o for e in entries for o in e["options"]),
            "units": [e["unit"] for e in entries],
        })
    all_ids = {c["id"] for c in load(WORK / "concepts.json")}
    stats["concepts_total"] = len(all_ids)
    stats["concepts_with_verified_row"] = len(per_concept)
    result = {
        "rows": merged_rows,
        "citations": [survivors[k] for k in sorted(survivors)],
        "additional_content": additional,
        "unverified_concepts": sorted(all_ids - set(per_concept)),
        "source_caveats": unique(caveats),
        "stats": stats,
    }
    (WORK / "merged.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(stats, indent=2))
    print("concepts without a verified row:", result["unverified_concepts"] or "none")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the merge and resolve gaps**

Run: `python .dmbok-work/merge_rows.py`
Expected: a stats block and `concepts without a verified row: none`.

If concepts are listed, the document cannot be rendered honestly: re-run the owning unit's reader for those concepts (Task 4 Step 6 pattern), re-verify that unit (Task 5 Step 3, Step 4), then re-run this step. Do not proceed with unverified concepts.

- [ ] **Step 3: Record the deviations register**

Create `.dmbok-work/deviations.json` with these four starting entries:

```json
[
 {"id":"DV-01","deviation":"Human-approval model for AI-produced work: AI proposes, evidence supports, the Data Steward evaluates, the appropriate human owner approves; agents never approve, designate, assign ownership or change production.","location":"HANDOFF.md (Decision model, Important non-goals); every agent contract (human_approval_required_for)","rationale":"The DMBOK2 describes human stewards and governance bodies; the project adds controls for a new actor, an AI agent that proposes work for them.","dmbok_position":"No DMBOK2 passage addresses AI agents as actors (2017 text; see Appendix C)."},
 {"id":"DV-02","deviation":"Evidence categories and five confidence labels (Supported, Partially supported, Unsupported, Contradictory, Unable to determine) attached to every material agent claim.","location":"HANDOFF.md (Evidence policy, Confidence policy); schemas/agent-contract.schema.json (confidence_labels); schemas/evidence.schema.json","rationale":"Makes AI-generated claims auditable and keeps internal evidence distinct from general industry context. The DMBOK2 has no equivalent for model output.","dmbok_position":"No DMBOK2 passage addresses confidence labelling of AI output (see Appendix C)."},
 {"id":"DV-03","deviation":"Agent Contracts (responsible_for, not_responsible_for, permitted tools, escalation conditions, evaluation scenarios) as governance artefacts for AI agents.","location":"AGENT-CONTRACT-TEMPLATE.md; contracts/*.contract.json; schemas/agent-contract.schema.json","rationale":"Agents need explicit authority limits that the DMBOK2 defines only for human roles.","dmbok_position":"No DMBOK2 passage addresses authority limits for AI agents (see Appendix C)."},
 {"id":"DV-04","deviation":"Read, Analyse, Recommend operating mode: agents never change production data, mappings or thresholds.","location":"HANDOFF.md (Initial operating mode, Important non-goals)","rationale":"Deliberate risk containment for a new technology; stricter than any DMBOK2 practice, which assumes human operators.","dmbok_position":"No DMBOK2 passage addresses autonomy limits for AI agents (see Appendix C)."}
]
```

Then list the merged rows that need a deviation entry and add one (`DV-05` onward, same four fields) for each not already covered above:

Run: `python -c "import json; m=json.load(open('.dmbok-work/merged.json', encoding='utf-8')); print([r['concept_id'] for r in m['rows'] if r['action']=='record-deviation'])"`

For each listed concept, write `deviation` (what the project does differently), `location` (the repo files from `concepts.json`), `rationale` (from the row's `rationales`), and `dmbok_position` (the row's `positions`, paraphrased, with the citation ID in square brackets when one exists).

- [ ] **Step 4: Draft and complete the proposals**

Create `.dmbok-work/draft_proposals.py`:

```python
"""Create .dmbok-work/proposals.json skeletons from merged rows whose action is structural-proposal."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".dmbok-work"
CITATION_ID = re.compile(r"DMBOK2-C\d{2}-\d{2}")

merged = json.loads((WORK / "merged.json").read_text(encoding="utf-8"))
concepts = {c["id"]: c for c in json.loads((WORK / "concepts.json").read_text(encoding="utf-8"))}
proposals = []
for row in merged["rows"]:
    if row["action"] != "structural-proposal":
        continue
    options = [
        {"label": f"Option {i}", "description": text, "citation_ids": CITATION_ID.findall(text)}
        for i, text in enumerate(row["proposal_options"], start=1)
    ]
    proposals.append({
        "id": f"P-{len(proposals) + 1:02d}",
        "concept_id": row["concept_id"],
        "title": concepts[row["concept_id"]]["name"],
        "options": options,
        "recommendation": "",
        "decision_owner": "Data Steward / project owner",
        "decision": "Pending",
    })
(WORK / "proposals.json").write_text(json.dumps(proposals, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"{len(proposals)} proposal skeletons written; set 'recommendation' on each before rendering")
```

Run: `python .dmbok-work/draft_proposals.py`

Then edit `.dmbok-work/proposals.json` by hand. For **every** proposal: (a) make each option's `description` one clear sentence stating what would be adopted and what it costs; make sure there is at least one option and, where the DMBOK2 offers alternatives, at least two; (b) set `recommendation` to the label of one option followed by a one-sentence reason (for example `Option 2 - smallest change that closes the gap`), or `None - defer` with the reason; (c) leave `decision` as `Pending`. The renderer refuses to run while any `recommendation` is empty.

- [ ] **Step 5: Write the renderer**

Create `.dmbok-work/render_alignment.py`:

```python
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
    out.append("- **Source:** DAMA-DMBOK (2nd Edition), DAMA International, supplied as a PDF-derived text conversion (`DAMA-DMBOK-2nd-Edition.md`, 1,050 PDF pages). The file is kept out of git; only quotes of 25 words or fewer appear in this repository.")
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
```

- [ ] **Step 6: Render the document and the registry**

Run: `python .dmbok-work/render_alignment.py`
Expected: `wrote …DMBOK-ALIGNMENT.md (32 matrix rows) and …dmbok2-citations.json (<n> citations)`. If it exits with `cannot render:`, fix the listed items in `proposals.json` or the working files and re-run.

- [ ] **Step 7: Run the guardrail tests (they now go green)**

Run: `python -m pytest tests/test_dmbok_alignment.py -v`
Expected: all pass: 2 Task 2 tests, 3 matrix tests, and one `test_quote_is_on_the_cited_pdf_page[…]` per indexed citation (none skipped while the DMBOK file is present).

- [ ] **Step 8: Run the whole suite**

Run: `python -m pytest -q`
Expected: `<n> passed` with no failures; the 37 original tests still pass.

- [ ] **Step 9: Spot-check five rows by hand**

Pick five matrix rows at random, including at least one `Divergent` or `Missing` and one `Out of DMBOK scope`. For each cited ID, open `docs/dmbok2-citations.json`, then read the cited PDF page in the DMBOK file (find `<!-- PDF page N -->` with the Grep tool, then Read ~40 lines). Confirm the quote is there and that the row's `Status` is a fair reading. If any row is wrong, fix the working files (`rows/`, `verify/`, `proposals.json`, `deviations.json`), re-run Steps 2 and 6–8.

- [ ] **Step 10: Commit (only if the owner has authorised commits)**

```bash
git add docs/DMBOK-ALIGNMENT.md docs/dmbok2-citations.json tests/test_dmbok_alignment.py
git commit -m "docs: add verified DMBOK2 alignment matrix, deviations, proposals and citation index"
```

---

### Task 8: Owner review gate (spec Step 4) — summarise and STOP

**Files (git-ignored):**
- Create: `.dmbok-work/summarise.py`

**Interfaces:**
- Consumes: `merged.json`, `concepts.json`, `proposals.json`, `deviations.json` (Task 7 shapes).
- Produces: a terminal summary for the owner; no repository changes.

- [ ] **Step 1: Write the summary script**

Create `.dmbok-work/summarise.py`:

```python
"""Print a short summary of the merged alignment for the owner review gate."""
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".dmbok-work"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def load(name):
    return json.loads((WORK / name).read_text(encoding="utf-8"))


merged = load("merged.json")
concepts = {c["id"]: c for c in load("concepts.json")}
proposals = load("proposals.json")
deviations = load("deviations.json")

print("Status counts:", dict(collections.Counter(r["status"] for r in merged["rows"])))
print("Action counts:", dict(collections.Counter(r["action"] for r in merged["rows"])))
print()
print("Gaps (Divergent or Missing):")
for r in merged["rows"]:
    if r["status"] in ("Divergent", "Missing"):
        print(f"  {r['concept_id']} {r['status']:<9} {concepts[r['concept_id']]['name']}")
print()
print(f"{len(proposals)} proposals for approval:")
for p in proposals:
    print(f"  {p['id']} ({p['concept_id']}) {p['title']} -> {p['recommendation']}")
print()
print(f"{len(deviations)} deviations recorded; {len(merged['citations'])} citations indexed.")
print("Verification:", merged["stats"])
```

- [ ] **Step 2: Final verification**

Run: `python -m pytest -q`
Expected: all tests pass (no failures, no unexpected skips while the DMBOK file is present).

Run: `git status --short`
Expected: only the intended files appear (`.gitignore`, `docs/DMBOK-ALIGNMENT.md`, `docs/dmbok2-citations.json`, `tests/dmbok_citations.py`, `tests/test_dmbok_citation_helpers.py`, `tests/test_dmbok_alignment.py`, plus the untracked spec and plan). The DMBOK file and `.dmbok-work/` must not appear.

- [ ] **Step 3: Produce the owner summary**

Run: `python .dmbok-work/summarise.py`

Present to the owner, in plain language: the status and action counts; the Divergent and Missing rows (the real gaps); the list of proposals with their recommendations; the deviations; anything the verifiers flagged (`no` verdicts, regraded rows, `missing_findings`); and the source limits (figures missing, 2017 edition). Link `docs/DMBOK-ALIGNMENT.md`.

- [ ] **Step 4: STOP**

Do **not** edit docs, contracts, schemas, wrappers, evals or the original handoff files, and do not start Tier 1 or Tier 2. Ask the owner to review sections 2–4 of `docs/DMBOK-ALIGNMENT.md` and to decide each proposal (approve, reject or defer). When they have, write the follow-up plan (Tier 1 and Tier 2 edits, pointer notes in the originals, and the vocabulary-consistency test) from the approved matrix.

---

## Handoff to the follow-up plan (not part of this plan)

Inputs the follow-up plan needs from this one: the approved `docs/DMBOK-ALIGNMENT.md` (matrix rows with `Action` of `wording`, `citation`, `structural-proposal` and `record-deviation`; the owner's decision on each proposal), `docs/dmbok2-citations.json`, and the two guardrail modules. Its scope per the spec: Tier 1 wording and citations in `docs/`, contract text (markdown and JSON kept in step), `.claude/agents/` wrappers and `evals/`; Tier 2 structural items the owner approved (each updating schema, contracts and tests together, plus a test that any new vocabulary is identical across schema, contracts and docs); pointer notes and minimal wording in the original handoff files; and a refresh of the README structure tree if new files are added.
