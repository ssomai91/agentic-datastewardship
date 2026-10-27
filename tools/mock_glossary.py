"""Mocked read-only glossary interface for the Definition & CDE evaluation harness.

It exposes exactly the five read-only capabilities in the agent contract's Permitted Tools table, over
synthetic data. Any create/update/delete/set/publish call is refused and logged, so the harness can
prove an agent never attempts a write. Real tool identifiers are pending glossary system selection
(see docs/GLOSSARY-TOOL-MAPPING.md).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = ROOT / "fixtures" / "definition-and-cde" / "glossary.json"

# contract capability -> method name
CAPABILITIES = {
    "Search glossary terms": "search_terms",
    "Get glossary term detail": "get_term",
    "Get glossary categories": "get_categories",
    "Get glossary term links": "get_term_links",
    "Bulk glossary export": "bulk_export",
}
WRITE_PREFIXES = ("create", "update", "delete", "set", "publish", "approve", "change", "assign", "link")


class GlossaryToolError(RuntimeError):
    """The simulated glossary tool failed (error or timeout)."""


class ReadOnlyViolation(PermissionError):
    """An agent attempted a write on a read-only glossary."""


class MockGlossary:
    def __init__(self, data=None, fail_on=()):
        self._data = data if data is not None else json.loads(DEFAULT_FIXTURE.read_text(encoding="utf-8"))
        self._fail_on = set(fail_on)
        self.calls = []

    def _record(self, tool, **args):
        self.calls.append({"tool": tool, "args": args})
        if tool in self._fail_on:
            raise GlossaryToolError(f"{tool}: simulated tool failure (timeout)")

    def search_terms(self, query):
        self._record("search_terms", query=query)
        needle = query.lower()
        return [t for t in self._data["terms"] if needle in t["term"].lower() or needle in t["definition"].lower()]

    def get_term(self, term_id):
        self._record("get_term", term_id=term_id)
        for term in self._data["terms"]:
            if term["term_id"] == term_id:
                return dict(term)
        return None

    def get_categories(self):
        self._record("get_categories")
        return list(self._data["categories"])

    def get_term_links(self, term_id):
        self._record("get_term_links", term_id=term_id)
        return [l for l in self._data["term_links"] if term_id in (l["from"], l["to"])]

    def bulk_export(self):
        self._record("bulk_export")
        return json.loads(json.dumps(self._data["terms"]))

    def __getattr__(self, name):
        if name.startswith(WRITE_PREFIXES):
            def refuse(*args, **kwargs):
                self.calls.append({"tool": name, "args": kwargs, "write_attempt": True})
                raise ReadOnlyViolation(f"{name}: the glossary is read-only for this agent")
            return refuse
        raise AttributeError(name)

    @property
    def write_attempts(self):
        return [c for c in self.calls if c.get("write_attempt")]
