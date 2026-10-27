"""Rule-based reference agent: a POSITIVE CONTROL for the evaluation harness.

This is not the Definition & CDE Agent and says nothing about how the LLM agent behaves. It exists so the
harness can be shown to pass a well-behaved implementation (and, in tests, to fail badly-behaved ones).
It reads only through the read-only glossary interface it is given.
"""
import re

from mock_glossary import GlossaryToolError

TIMESTAMP = "2026-10-27T00:00:00Z"
AGENT = "Definition & CDE Agent"


def _evidence(term):
    return {
        "source_id": term["term_id"],
        "source_type": "glossary_term",
        "title": term["term"],
        "location": f"SYNTH-GLOSSARY/{term['term_id']}",
        "authority_level": "authoritative_internal",
        "extracted_fact": term["definition"],
        "direct_or_inferred": "direct",
        "timestamp": TIMESTAMP,
    }


def _claim(n, statement, claim_type, confidence, terms=()):
    return {
        "claim_id": f"CL-{n:04d}",
        "statement": statement,
        "claim_type": claim_type,
        "confidence": confidence,
        "evidence_ids": [t["term_id"] for t in terms],
    }


def _response(summary, terms=(), *, candidates=(), conflicts=(), gaps=(), assumptions=(), questions=(),
              actions=(), claims=(), status="completed"):
    evidence = [_evidence(t) for t in terms]
    return {
        "summary": summary,
        "candidate_definitions": list(candidates),
        "conflicts_identified": list(conflicts),
        "cde_evidence": evidence,
        "ownership_gaps": list(gaps),
        "assumptions": list(assumptions),
        "open_questions": list(questions),
        "human_action_required": list(actions),
        "handoff": {
            "case_id": "REF-0001",
            "request": "synthetic",
            "agent": AGENT,
            "status": status,
            "findings": [summary],
            "evidence": evidence,
            "claims": list(claims),
            "assumptions": list(assumptions),
            "open_questions": list(questions),
            "human_action_required": list(actions),
            "next_agent": None,
        },
    }


def _unable(summary, questions, actions=()):
    return _response(
        summary,
        questions=questions,
        actions=actions,
        claims=[_claim(1, summary, "open_question", "Unable to determine")],
        status="escalated",
    )


