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
