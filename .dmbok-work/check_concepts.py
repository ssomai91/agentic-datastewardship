"""Validate .dmbok-work/concepts.json and units.json against the repo and the DMBOK file."""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".dmbok-work"
DMBOK = Path(os.environ.get("DMBOK_MD", ROOT / "DAMA-DMBOK-Summary.md"))

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
