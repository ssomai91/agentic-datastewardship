"""DC-8 status recorder and output checker (stand-in), contract Process step 11, checks (a) to (g).

Deterministic and bounded. It rejects an output that differs from what the contract's rules compute; where the contract is silent
(the summary template, the schema-required free strings, the form of the rank 1 stop record, the approval_check field) it WARNS
instead of rejecting, and each warning names the open point, so this code does not become a second, unreviewed source of truth.

Not implemented, and stated so: authentication of the human channel; DC-5 request state; DC-7 register. The 'authenticated role'
passed to record_human_resolution is supplied by the caller and proves nothing.
"""
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from assurance.gate import GateInputs, derive, is_blocking
from assurance.manifest import coverage_state, missing_inputs, stop_conditions
from assurance.validator import result_of
from handoff_checks import handoff_reference_problems
from schema_support import SCHEMAS, validator_for

OUTPUT_SCHEMA = SCHEMAS / "outputs" / "assurance-reviewer.output.schema.json"
OWN_PREFIX = "AR-EV-"
ABSENT_SENTENCE = re.compile(r"^no entry matching (?P<key>.+) in extract (?P<run>\S+)$")
GATE_NOTE_PHRASES = ("recommendation only", "not a clearance")
RESOLVING_ROLE = "Project Owner"  # GD-01; whether the deputy may resolve is an open assumption and is NOT allowed here


@dataclass
class Verdict:
    accepted: bool
    problems: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    expected: object = None


def _location_text(packet, location):
    """Location form: <item path>[@<version>][#<field path or line>]. Returns (item text or None, problem or None)."""
    path = location.split("#", 1)[0]
    version = None
    if "@" in path:
        path, version = path.split("@", 1)
    versions = {i["path"]: i["version"] for i in packet.manifest["items"]}
    if path not in packet.items or path not in versions:
        return None, f"location names an item that is not in the packet: {path}"
    if version is not None and version != versions[path]:
        return None, f"location version {version} differs from the manifest version {versions[path]} for {path}"
    return packet.items[path], None


def derive_expected(output, packet, validator_report, resolutions=None):
    manifest = packet.manifest
    stops = stop_conditions(manifest)
    missing = set(missing_inputs(manifest, packet.items))
    if validator_report is not None and result_of(validator_report, "boundary") == "absent":
        missing.add("boundary check result")
    rank1 = bool(stops)
    assessments = () if rank1 else tuple(rc["producer_claim_assessment"] for rc in output.get("reviewed_claims", []))
    ftypes = () if rank1 else tuple(f["finding_type"] for f in output.get("findings", []))
    return derive(GateInputs(frozenset(stops), assessments, ftypes, frozenset(missing), coverage_state(manifest)), resolutions)


