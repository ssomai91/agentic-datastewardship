"""Guards the accepted DMBOK alignment proposals (GD-06) once applied: each entry names the file and the phrases
that must be present, and every DMBOK2 id cited in those files must exist in the citation index."""
import json
import re

import pytest

from schema_registry import ROOT

INDEX = {c["id"] for c in json.loads((ROOT / "docs" / "dmbok2-citations.json").read_text(encoding="utf-8"))}
CITATION_ID = re.compile(r"DMBOK2-C\d{2}-\d{2}")

# (proposal id, file, phrases that must appear)
APPLIED = [
    ('P-01', 'docs/STEWARDSHIP-FRAMEWORK.md', ['## 1. Steward title (P-01', 'neutral title **Data Steward**', 'No steward type']),
    ('P-01-readme', 'README.md', ['neutral title', 'docs/STEWARDSHIP-FRAMEWORK.md']),
    ('P-02', 'docs/STEWARDSHIP-FRAMEWORK.md', ['## 2. Governance owner and escalation (P-02', 'Deputy', 'Executive sponsor', 'no layered escalation']),
    ('P-03', 'docs/STEWARDSHIP-FRAMEWORK.md', ['## 3. Governance metrics (P-03', 'Deferred.', 'system-level criteria only']),
    ('P-04', 'docs/STEWARDSHIP-FRAMEWORK.md', ['## 4. Definition approval lifecycle (P-04', 'DRAFT-NOT-APPROVED', 'GD-05']),
]


@pytest.mark.parametrize("proposal,path,phrases", APPLIED, ids=[a[0] for a in APPLIED])
def test_applied_proposal_is_present_and_cites_real_dmbok_ids(proposal, path, phrases):
    text = (ROOT / path).read_text(encoding="utf-8")
    missing = [p for p in phrases if p not in text]
    assert not missing, f"{proposal}: {path} is missing {missing}"
    unknown = set(CITATION_ID.findall(text)) - INDEX
    assert not unknown, f"{proposal}: {path} cites ids not in the citation index: {sorted(unknown)}"
