"""Validate a Claude Agent Builder output's coverage trace against the approved contract.

    python tools/validate_coverage_trace.py BUILDER_OUTPUT.json CONTRACT.json

Checks (exit code 1 on any problem):
  1. every contract field is accounted for exactly once: traced in coverage_trace or listed in uncovered_fields;
  2. neither list names a field the contract does not have (a Builder cannot invent or widen scope);
  3. every generated file is under prompts/ and cannot touch agents/operational/ or contracts/;
  4. when the generated files exist, every cited prompt_passage really occurs in one of them.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PREFIXES = ("agents/operational/", "contracts/")


def _norm(text):
    return re.sub(r"\s+", " ", text).strip().lower()


def contract_fields(contract_schema):
    return list(contract_schema["required"])


def coverage_trace_problems(output, contract, contract_schema, files=None):
    """Return a list of problems. files maps a generated path to its text (None skips check 4)."""
    problems = []
    fields = set(contract_fields(contract_schema))
    present = set(contract) & fields
    traced = [t["contract_field"] for t in output.get("coverage_trace", [])]
    uncovered = list(output.get("uncovered_fields", []))

    for name in sorted(set(traced) | set(uncovered)):
        if name not in contract:
            problems.append(f"'{name}' is not a field of the approved contract")
    for name in sorted(set(traced) & set(uncovered)):
        problems.append(f"'{name}' is both traced and listed as uncovered")
    for name in sorted({n for n in traced if traced.count(n) > 1}):
        problems.append(f"'{name}' is traced more than once")
    for name in sorted(present - set(traced) - set(uncovered)):
        problems.append(f"contract field '{name}' is neither traced nor listed as uncovered")

    for path in output.get("generated_files", []):
        norm = path.replace("\\", "/")
        if not norm.startswith("prompts/") or ".." in norm.split("/"):
            problems.append(f"generated file '{path}' is outside prompts/")
        if norm.startswith(FORBIDDEN_PREFIXES):
            problems.append(f"generated file '{path}' touches a protected location")

    if files is not None:
        haystack = {p: _norm(t) for p, t in files.items()}
        for entry in output.get("coverage_trace", []):
            passage = _norm(entry["prompt_passage"])
            if not any(passage in text for text in haystack.values()):
                problems.append(f"passage for '{entry['contract_field']}' does not occur in any generated file")
    return problems


def main(argv):
    if len(argv) != 3:
        sys.exit(__doc__)
    output = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    contract = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "schemas" / "agent-contract.schema.json").read_text(encoding="utf-8"))
    files = {}
    for path in output.get("generated_files", []):
        target = ROOT / path
        if target.is_file():
            files[path] = target.read_text(encoding="utf-8")
    found = coverage_trace_problems(output, contract, schema, files if len(files) == len(output.get("generated_files", [])) else None)
    for line in found:
        print("PROBLEM:", line)
    print(f"{len(found)} problems")
    sys.exit(1 if found else 0)


if __name__ == "__main__":
    main(sys.argv)