def check_output(output, packet, validator_report, approval_extract, resolutions=None):
    problems, warnings = [], []
    manifest = packet.manifest
    pack = json.loads(packet.items["pack/producer-output.json"])
    pack_claim_ids = [c["claim_id"] for c in pack.get("handoff", {}).get("claims", [])]

    # (e) structure: the output schema enforces identifiers, enums and the closed forms
    for e in validator_for(OUTPUT_SCHEMA).iter_errors(output):
        problems.append(f"(e) schema: {list(e.absolute_path)}: {e.message[:140]}")
    if problems:
        return Verdict(False, problems, warnings, None)

    exp = derive_expected(output, packet, validator_report, resolutions)

    # (a) gate, own gate claim, status, blocking flags, counts, boundary echo
    if output["gate_recommendation"] != exp.value:
        problems.append(f"(a) gate {output['gate_recommendation']} differs from the step 9 value {exp.value} ({', '.join(exp.reasons)})")
    gate_claims = [c for c in output["handoff"]["claims"] if c["claim_id"] == "AR-C-GATE"]
    if len(gate_claims) != 1 or not gate_claims[0]["statement"].startswith(f"Gate {exp.value}"):
        problems.append("(a) the own claim AR-C-GATE is missing, repeated or states a different gate")
    if output["handoff"]["status"] != exp.handoff_status:
        problems.append(f"(a) handoff.status {output['handoff']['status']} differs from the status table value {exp.handoff_status}")
    assess = {rc["source_claim_id"]: rc["producer_claim_assessment"] for rc in output["reviewed_claims"]}
    for f in output["findings"]:
        want = is_blocking(assessment=assess.get(f["source_claim_id"]), finding_type=f["finding_type"])
        if f["blocking"] != want:
            problems.append(f"(a) finding {f['finding_id']} blocking={f['blocking']} but the step 9 rank 2 test gives {want}")
    cov = output["coverage"]
    if cov["claims_in_pack"] != len(pack_claim_ids) or cov["claims_reviewed"] != len(output["reviewed_claims"]):
        problems.append("(a) coverage counts do not match the pack and the reviewed claims")
    want_boundary = {"pass": "consistent", "fail": "breach", "absent": "unable_to_determine"}[result_of(validator_report or {"checks": []}, "boundary")]
    if output["boundary_check"] != want_boundary:
        problems.append(f"(a) boundary_check {output['boundary_check']} differs from the validator report ({want_boundary})")
    if exp.rank == 1 and (output["findings"] or output["reviewed_claims"]):
        warnings.append("(a) rank 1: the contract says no finding other than the stop record, but the form of the stop record is not specified (eval open point); content findings are not rejected here")
    warnings.append("(a) approval_check is not cross-checked: the contract does not say how a claim maps to an approval-log entry")

    # (b) reviewed claim set equals the pack's claim set (empty at rank 1)
    reviewed = [rc["source_claim_id"] for rc in output["reviewed_claims"]]
    if exp.rank == 1:
        if reviewed:
            problems.append("(b) rank 1 is a stop: reviewed_claims must be empty")
    elif sorted(reviewed) != sorted(pack_claim_ids) or len(reviewed) != len(set(reviewed)):
        problems.append(f"(b) reviewed_claims {sorted(reviewed)} do not equal the pack's claim ids {sorted(pack_claim_ids)}")

    # (c) duplicate and unresolved ids in the agent's own output
    problems += [f"(c) {p}" for p in handoff_reference_problems(output["handoff"])]
    ids = [f["finding_id"] for f in output["findings"]]
    if len(ids) != len(set(ids)):
        problems.append("(c) duplicate finding_id")
    prefix = f"AR-{manifest['case_id']}-{manifest['pack_id']}-"
    problems += [f"(c) finding id {i} does not carry the prefix {prefix}" for i in ids if not i.startswith(prefix)]
    paths = {i["path"] for i in manifest["items"]}
    collisions = [p for p in paths if p.startswith("evidence/") and Path(p).stem.startswith(OWN_PREFIX)]
    if collisions and not any(f["finding_type"] == "source_id_collision" for f in output["findings"]):
        problems.append("(c) a producer record carries the reviewer's reserved prefix AR-EV- but no source_id_collision finding was raised")

    # (d) quotations are verbatim at their stated location; absence records re-run the lookup
    for f in output["findings"]:
        if f["quoted_excerpt"] is not None:
            texts = [_location_text(packet, loc) for loc in f["locations"]]
            if not any(t is not None and f["quoted_excerpt"] in t for t, _ in texts):
                problems.append(f"(d) quoted_excerpt of {f['finding_id']} does not occur verbatim at any of its locations")
    for rec in output["handoff"]["evidence"]:
        sid = rec["source_id"]
        if sid.startswith(OWN_PREFIX + "ABSENT-"):
            m = ABSENT_SENTENCE.match(rec["extracted_fact"])
            if not m:
                problems.append(f"(d) {sid}: the fixed sentence 'no entry matching <key> in extract <run id>' was not used")
            elif approval_extract is None or m.group("run") != approval_extract["run_id"]:
                problems.append(f"(d) {sid}: names an extract run id that was not supplied")
            else:
                key = m.group("key").lower()
                if any(key in (e["data_element"], e["subject"].lower()) for e in approval_extract["entries"]):
                    problems.append(f"(d) {sid}: the lookup re-run finds an entry matching {m.group('key')}")
        elif sid.startswith(OWN_PREFIX):
            text, why = _location_text(packet, rec["location"])
            if why:
                problems.append(f"(d) {sid}: {why}")
            elif rec["extracted_fact"] not in text:
                problems.append(f"(d) {sid}: extracted_fact does not occur verbatim at its location")
        else:
            item = packet.items.get(f"evidence/{sid}.json")
            if item is None:
                problems.append(f"(d) producer record {sid} is not in the packet")
            elif json.loads(item)["extracted_fact"] != rec["extracted_fact"]:
                problems.append(f"(d) producer record {sid} was altered: its extracted_fact differs from the packet copy")

    # (e) free strings: quoted assumptions must be verbatim; the rest the contract does not pin down is a warning
    pack_text = "\n".join(packet.items.values())
    for a in list(output["assumptions"]) + [x for rc in output["reviewed_claims"] for x in rc["assumption_excerpts"]]:
        if a not in pack_text:
            problems.append("(e) an assumption excerpt is not a verbatim quotation of the packet")
    if not re.match(r"^Gate (HOLD_RECOMMENDED|NO_BLOCKING_FINDINGS_IDENTIFIED|INCOMPLETE)\b", output["summary"]):
        warnings.append("(e) summary does not start with the gate value; the contract's fixed template is not specified (open point)")
    if not all(p in output["gate_recommendation_note"].lower() for p in GATE_NOTE_PHRASES):
        problems.append("(e) gate_recommendation_note does not carry the fixed text (recommendation only; not a clearance)")
    warnings.append("(e) schema-required agent-set strings (claim statement, evidence title, source_type, timestamp) are not constrained: the contract gives no closed form (eval open point)")

    return Verdict(not problems, problems, warnings, exp)


