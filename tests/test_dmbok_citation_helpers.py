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
