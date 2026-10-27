"""Cross-reference checks that JSON Schema cannot express."""


def handoff_reference_problems(handoff):
    """Return a list of problems: duplicate ids and claims that cite evidence not in the handoff."""
    problems = []
    source_ids = [e["source_id"] for e in handoff.get("evidence", [])]
    if len(source_ids) != len(set(source_ids)):
        problems.append("duplicate evidence source_id")
    claim_ids = [c["claim_id"] for c in handoff.get("claims", [])]
    if len(claim_ids) != len(set(claim_ids)):
        problems.append("duplicate claim_id")
    known = set(source_ids)
    for claim in handoff.get("claims", []):
        for evidence_id in claim["evidence_ids"]:
            if evidence_id not in known:
                problems.append(f"{claim['claim_id']} cites unknown evidence {evidence_id}")
    return problems