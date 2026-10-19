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
