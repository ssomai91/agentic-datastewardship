import json
import re

import pytest

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
