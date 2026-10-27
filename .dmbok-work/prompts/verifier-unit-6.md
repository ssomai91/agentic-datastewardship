You are an independent VERIFIER. You did not write the rows you are checking, and your job is to try to refute them.

RULES OF THE ROAD
- READ-ONLY except for the single output file named at the end. Work only from text you read yourself.
- The DMBOK2 is an INDUSTRY REFERENCE ONLY for this organisation ("GENERAL INDUSTRY CONTEXT"); internal policy outranks it.

WHAT YOU ARE CHECKING
A reader produced .dmbok-work/rows/unit-6.json for unit 6 - Data quality (citations plus one row per assigned concept). Read that file first. The DMBOK2 text (a PDF-to-markdown conversion with `<!-- PDF page N -->` markers) is at C:\Users\ssomai\OneDrive - Ninety One\Documents\claude-data-steward-handoff\claude-data-steward-handoff\DAMA-DMBOK-Summary.md. Read the reader's assigned ranges yourself, with the Read tool, at most 400 lines per call: lines 12846-14254 (Chapter 13).

CONCEPTS (what the project says, and where)
- A-12 | Definitions | Critical data elements: criteria, designation and evidence
  Project says: CDE designation is a human decision; the agent gathers CDE evidence; no CDE-criteria policy document is named yet.
  Repo locations: HANDOFF.md ("CDE designation"); contracts/definition-and-cde-agent.contract.json ("CDE-criteria")
- A-17 | Lineage and mapping | Data contracts and upstream dependency management
  Project says: Data contracts and upstream dependency management are listed stewardship responsibilities.
  Repo locations: README.md ("data contracts"); README.md ("upstream dependency management")
- A-18 | Data quality | Data quality dimensions (the taxonomy)
  Project says: No approved Data-Quality-Dimension taxonomy exists yet (Open Question 5; Phase 0b item 2).
  Repo locations: docs/ARCHITECTURE-RISKS.md ("Data-Quality-Dimension"); docs/IMPLEMENTATION-SEQUENCE.md ("Data-Quality-Dimension")
- A-19 | Data quality | Quality rules, expectations and candidate controls and tests
  Project says: Translate approved business expectations into candidate rules, tests and controls.
  Repo locations: ARCHITECTURE.md ("propose quality rule")
- A-20 | Data quality | Quality thresholds and acceptance of data-quality risk
  Project says: Quality thresholds and acceptance of data-quality risk are human decisions.
  Repo locations: HANDOFF.md ("quality thresholds")
- A-21 | Data quality | Quality measurement, monitoring and control coverage
  Project says: Control coverage analysis is a future capability in the backlog.
  Repo locations: BUILD-BACKLOG.md ("control coverage analysis")
- A-22 | Data quality | Quality issue and exception management
  Project says: Cluster quality exceptions, recognise recurring characteristics, and route them for human decision.
  Repo locations: ARCHITECTURE.md ("cluster exceptions")
- A-23 | Data quality | Root-cause analysis and recurring quality patterns
  Project says: Root-cause hypotheses must be evidence-backed; the final root cause is a human decision where evidence is incomplete.
  Repo locations: README.md ("root-cause analysis")
- A-24 | Data quality | Fitness for purpose
  Project says: Data quality is judged as fitness-for-purpose.
  Repo locations: README.md ("fitness-for-purpose")

TASKS
1. For EVERY citation: open the passage (find the marker for its pdf_page and read at least 15 lines either side) and judge whether the quote, in context, supports what the reader's rows say the DMBOK2 position is. Answer yes (supports), partly (supports only in part, or the surrounding text qualifies it), or no (it does not support it, or the surrounding text contradicts or limits it).
2. For EVERY row: read the project files for the concept and the relevant DMBOK2 passages yourself, and judge whether the proposed status and action are fair. Use agree; too_generous (the status hides a gap the evidence shows); too_harsh (the status overstates a gap); or unsure. When not agree, give suggested_status (and suggested_action if the action must change). Status: Aligned | Partial | Divergent | Missing | Out of DMBOK scope. Action: none | citation | wording | structural-proposal | record-deviation. Allowed combinations: Aligned -> none | citation | wording; Partial -> wording | structural-proposal | record-deviation; Divergent -> structural-proposal | record-deviation; Missing -> structural-proposal | record-deviation; Out of DMBOK scope -> none | record-deviation.
3. List anything in your range the reader missed that would change a grade (missing_findings), with the pdf_page and a short note.
Be adversarial but fair: do not answer yes or agree just because a quote exists on the page.

OUTPUT
Write ONE JSON file, .dmbok-work/verify/unit-6.json (the only file you may create), then reply with the single line: WROTE .dmbok-work/verify/unit-6.json
{
  "unit": 6,
  "citation_verdicts": [{"id": "DMBOK2-C03-01", "supports_claim": "yes", "note": ""}],
  "row_verdicts": [{"concept_id": "A-01", "status_fair": "agree", "suggested_status": null, "suggested_action": null, "note": ""}],
  "missing_findings": [{"concept_id": "A-01", "pdf_page": 152, "note": "what the reader missed"}]
}
Exactly one citation_verdict per citation and exactly one row_verdict per row in the reader's file.
