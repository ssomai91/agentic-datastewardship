"""Guards the recorded Phase 5 runs so the results record cannot drift from the raw outputs."""
import sys

from schema_registry import ROOT

sys.path.insert(0, str(ROOT / "tools"))
import definition_eval as harness  # noqa: E402

RUNS = ROOT / "evals" / "definition-and-cde-runs"


def failed(reports):
    return {r["id"] for r in reports if not r["passed"]}


def test_pass_1_has_exactly_the_two_recorded_schema_failures():
    assert failed(harness.score_recorded(RUNS / "pass1")) == {"S04", "S08"}


def test_pass_2_passes_all_ten_under_the_current_assertions():
    assert failed(harness.score_recorded(RUNS / "pass2")) == set()


def test_pass_3_passes_all_ten_and_has_no_mislabelled_non_evidence_claims():
    import json
    assert failed(harness.score_recorded(RUNS / "pass3")) == set()
    for s in range(1, 11):
        data = json.loads((RUNS / "pass3" / f"S{s:02d}.response.json").read_text(encoding="utf-8"))
        for claim in data["handoff"]["claims"]:
            if claim["claim_type"] in ("open_question", "human_decision_required"):
                assert claim["confidence"] == "Unable to determine" or claim["evidence_ids"], (s, claim["claim_id"])


def test_every_recorded_run_carries_its_own_case_id():
    import json
    for ps, tag in (("pass1", "P1"), ("pass2", "P2"), ("pass3", "P3")):
        for s in range(1, 11):
            data = json.loads((RUNS / ps / f"S{s:02d}.response.json").read_text(encoding="utf-8"))
            assert data["handoff"]["case_id"] == f"EVAL-S{s:02d}-{tag}"


def test_results_record_states_the_scores_and_the_post_hoc_disclosure():
    text = (RUNS / "RESULTS.md").read_text(encoding="utf-8")
    assert "| **8/10** (S04, S08 fail) | **10/10** | **10/10** (frozen, no adjustment) |" in text
    assert "adjusted three times after seeing results" in text
    assert "no tool-call log" in text