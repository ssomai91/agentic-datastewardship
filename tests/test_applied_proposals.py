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
    ('P-05', 'docs/CDE-CRITERIA-POLICY.md', ['## 4. Criticality drivers', 'Master Data is treated as critical by definition', 'never designate a CDE', '## 7. Implementation']),
    ('P-06', 'docs/STEWARDSHIP-FRAMEWORK.md', ['## 5. Metadata: hybrid model (P-06', 'steward-added governance metadata only', '`<system>:<identifier>`']),
    ('P-07', 'docs/DATA-QUALITY-FRAMEWORK.md', ['Taxonomy version 0.1', 'Completeness', 'Consistency', 'Characteristics outside the six', 'GD-04']),
    ('P-08', 'docs/DATA-QUALITY-FRAMEWORK.md', ['## 2. Candidate rule pre-approval checklist (P-08', 'Confirmed by a subject-matter expert', 'UNRESOLVED - pending human definition']),
    ('P-09', 'docs/DATA-QUALITY-FRAMEWORK.md', ['## 3. Quality coverage (P-09', 'Coverage is defined as a matrix', 'only when both a rule and a threshold have human approval']),
    ('P-10', 'docs/DATA-QUALITY-FRAMEWORK.md', ['## 4. Minimum quality issue record (P-10', '`decision_owner`', 'never records a decision']),
]


@pytest.mark.parametrize("proposal,path,phrases", APPLIED, ids=[a[0] for a in APPLIED])
def test_applied_proposal_is_present_and_cites_real_dmbok_ids(proposal, path, phrases):
    text = (ROOT / path).read_text(encoding="utf-8")
    missing = [p for p in phrases if p not in text]
    assert not missing, f"{proposal}: {path} is missing {missing}"
    unknown = set(CITATION_ID.findall(text)) - INDEX
    assert not unknown, f"{proposal}: {path} cites ids not in the citation index: {sorted(unknown)}"
