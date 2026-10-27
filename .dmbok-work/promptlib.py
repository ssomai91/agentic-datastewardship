"""Shared helpers for building reader and verifier prompts (working files live in .dmbok-work/)."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".dmbok-work"
DMBOK = Path(os.environ.get("DMBOK_MD", ROOT / "DAMA-DMBOK-SUMMARY.md"))


def load_concepts():
    return json.loads((WORK / "concepts.json").read_text(encoding="utf-8"))


def load_units():
    return json.loads((WORK / "units.json").read_text(encoding="utf-8"))["units"]


def describe_ranges(unit):
    pairs, chapters = unit["line_ranges"], unit["chapters"]
    if len(pairs) == len(chapters):
        return "; ".join(f"lines {a}-{b} (Chapter {c})" for (a, b), c in zip(pairs, chapters))
    names = " and ".join(str(c) for c in chapters)
    return "; ".join(f"lines {a}-{b} (Chapters {names})" for a, b in pairs)


def concept_block(concepts, unit_number):
    lines = []
    for c in concepts:
        if unit_number not in c["units"]:
            continue
        where = "; ".join(f'{loc["file"]} ("{loc["anchor"]}")' for loc in c["repo_locations"])
        lines.append(f'- {c["id"]} | {c["area"]} | {c["name"]}\n  Project says: {c["description"]}\n  Repo locations: {where}')
    return "\n".join(lines)
