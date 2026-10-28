"""Manifest checks that are deterministic inputs to the gate (Required Inputs, 'Packet manifest' row; Process steps 1 and 3).

stop_conditions: the COMPLETE list of step 3 stop conditions, from the manifest row. A sampling_rule_ref is deliberately not one.
missing_inputs: required inputs and deterministic results that are absent (step 9 rank 3).
coverage_state: the Coverage entry row, with DC-7 deferred.
"""
REQUIRED_FIELDS = ("case_id", "pack_id", "request", "produced_by", "authored_by", "assembled_by", "manifest_approved_by",
                   "evidence_store_run_id", "evidence_store_query", "uncited_evidence_ids", "provenance", "validator_run_id",
                   "approval_log_run_id", "items")
REVIEWER_NAME = "Assurance Reviewer"


def stop_conditions(manifest, readable=True):
    stops = set()
    if not readable or not isinstance(manifest, dict):
        return {"packet or manifest unreadable"}
    for f in REQUIRED_FIELDS:
        # An absent field is a stop. validator_run_id and approval_log_run_id are declarations that may be null:
        # a null there is a missing deterministic result (rank 3), not an absent field, so they are checked by missing_inputs.
        if f not in manifest:
            stops.add(f"manifest field absent: {f}")
    if "request" in manifest and not str(manifest["request"]).strip():
        stops.add("original request is empty")
    if manifest.get("provenance") != "synthetic":
        stops.add(f"provenance is {manifest.get('provenance', 'absent')}")
    for role in ("assembled_by", "manifest_approved_by"):
        v = manifest.get(role)
        if role in manifest and (not v or v in (manifest.get("produced_by"), manifest.get("authored_by"))):
            stops.add(f"{role} is absent or not independent of the producer or author")
    if REVIEWER_NAME in (manifest.get("produced_by"), manifest.get("authored_by")):
        stops.add("the Assurance Reviewer is named as producer or author")
    return stops


def missing_inputs(manifest, items):
    paths = {i["path"] for i in manifest.get("items", [])}
    missing = set()
    if not manifest.get("validator_run_id") or "checks/validator-report.json" not in paths:
        missing.add("validator and boundary report")
    if not manifest.get("approval_log_run_id") or "checks/approval-log-extract.json" not in paths:
        missing.add("approval-log extract")
    for sid in manifest.get("uncited_evidence_ids", []):
        if f"evidence/{sid}.json" not in paths:
            missing.add(f"uncited record {sid} listed but not in the packet")
    return missing


def coverage_state(manifest):
    """Coverage entry with DC-7 deferred: 'full' is the only usable value. A sampling_rule_ref cannot be verified (rank 3, not a stop)."""
    if "coverage" not in manifest:
        return "absent"
    if manifest.get("sampling_rule_ref"):
        return "unverifiable_sampling_ref"
    return "full" if manifest["coverage"] == "full" else "outside_approved_rule"