"""DC-1 packet assembly and DC-6 provenance flag (stand-in).

Contract (Build Preconditions, DC-1): assembles the packet and manifest independently of the producer from the named case evidence
store: every record cited by any pack claim, plus every uncited record keyed to the same data-element identifiers as the pack's
claims. A mechanical key match; it does NOT judge contradiction. Writes the store query, the store run id and uncited_evidence_ids.
DC-6: the provenance flag is set here, by assembly, never by the agent.
"""
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from assurance.store import CaseStore


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def cited_ids(output):
    """Every evidence id the producer's pack cites: evidence records and claim evidence ids."""
    ids = {e["source_id"] for e in output.get("cde_evidence", [])}
    handoff = output.get("handoff", {})
    ids |= {e["source_id"] for e in handoff.get("evidence", [])}
    for claim in handoff.get("claims", []):
        ids |= set(claim.get("evidence_ids", []))
    return ids


def provenance_flag(store):
    """DC-6: set from the store's own declaration, never by the agent. An undeclared store reads as missing."""
    return {True: "synthetic", False: "real", None: "missing"}[store.synthetic]


@dataclass
class Packet:
    manifest: dict
    items: dict = field(default_factory=dict)  # packet path -> text


def _json(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def assemble(output, store, *, case_id, pack_id, request, produced_by, authored_by, assembled_by, manifest_approved_by,
             producer_contract=None, governing_docs=None, validator_report=None, approval_extract=None,
             coverage="full", sampling_rule_ref=None):
    items = {"pack/producer-output.json": _json(output)}
    cited = sorted(cited_ids(output))
    elements, unresolved = set(), []
    for sid in cited:
        rec = store.get(sid)
        if rec is None:
            unresolved.append(sid)  # left out on purpose: an id that does not resolve is the reviewer's finding, not ours to hide
            continue
        elements.add(rec["data_element"])
        items[f"evidence/{sid}.json"] = _json({k: v for k, v in rec.items() if k != "data_element"})
    uncited = sorted(r["source_id"] for el in elements for r in store.by_data_element(el) if r["source_id"] not in set(cited))
    for sid in uncited:
        items[f"evidence/{sid}.json"] = _json({k: v for k, v in store.get(sid).items() if k != "data_element"})
    if producer_contract is not None:
        items["governing/producer-contract.json"] = _json(producer_contract)
    for name, text in (governing_docs or {}).items():
        items[f"governing/{name}"] = text
    if validator_report is not None:
        items["checks/validator-report.json"] = _json(validator_report)
    if approval_extract is not None:
        items["checks/approval-log-extract.json"] = _json(approval_extract)

    query = f"records cited by the pack plus records keyed to data elements {sorted(elements)}"
    manifest = {
        "case_id": case_id, "pack_id": pack_id, "request": request,
        "produced_by": produced_by, "authored_by": authored_by,
        "assembled_by": assembled_by, "manifest_approved_by": manifest_approved_by,
        "evidence_store_run_id": store.run_id(query), "evidence_store_query": query,
        "uncited_evidence_ids": uncited,
        "provenance": provenance_flag(store),
        "coverage": coverage, "sampling_rule_ref": sampling_rule_ref,
        "validator_run_id": (validator_report or {}).get("run_id"),
        "approval_log_run_id": (approval_extract or {}).get("run_id"),
        "items": [{"path": p, "version": sha(t)} for p, t in sorted(items.items())],
    }
    return Packet(manifest=manifest, items=items)


def write(packet, directory):
    root = Path(directory)
    for path, text in packet.items.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
    (root / "manifest.json").write_text(_json(packet.manifest), encoding="utf-8", newline="\n")
    return root