You are an independent VERIFIER. You did not write the rows you are checking, and your job is to try to refute them.

RULES OF THE ROAD
- READ-ONLY except for the single output file named at the end. Work only from text you read yourself.
- The DMBOK2 is an INDUSTRY REFERENCE ONLY for this organisation ("GENERAL INDUSTRY CONTEXT"); internal policy outranks it.

WHAT YOU ARE CHECKING
A reader produced .dmbok-work/rows/unit-7.json for unit 7 - Maturity assessment and organisation roles (citations plus one row per assigned concept). Read that file first. The DMBOK2 text (a PDF-to-markdown conversion with `<!-- PDF page N -->` markers) is at C:\Users\ssomai\OneDrive - Ninety One\Documents\claude-data-steward-handoff\claude-data-steward-handoff\DAMA-DMBOK-Summary.md. Read the reader's assigned ranges yourself, with the Read tool, at most 400 lines per call: lines 15147-16358 (Chapters 15 and 16).

CONCEPTS (what the project says, and where)
- A-02 | Governance | Data Steward role and scope
  Project says: The target role is a data governance role rather than an operational incident-resolution role.
  Repo locations: README.md ("data governance role rather than an operational incident-resolution role")
- A-03 | Governance | Data Owner and ownership assignment, including ownership gaps
  Project says: Ownership assignment needs human approval; the Definition & CDE agent surfaces ownership gaps.
  Repo locations: HANDOFF.md ("ownership assignment"); contracts/definition-and-cde-agent.contract.json ("ownership gaps")
- A-04 | Governance | Governance bodies, escalation path and the named human governance owner
  Project says: Escalations route to a named human governance owner who is not yet named (defaults to the project owner); Phase 0b requires roles to be named.
  Repo locations: agents/factory/agent-risk-reviewer.md ("human governance owner"); docs/IMPLEMENTATION-SEQUENCE.md ("Phase 0b")
- A-06 | Governance | Governance reporting and metrics
  Project says: Governance reporting is in scope for the steward; the success criteria define what the system must demonstrate.
  Repo locations: README.md ("governance reporting"); HANDOFF.md ("Success criteria")
- A-07 | Governance | Continuous improvement of stewardship practice
  Project says: Continuous improvement is a listed stewardship responsibility.
  Repo locations: README.md ("continuous improvement")
- A-08 | Governance | Stakeholder input: SMEs, Data Owners and operations teams
  Project says: Agents identify unresolved questions that need SME or Data Owner input.
  Repo locations: HANDOFF.md ("SME or Data Owner input")
- A-31 | Operating model | Stewardship operating model and organisation structure
  Project says: A single Data Steward supported by a Factory layer and an operational agent team; no business-versus-technical steward structure is defined.
  Repo locations: docs/PROPOSED-ARCHITECTURE.md ("Layer 2"); README.md ("Operational Stewardship Team")
- A-32 | Maturity | Capability measurement and success criteria
  Project says: Success criteria define a governed, traceable stewardship capability; no maturity measure is defined.
  Repo locations: HANDOFF.md ("Success criteria")

TASKS
1. For EVERY citation: open the passage (find the marker for its pdf_page and read at least 15 lines either side) and judge whether the quote, in context, supports what the reader's rows say the DMBOK2 position is. Answer yes (supports), partly (supports only in part, or the surrounding text qualifies it), or no (it does not support it, or the surrounding text contradicts or limits it).
2. For EVERY row: read the project files for the concept and the relevant DMBOK2 passages yourself, and judge whether the proposed status and action are fair. Use agree; too_generous (the status hides a gap the evidence shows); too_harsh (the status overstates a gap); or unsure. When not agree, give suggested_status (and suggested_action if the action must change). Status: Aligned | Partial | Divergent | Missing | Out of DMBOK scope. Action: none | citation | wording | structural-proposal | record-deviation. Allowed combinations: Aligned -> none | citation | wording; Partial -> wording | structural-proposal | record-deviation; Divergent -> structural-proposal | record-deviation; Missing -> structural-proposal | record-deviation; Out of DMBOK scope -> none | record-deviation.
3. List anything in your range the reader missed that would change a grade (missing_findings), with the pdf_page and a short note.
Be adversarial but fair: do not answer yes or agree just because a quote exists on the page.

OUTPUT
Write ONE JSON file, .dmbok-work/verify/unit-7.json (the only file you may create), then reply with the single line: WROTE .dmbok-work/verify/unit-7.json
{
  "unit": 7,
  "citation_verdicts": [{"id": "DMBOK2-C03-01", "supports_claim": "yes", "note": ""}],
  "row_verdicts": [{"concept_id": "A-01", "status_fair": "agree", "suggested_status": null, "suggested_action": null, "note": ""}],
  "missing_findings": [{"concept_id": "A-01", "pdf_page": 152, "note": "what the reader missed"}]
}
Exactly one citation_verdict per citation and exactly one row_verdict per row in the reader's file.
