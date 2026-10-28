"""DC-2 packet-scoped read guard, and the slice end to end: assemble -> write -> guarded read -> gate pre-checks."""
import json
import os
import sys

import pytest

from schema_registry import ROOT, SCHEMAS

sys.path.insert(0, str(ROOT / "tools"))
from assurance.approval_log import lookup  # noqa: E402
from assurance.assemble import assemble, write  # noqa: E402
from assurance.gate import GateInputs, derive  # noqa: E402
from assurance.manifest import coverage_state, missing_inputs, stop_conditions  # noqa: E402
from assurance.packet_read import PacketAccessError, PacketReader  # noqa: E402
from assurance.store import CaseStore  # noqa: E402
from assurance.validator import validate  # noqa: E402
from mock_glossary import CAPABILITIES  # noqa: E402

GLOSSARY = ROOT / "fixtures" / "definition-and-cde" / "glossary.json"
LOG = ROOT / "fixtures" / "assurance" / "approval-log.json"
SCHEMA = SCHEMAS / "outputs" / "definition-and-cde-agent.output.schema.json"
ROLES = dict(produced_by="SYN Definition & CDE Agent", authored_by="SYN Definition & CDE Agent",
             assembled_by="SYN-ROLE-ASSEMBLER", manifest_approved_by="SYN-ROLE-MANIFEST-APPROVER")


def real_pack(scenario, passno="pass3", calls=None):
    out = json.loads((ROOT / "evals" / "definition-and-cde-runs" / passno / f"{scenario}.response.json").read_text(encoding="utf-8"))
    report = validate(out, SCHEMA, set(CAPABILITIES.values()), calls)
    store = CaseStore.from_glossary(GLOSSARY)
    elements = sorted({store.get(e["source_id"])["data_element"] for e in out.get("cde_evidence", []) if store.get(e["source_id"])}) or ["none"]
    extract = lookup(LOG, elements)
    return out, assemble(out, store, case_id=f"EVAL-{scenario}-P3", pack_id=f"PASS3-{scenario}", request=out["handoff"]["request"], **ROLES,
                         validator_report=report, approval_extract=extract), report


def test_reads_inside_the_manifest_succeed_and_everything_else_fails_mechanically(tmp_path):
    _, packet, _ = real_pack("S01")
    root = write(packet, tmp_path / "pkt")
    (root / "stray.txt").write_text("not in the manifest", encoding="utf-8")
    reader = PacketReader(root)
    for item in packet.items:
        assert reader.read(item) == packet.items[item]
    assert json.loads(reader.read("manifest.json"))["case_id"] == packet.manifest["case_id"]
    for bad in ("../outside.txt", "stray.txt", "pack/../../x", "/etc/passwd", "C:/Windows/win.ini", "../SYN-repo/GOVERNANCE-DECISIONS", "pack/not-listed.json"):
        with pytest.raises(PacketAccessError):
            reader.read(bad)
    assert "stray.txt" in reader.calls  # every attempt is recorded, successful or not


def test_a_symlink_that_escapes_the_packet_is_refused(tmp_path):
    _, packet, _ = real_pack("S01")
    root = write(packet, tmp_path / "pkt")
    secret = tmp_path / "secret.txt"
    secret.write_text("outside", encoding="utf-8")
    link = root / "pack" / "producer-output.json"
    link.unlink()
    try:
        os.symlink(secret, link)
    except (OSError, NotImplementedError):
        pytest.skip("cannot create symlinks on this machine")
    with pytest.raises(PacketAccessError):
        PacketReader(root).read("pack/producer-output.json")


def test_end_to_end_with_no_tool_call_log_the_real_packs_gate_incomplete_at_rank_3():
    """The honest first result: none of the recorded LLM runs has a tool-call log, so boundary adherence cannot be checked."""
    for s in range(1, 11):
        out, packet, report = real_pack(f"S{s:02d}")
        stops, missing = stop_conditions(packet.manifest), set(missing_inputs(packet.manifest, packet.items))
        assert not stops, (s, stops)
        gate = derive(GateInputs(frozenset(stops), tuple("Supported" for _ in out["handoff"]["claims"]), (), frozenset(missing | {"boundary check result"}), coverage_state(packet.manifest)))
        assert (gate.value, gate.rank, gate.handoff_status) == ("INCOMPLETE", 3, "escalated"), s


def test_end_to_end_with_a_labelled_stand_in_call_log_the_same_pack_can_reach_a_clean_gate():
    calls = [{"tool": "get_term", "args": {"term_id": "GL-101"}}]  # STAND-IN: not a real log of that run
    out, packet, report = real_pack("S01", calls=calls)
    missing = set(missing_inputs(packet.manifest, packet.items))
    assert not missing and not stop_conditions(packet.manifest)
    gate = derive(GateInputs(claim_assessments=tuple("Supported" for _ in out["handoff"]["claims"]), coverage=coverage_state(packet.manifest)))
    assert (gate.value, gate.rank, gate.handoff_status) == ("NO_BLOCKING_FINDINGS_IDENTIFIED", 4, "completed")


def test_the_manifest_checks_catch_the_stop_conditions_on_a_real_pack_and_the_gate_ranks_them_first():
    out, packet, _ = real_pack("S08")
    m = {**packet.manifest, "assembled_by": packet.manifest["produced_by"]}
    stops = stop_conditions(m)
    assert stops
    assert derive(GateInputs(frozenset(stops), claim_assessments=("Unsupported",))).rank == 1