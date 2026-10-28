"""DC-8 core: the step 9 gate derivation and the handoff.status mapping, as one pure function.

Source of truth: agents/operational/assurance-reviewer.md, Process step 9 and Output Schema "Mapping to the handoff". This module
restates nothing differently; if the contract changes, this must change with it (tests compare it to the evaluation spec).

STAND-IN. Where the contract is ambiguous the choice is named in RESOLUTIONS, cites the open point in
evals/assurance-reviewer.eval.md, and is made only to keep the function total; it is an assumption, not a decision.
"""
from dataclasses import dataclass, field

HOLD = "HOLD_RECOMMENDED"
NO_BLOCKING = "NO_BLOCKING_FINDINGS_IDENTIFIED"
INCOMPLETE = "INCOMPLETE"
GATE_VALUES = (HOLD, NO_BLOCKING, INCOMPLETE)

BLOCKING_ASSESSMENTS = frozenset({"Unsupported", "Contradictory"})
BLOCKING_FINDING_TYPES = frozenset({"missing_approval", "boundary_breach", "embedded_instruction", "source_id_collision"})

# Coverage entry states (contract: Required Inputs, "Coverage entry"). Anything but 'full' is rank 3 (never a stop condition).
COVERAGE_STATES = ("full", "absent", "unapproved_sampling", "outside_approved_rule", "unverifiable_sampling_ref")

# Choices made to keep the function total where the contract leaves a point open. Each is an ASSUMPTION, not a decision.
RESOLUTIONS = {
    # Open point (eval spec, AR-T21/T22): an absent manifest `coverage` field is a manifest-field stop (rank 1) by the manifest row,
    # or rank 3 by the Coverage row ("Absent is rank 3"). Default follows the Coverage row's literal text.
    "coverage_absent": "rank3",
    # Open point: a claim `Unable to determine` counts for rank 3 only "because of a gap". Every Unable to determine is treated as a gap.
    "unable_to_determine": "always_a_gap",
}


@dataclass(frozen=True)
class GateInputs:
    stop_conditions: frozenset = frozenset()        # step 3 conditions that hold (names are free labels)
    claim_assessments: tuple = ()                   # producer claim assessment per reviewed claim
    finding_types: tuple = ()                       # finding_type per finding
    missing_inputs: frozenset = frozenset()         # required inputs, deterministic results or declarations missing or unknown
    coverage: str = "full"
    open_requests_within_timeout_cover_every_gap: bool = False  # DC-5 (or the steward's log): every gap is an open request in time


@dataclass(frozen=True)
class Gate:
    value: str
    rank: int
    handoff_status: str
    reasons: tuple = field(default_factory=tuple)


def is_blocking(assessment=None, finding_type=None):
    """The step 9 rank 2 blocking test for one reviewed claim or one finding."""
    return (assessment in BLOCKING_ASSESSMENTS) or (finding_type in BLOCKING_FINDING_TYPES)


def derive(inputs, resolutions=None):
    """Return the Gate for the inputs: first match wins, ranks 1 to 4 as in step 9."""
    res = dict(RESOLUTIONS, **(resolutions or {}))
    if inputs.coverage not in COVERAGE_STATES:
        raise ValueError(f"unknown coverage state {inputs.coverage!r}")
    stops = set(inputs.stop_conditions)
    if inputs.coverage == "absent" and res["coverage_absent"] == "rank1":
        stops.add("coverage field absent (manifest-field stop reading)")
    if stops:
        return Gate(INCOMPLETE, 1, "escalated", tuple(sorted(stops)))

    blocking = [a for a in inputs.claim_assessments if a in BLOCKING_ASSESSMENTS] + [t for t in inputs.finding_types if t in BLOCKING_FINDING_TYPES]
    if blocking:
        return Gate(HOLD, 2, "escalated", tuple(blocking))

    gaps = sorted(inputs.missing_inputs)
    if "Unable to determine" in inputs.claim_assessments:
        gaps.append("a claim is Unable to determine")
    if inputs.coverage != "full":
        gaps.append(f"coverage entry: {inputs.coverage}")
    if gaps:
        in_progress = inputs.open_requests_within_timeout_cover_every_gap
        return Gate(INCOMPLETE, 3, "in_progress" if in_progress else "escalated", tuple(gaps))

    return Gate(NO_BLOCKING, 4, "completed", ())