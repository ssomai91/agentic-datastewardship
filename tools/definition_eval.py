"""Executable evaluation harness for the Definition & CDE Agent (evals/definition-and-cde-agent.eval.md).

Score an agent against the ten synthetic scenarios in evals/definition-and-cde/scenarios.json, using the
mocked read-only glossary in tools/mock_glossary.py.

    python tools/definition_eval.py --reference            # positive control (rule-based, NOT the real agent)
    python tools/definition_eval.py --responses DIR        # score recorded responses

For --responses, DIR holds S01.response.json ... S10.response.json (the agent's output JSON) and,
optionally, S01.calls.json ... (a list of {"tool", "args"} glossary calls). Without a calls file the
tool-call assertions are reported as SKIPPED rather than passed.

Exit code 1 if any scenario fails; SKIPPED assertions do not fail a scenario but are counted.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from handoff_checks import handoff_reference_problems  # noqa: E402
from mock_glossary import DEFAULT_FIXTURE, GlossaryToolError, MockGlossary  # noqa: E402
from schema_support import SCHEMAS, validator_for  # noqa: E402

SCENARIOS = ROOT / "evals" / "definition-and-cde" / "scenarios.json"
OUTPUT_SCHEMA = SCHEMAS / "outputs" / "definition-and-cde-agent.output.schema.json"
PASS, FAIL, SKIPPED = "PASS", "FAIL", "SKIPPED"
CALL_ASSERTIONS = {"called", "no_write_attempts"}


def load_scenarios():
    return json.loads(SCENARIOS.read_text(encoding="utf-8"))["scenarios"]


def load_fixture():
    return json.loads(DEFAULT_FIXTURE.read_text(encoding="utf-8"))


def _norm(text):
    return re.sub(r"\s+", " ", text).strip().lower()


def _text(response, fields=None):
    parts = response if fields is None else {k: response.get(k) for k in fields}
    return _norm(json.dumps(parts, ensure_ascii=False))


NEGATORS = re.compile(r"\b(not|no|nothing|never|neither|nor|cannot|without)\b|n't")


def _asserted(text, phrase):
    """True if the phrase occurs in the text at least once without a negator in the 30 characters before it."""
    for match in re.finditer(re.escape(phrase), text):
        if not NEGATORS.search(text[max(0, match.start() - 30):match.start()]):
            return True
    return False


def _evidence(response):
    return list(response.get("cde_evidence", [])) + list(response.get("handoff", {}).get("evidence", []))


def _structural_problems(response):
    """Checks every scenario gets: the output schema, and handoff claims that cite real evidence."""
    problems = [e.message[:140] for e in validator_for(OUTPUT_SCHEMA).iter_errors(response)]
    if not problems:
        problems += handoff_reference_problems(response["handoff"])
    return problems


def check(assertion, response, calls, fixture):
    """Return (outcome, detail) for one assertion."""
    kind = assertion["type"]
    if kind in CALL_ASSERTIONS and calls is None:
        return SKIPPED, "no tool-call log supplied"

    if kind == "called":
        wanted = assertion.get("args", {})
        hit = any(c["tool"] == assertion["tool"] and all(c["args"].get(k) == v for k, v in wanted.items()) for c in calls)
        return (PASS if hit else FAIL), f"{assertion['tool']} {wanted}"
    if kind == "no_write_attempts":
        writes = [c for c in calls if c.get("write_attempt")]
        return (PASS if not writes else FAIL), f"{len(writes)} write attempts"
    if kind == "empty":
        return (PASS if not response.get(assertion["field"]) else FAIL), assertion["field"]
    if kind == "nonempty":
        return (PASS if response.get(assertion["field"]) else FAIL), assertion["field"]
    if kind == "candidates_do_not_pick_a_side":
        picked = []
        for cand in response.get("candidate_definitions", []):
            text = _norm(cand.get("draft_text", ""))
            present = [m for m in assertion["exclusive"] if _norm(m) in text]
            if len(present) == 1:
                picked.append(f"{cand.get('term')}: only {present[0]}")
        return (PASS if not picked else FAIL), f"candidate prefers one side: {picked}" if picked else "no side preferred"
    if kind == "candidates_cover_all":
        cands = [_norm(c.get("term", "")) for c in response.get("candidate_definitions", [])]
        missing = [t for t in assertion["terms"] if cands and not any(_norm(t) in c for c in cands)]
        return (PASS if not missing else FAIL), f"candidates cover only part of the matches; missing {missing}" if missing else "all matches or none"
    if kind == "all_status":
        bad = [c for c in response.get(assertion["field"], []) if c.get("status") != assertion["value"]]
        return (PASS if not bad else FAIL), f"{len(bad)} items not {assertion['value']}"
    if kind == "claim_confidence":
        have = {c["confidence"] for c in response["handoff"].get("claims", [])}
        return (PASS if assertion["value"] in have else FAIL), f"wanted {assertion['value']}, have {sorted(have)}"
    if kind == "text_contains":
        text = _text(response, assertion["fields"])
        hit = any(_norm(s) in text for s in assertion["any"])
        return (PASS if hit else FAIL), f"none of {assertion['any']} in {assertion['fields']}" if not hit else "found"
    if kind == "text_not_contains":
        text = _text(response)
        found = [s for s in assertion["any"] if _asserted(text, _norm(s))]
        return (PASS if not found else FAIL), f"forbidden phrases present: {found}" if found else "none present"
    if kind == "cites":
        evidence = _evidence(response)
        missing = []
        for term_id in assertion["ids"]:
            matches = [e for e in evidence if term_id in e.get("source_id", "") or term_id in e.get("location", "")]
            if not matches or (assertion.get("direct") and not any(e.get("direct_or_inferred") == "direct" for e in matches)):
                missing.append(term_id)
        return (PASS if not missing else FAIL), f"missing evidence for {missing}" if missing else "all cited"
    if kind == "verbatim":
        text = _text(response)
        by_id = {t["term_id"]: t for t in fixture["terms"]}
        missing = [i for i in assertion["term_ids"] if _norm(by_id[i]["definition"]) not in text]
        return (PASS if not missing else FAIL), f"definitions not surfaced verbatim: {missing}" if missing else "verbatim"
    if kind == "no_owner_invented":
        text = _text(response)
        owners = [t["owner"].split(" (")[0] for t in fixture["terms"] if t.get("owner")]
        found = [o for o in owners if _norm(o) in text]
        return (PASS if not found else FAIL), f"owner names appear in response: {found}" if found else "no owner named"
    if kind == "industry_context_labelled":
        text = _text(response)
        ok = "industry" not in text or "general industry context" in text
        return (PASS if ok else FAIL), "industry knowledge must be labelled GENERAL INDUSTRY CONTEXT"
    if kind == "no_evidence_cited":
        return (PASS if not _evidence(response) else FAIL), f"{len(_evidence(response))} evidence records cited"
    raise ValueError(f"unknown assertion type {kind!r}")


def score(scenario, response, calls, fixture=None):
    """Score one scenario. Returns {id, passed, results: [(assertion, outcome, detail)]}."""
    fixture = fixture or load_fixture()
    results = []
    structural = _structural_problems(response)
    results.append(({"type": "schema_and_references"}, FAIL if structural else PASS, "; ".join(structural) or "valid"))
    for assertion in scenario["assertions"]:
        outcome, detail = check(assertion, response, calls, fixture)
        results.append((assertion, outcome, detail))
    return {
        "id": scenario["id"],
        "title": scenario["title"],
        "passed": all(outcome != FAIL for _a, outcome, _d in results),
        "results": results,
    }


def run_agent(agent_fn, scenarios=None):
    """Run a callable agent_fn(request, glossary) -> response dict over every scenario."""
    fixture = load_fixture()
    reports = []
    for scenario in scenarios or load_scenarios():
        glossary = MockGlossary(fixture, fail_on=scenario["glossary"]["fail_on"])
        try:
            response = agent_fn(scenario["request"], glossary)
        except Exception as exc:  # an agent that crashes fails the scenario
            reports.append({"id": scenario["id"], "title": scenario["title"], "passed": False,
                            "results": [({"type": "agent_ran"}, FAIL, f"{type(exc).__name__}: {exc}")]})
            continue
        reports.append(score(scenario, response, glossary.calls, fixture))
    return reports


def score_recorded(directory):
    fixture = load_fixture()
    reports = []
    for scenario in load_scenarios():
        response_file = Path(directory) / f"{scenario['id']}.response.json"
        if not response_file.is_file():
            reports.append({"id": scenario["id"], "title": scenario["title"], "passed": False,
                            "results": [({"type": "response_present"}, FAIL, f"{response_file.name} not found")]})
            continue
        calls_file = Path(directory) / f"{scenario['id']}.calls.json"
        calls = json.loads(calls_file.read_text(encoding="utf-8")) if calls_file.is_file() else None
        response = json.loads(response_file.read_text(encoding="utf-8"))
        reports.append(score(scenario, response, calls, fixture))
    return reports


def print_report(reports):
    for report in reports:
        print(f"{report['id']} {'PASS' if report['passed'] else 'FAIL'}  {report['title']}")
        for assertion, outcome, detail in report["results"]:
            if outcome != PASS:
                print(f"    {outcome}: {assertion['type']} - {detail}")
    passed = sum(r["passed"] for r in reports)
    skipped = sum(o == SKIPPED for r in reports for _a, o, _d in r["results"])
    print(f"{passed}/{len(reports)} scenarios passed; {skipped} assertions skipped")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--reference", action="store_true", help="run the rule-based reference agent (positive control)")
    group.add_argument("--responses", metavar="DIR", help="score recorded agent responses")
    args = parser.parse_args(argv)
    if args.reference:
        from reference_definition_agent import reference_agent

        reports = run_agent(reference_agent)
    else:
        reports = score_recorded(args.responses)
    print_report(reports)
    sys.exit(0 if all(r["passed"] for r in reports) else 1)


if __name__ == "__main__":
    main()
