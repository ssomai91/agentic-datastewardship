"""DC-3 deterministic validator and boundary checker (stand-in).

Runs the checks the contract lists: schema, duplicate and unresolved evidence ids (extending tools/handoff_checks.py), and the tools the
producer used versus the producer contract's permitted tools. Produces a report with a run id. Each check is pass, fail or absent;
'absent' means the input needed to run it was not supplied (for example no tool-call log), which the reviewer must treat as Unable to determine.
"""
import hashlib
import json

from handoff_checks import handoff_reference_problems
from schema_support import validator_for

WRITE_PREFIXES = ("create", "update", "delete", "set", "publish", "approve", "change", "assign", "link")


def _check(name, result, detail):
    return {"check": name, "result": result, "detail": detail}


def validate(output, output_schema_path, permitted_tools, tool_calls=None):
    schema_errors = [f"{list(e.absolute_path)}: {e.message[:120]}" for e in validator_for(output_schema_path).iter_errors(output)]
    ref_problems = handoff_reference_problems(output.get("handoff", {})) if isinstance(output.get("handoff"), dict) else ["no handoff object"]
    checks = [
        _check("output_schema", "fail" if schema_errors else "pass", "; ".join(schema_errors[:5])),
        _check("duplicate_and_unresolved_evidence_ids", "fail" if ref_problems else "pass", "; ".join(ref_problems)),
    ]
    if tool_calls is None:
        checks.append(_check("boundary", "absent", "no tool-call log supplied"))
    else:
        outside = sorted({c["tool"] for c in tool_calls if c["tool"] not in permitted_tools})
        writes = [c["tool"] for c in tool_calls if c.get("write_attempt") or c["tool"].startswith(WRITE_PREFIXES)]
        problems = [f"tool not permitted: {t}" for t in outside] + [f"write attempt: {t}" for t in writes]
        checks.append(_check("boundary", "fail" if problems else "pass", "; ".join(problems)))
    digest = hashlib.sha256(json.dumps([output, [c["result"] for c in checks]], sort_keys=True, default=str).encode("utf-8")).hexdigest()[:12]
    return {"run_id": f"SYN-VAL-{digest}", "checks": checks}


def result_of(report, check):
    for c in report["checks"]:
        if c["check"] == check:
            return c["result"]
    return "absent"