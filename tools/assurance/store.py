"""STAND-IN case evidence store (the contract does not choose one; see DC-1 and the case-store open question).

Built from the synthetic glossary fixture: each glossary term becomes an evidence record keyed to a data element (the term's name).
It exists only so DC-1 can be exercised. It is not a decision about where real evidence lives.
"""
import hashlib
import json
import re
from pathlib import Path

TIMESTAMP = "2026-10-28T00:00:00Z"


def element_key(name):
    """Mechanical key match: the term name lower-cased, parenthetical qualifier removed."""
    return re.sub(r"\s*\(.*?\)\s*", "", name).strip().lower()


class CaseStore:
    def __init__(self, records, synthetic):
        self._records = {r["source_id"]: r for r in records}
        self.synthetic = synthetic  # True, False, or None when the store does not say (provenance then reads "missing")

    @classmethod
    def from_glossary(cls, path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        records = []
        for t in data["terms"]:
            records.append({
                "source_id": t["term_id"], "source_type": "glossary_term", "title": t["term"],
                "location": f"{data['glossary_id']}/{t['term_id']}", "authority_level": "authoritative_internal",
                "extracted_fact": t["definition"], "direct_or_inferred": "direct", "timestamp": TIMESTAMP,
                "data_element": element_key(t["term"]),
            })
        synthetic = True if "SYNTHETIC" in data.get("_note", "") else None
        return cls(records, synthetic)

    def get(self, source_id):
        return self._records.get(source_id)

    def by_data_element(self, key):
        return [r for r in self._records.values() if r["data_element"] == key]

    def run_id(self, query):
        digest = hashlib.sha256(json.dumps([sorted(self._records), query], sort_keys=True).encode("utf-8")).hexdigest()[:12]
        return f"STORE-RUN-{digest}"