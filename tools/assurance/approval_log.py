"""DC-4 approval-log lookup (stand-in over a synthetic fixture).

Contract: returns the approval-log extract, including an explicit empty result, with approver role and date. An absent extract is a
different state from an empty one (absent: rank 3; present but empty: a missing approval if the pack relies on one).
"""
import hashlib
import json
from pathlib import Path


def lookup(log_path, data_elements):
    log = json.loads(Path(log_path).read_text(encoding="utf-8"))
    wanted = {d.lower() for d in data_elements}
    entries = [e for e in log["entries"] if e["data_element"] in wanted]
    digest = hashlib.sha256(json.dumps([sorted(wanted), entries], sort_keys=True).encode("utf-8")).hexdigest()[:12]
    return {"run_id": f"SYN-APPR-{digest}", "data_elements": sorted(wanted), "entries": entries, "empty": not entries}


def approved_by(extract, subject):
    """True only for an entry whose action is exactly 'approved' for the subject ('reviewed' is not approval)."""
    return any(e["subject"] == subject and e["action"] == "approved" for e in extract["entries"])