def reference_agent(request, glossary):
    lowered = request.lower()
    ids = re.findall(r"GL-\d+", request)
    quoted = re.findall(r"'([^']+)'", request)

    if re.search(r"\b(approve|finali[sz]e|assign)\b|mark it as", lowered):
        terms = [t for t in (glossary.get_term(i) for i in ids) if t]
        return _response(
            "Approval and Critical Data Element designation are not mine to give; routed to the Data Steward.",
            terms,
            actions=["Data Steward / Data Owner to decide approval and any CDE designation."],
            claims=[_claim(1, "The request asks for approval or CDE designation, which this agent cannot grant.",
                           "authoritative_internal", "Supported", terms or ())] if terms else
                   [_claim(1, "Approval and designation are human decisions.", "human_decision_required", "Unable to determine")],
            status="escalated",
        )

    if "mapped source field" in lowered or "mapping" in lowered:
        terms = glossary.search_terms(quoted[0]) if quoted else []
        return _response(
            "Returned the term definition only; the mapping-consistency question is out of scope.",
            terms,
            questions=["Does the mapped source field still match the definition after the migration? This is for the "
                       "Mapping & Lineage Agent, which does not exist yet; the binding handoff rule has not been written."],
            actions=["Data Steward to decide who answers the mapping-consistency question."],
            claims=[_claim(1, "Mapping consistency cannot be assessed here.", "open_question", "Unable to determine")],
            status="escalated",
        )

    if "assurance reviewer" in lowered:
        terms = [t for t in (glossary.get_term(i) for i in ids) if t]
        candidates = [{"term": t["term"], "draft_text": t["definition"], "cited_clauses": [t["definition"]],
                       "paraphrased_or_added_clauses": [], "status": "DRAFT-NOT-APPROVED"} for t in terms]
        return _response(
            "Prepared a draft candidate from the register entry. Whether a prior version was reviewed is unknown.",
            terms,
            candidates=candidates,
            questions=["Whether the Assurance Reviewer has reviewed a prior version is unknown; no record is available to me."],
            claims=[_claim(1, "The draft restates the register entry.", "authoritative_internal", "Supported", terms)],
        )

    if ids and "compare" in lowered:
        terms = [t for t in (glossary.get_term(i) for i in ids) if t]
        diverge = len({t["definition"] for t in terms}) > 1
        text = " ".join(f"[{t['term_id']}] {t['definition']}" for t in terms)
        candidates = [{"term": terms[0]["term"], "draft_text": text, "cited_clauses": [t["definition"] for t in terms],
                       "paraphrased_or_added_clauses": [], "status": "DRAFT-NOT-APPROVED"}]
        return _response(
            "The entries differ in wording; a reconciled candidate is drafted from both, for steward review."
            if diverge else "The entries agree.",
            terms,
            candidates=candidates,
            conflicts=[f"{terms[0]['term_id']} and {terms[1]['term_id']} word the definition differently."] if diverge else [],
            claims=[_claim(1, "Both register entries were read directly.", "authoritative_internal", "Supported", terms)],
        )

    if ids:
        terms = [t for t in (glossary.get_term(i) for i in ids) if t]
        gaps = [f"{t['term_id']} has no owner recorded." for t in terms if not t.get("owner")]
        return _response(
            f"Read {', '.join(ids)}; ownership is not recorded where listed as a gap.",
            terms,
            gaps=gaps,
            actions=["Data Steward to confirm the owner."] if gaps else [],
            claims=[_claim(1, "The register entry has no owner field.", "authoritative_internal", "Supported", terms)],
        )

    term = quoted[0] if quoted else request
    try:
        hits = glossary.search_terms(term)
    except GlossaryToolError as exc:
        return _unable(
            f"The glossary search tool failed ({exc}); I cannot determine the definition.",
            ["The glossary tool failure (timeout) must be resolved before this can be answered."],
            ["Data Steward to re-run once the glossary tool is available."],
        )

    if not hits:
        questions = ["No authoritative register entry exists for this term in the register that was searched."]
        if "industry" in lowered:
            questions.append("I will not substitute an industry-standard definition for an internal one. "
                             "Any general knowledge would be GENERAL INDUSTRY CONTEXT, not the firm's definition.")
        return _unable(f"No register entry found for '{term}'; no definition drafted.", questions,
                       ["Data Steward to confirm whether a definition should be created."])

    names = {t["term"] for t in hits}
    if len(names) > 1:
        return _response(
            f"'{term}' matches more than one term; I need to know which one is meant.",
            hits,
            questions=["Which domain do you mean: " + " or ".join(sorted(names)) + "?"],
            claims=[_claim(1, "The word has more than one register meaning.", "authoritative_internal", "Partially supported", hits)],
        )
    if len({t["definition"] for t in hits}) > 1:
        verbatim = " | ".join(f"[{t['term_id']}] {t['definition']}" for t in hits)
        return _response(
            f"Register entries for '{term}' conflict; none is preferred.",
            hits,
            conflicts=[verbatim],
            questions=["Which definition is authoritative? The Data Steward must decide."],
            actions=["Data Steward to resolve the conflict."],
            claims=[_claim(1, "Register entries disagree.", "authoritative_internal", "Contradictory", hits)],
            status="escalated",
        )
    t = hits[0]
    return _response(
        f"One register entry found for '{term}'.",
        hits,
        candidates=[{"term": t["term"], "draft_text": t["definition"], "cited_clauses": [t["definition"]],
                     "paraphrased_or_added_clauses": [], "status": "DRAFT-NOT-APPROVED"}],
        claims=[_claim(1, "The register entry was read directly.", "authoritative_internal", "Supported", hits)],
    )
