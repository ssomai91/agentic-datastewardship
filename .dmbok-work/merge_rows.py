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