class Recorder:
    """(f) and (g): append-only JSONL of gate RECOMMENDATIONS. No update, delete, clear, approve or supersede exists on this class."""

    ALLOWED_VALUES = ("HOLD_RECOMMENDED", "NO_BLOCKING_FINDINGS_IDENTIFIED", "INCOMPLETE")

    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def records(self):
        return [json.loads(l) for l in self.path.read_text(encoding="utf-8").splitlines() if l.strip()]

    def append_review(self, output, verdict, manifest, run_id):
        """Writes a new record for an ACCEPTED output. Never alters an earlier record, whatever the new value is."""
        if not verdict.accepted:
            raise ValueError("a rejected output is never recorded: " + "; ".join(verdict.problems[:3]))
        value = output["gate_recommendation"]
        if value not in self.ALLOWED_VALUES:
            raise ValueError(f"value {value!r} is outside the three gate values")
        prior = [r for r in self.records() if r["kind"] == "review" and r["case_id"] == manifest["case_id"] and r["pack_id"] == manifest["pack_id"]]
        rec = {"seq": len(self.records()) + 1, "kind": "review", "case_id": manifest["case_id"], "pack_id": manifest["pack_id"],
               "assurance_gate_recommendation": value, "run_id": run_id, "finding_ids": [f["finding_id"] for f in output["findings"]],
               "prior_record_seq": prior[-1]["seq"] if prior else None}
        with self.path.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
        return rec

    def record_human_resolution(self, *, authenticated_role, owner_name, case_id, pack_id, finding_id, reason, date):
        """Stand-in for the separate human channel. `authenticated_role` is SUPPLIED BY THE CALLER and nothing here authenticates it."""
        if authenticated_role != RESOLVING_ROLE:
            raise PermissionError(f"only the {RESOLVING_ROLE} may record a resolution (GD-01); got {authenticated_role!r}")
        if not all([owner_name, finding_id, reason, date]):
            raise ValueError("a resolution is logged with finding id, reason, date and the owner's name")
        rec = {"seq": len(self.records()) + 1, "kind": "human_resolution", "case_id": case_id, "pack_id": pack_id, "finding_id": finding_id,
               "reason": reason, "date": date, "owner_name": owner_name, "role": authenticated_role}
        with self.path.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
        return rec

    def open_holds(self, case_id, pack_id):
        """HOLD records with at least one finding id that no human resolution record covers. A later review never closes one."""
        recs = [r for r in self.records() if r["case_id"] == case_id and r["pack_id"] == pack_id]
        resolved = {r["finding_id"] for r in recs if r["kind"] == "human_resolution"}
        return [r for r in recs if r["kind"] == "review" and r["assurance_gate_recommendation"] == "HOLD_RECOMMENDED"
                and (not r["finding_ids"] or set(r["finding_ids"]) - resolved)]