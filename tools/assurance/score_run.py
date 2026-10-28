"""Score recorded Assurance Reviewer outputs against the FROZEN expectations and through the recorder (DC-8).

    python tools/assurance/score_run.py [outputs_dir]      # default evals/assurance-runs/pass1

Two separate questions per packet: (1) do the agent's gate, status and rank match EXPECTED.json; (2) does the recorder accept the output.
A mismatch is reported, not judged: read the findings before calling the agent wrong.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from assurance import run_slice  # noqa: E402
from assurance.recorder import check_output  # noqa: E402

EXPECTED = ROOT / "evals" / "assurance-runs" / "EXPECTED.json"


def score_one(pid, packet, output, expected):
    report = json.loads(packet.items["checks/validator-report.json"])
    extract = json.loads(packet.items["checks/approval-log-extract.json"]) if "checks/approval-log-extract.json" in packet.items else None
    verdict = check_output(output, packet, report, extract)
    got = {"gate": output.get("gate_recommendation"), "status": output.get("handoff", {}).get("status")}
    assess = {rc["source_claim_id"]: rc["producer_claim_assessment"] for rc in output.get("reviewed_claims", [])}
    types = [f["finding_type"] for f in output.get("findings", [])]
    matches = {"gate": got["gate"] == expected["expected_gate"], "status": got["status"] == expected["expected_status"]}
    for cid, want in expected.get("expected_claim_assessment", {}).items():
        matches[f"assessment {cid}"] = assess.get(cid) == want
    for t in expected.get("expected_finding_types_include", []):
        matches[f"finding type {t}"] = t in types
    if expected["expected_rank"] == 1:
        matches["no claims reviewed (rank 1)"] = not output.get("reviewed_claims")
    return {"id": pid, "expected": (expected["expected_gate"], expected["expected_status"]), "got": (got["gate"], got["status"]), "matches": matches,
            "recorder_accepted": verdict.accepted, "problems": verdict.problems, "assessments": assess, "finding_types": types}


def main(outputs_dir=None):
    outputs_dir = Path(outputs_dir) if outputs_dir else ROOT / "evals" / "assurance-runs" / "pass1"
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))["packets"]
    packets = run_slice.packets()
    rows = []
    for pid in sorted(expected):
        f = outputs_dir / f"{pid}.output.json"
        if not f.is_file():
            rows.append({"id": pid, "missing": True})
            continue
        try:
            output = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            rows.append({"id": pid, "unparseable": str(e)})
            continue
        rows.append(score_one(pid, packets[pid], output, expected[pid]))
    return rows


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    rows = main(sys.argv[1] if len(sys.argv) > 1 else None)
    for r in rows:
        if r.get("missing") or r.get("unparseable"):
            print(r["id"], "MISSING" if r.get("missing") else "UNPARSEABLE " + r["unparseable"][:80])
            continue
        ok = all(r["matches"].values())
        print(f"{r['id']}  expected {r['expected']}  got {r['got']}  match={'YES' if ok else 'NO'}  recorder={'ACCEPTED' if r['recorder_accepted'] else 'REJECTED'}")
        for k, v in r["matches"].items():
            if not v:
                print(f"     mismatch: {k}")
        print(f"     assessments={r['assessments']} finding_types={r['finding_types']}")
        for p in r["problems"][:6]:
            print(f"     problem: {p[:230]}")
    n = sum(1 for r in rows if r.get("matches") and all(r["matches"].values()))
    a = sum(1 for r in rows if r.get("recorder_accepted"))
    print(f"\nmatch frozen expectations: {n}/{len(rows)} | recorder accepted: {a}/{len(rows)}")