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
