You are a READER on a review of how a data-stewardship project aligns with the DAMA-DMBOK (2nd edition).

RULES OF THE ROAD
- READ-ONLY. Do not modify, create or delete any file except the single output file named at the end. Do not run shell commands that write anywhere.
- Work only from text you read. Do not rely on memory of the book: every claim about what the DMBOK2 says must be backed by a passage you read in your assigned range.
- The DMBOK2 is an INDUSTRY REFERENCE ONLY for this organisation: every DMBOK2 statement is "GENERAL INDUSTRY CONTEXT"; adopting any element is a proposal needing human approval; internal policy outranks it.

CONTEXT
The repository (your working directory) designs an AI-augmented stewardship capability for an Investment Operations Data Steward. Its principle: "AI proposes, evidence supports, the Data Steward evaluates, the appropriate human owner approves." The DMBOK2 text is a PDF-to-markdown conversion at C:\Users\ssomai\OneDrive - Ninety One\Documents\claude-data-steward-handoff\claude-data-steward-handoff\DAMA-DMBOK-2nd-Edition.md. Every PDF page starts with a marker line like `<!-- PDF page 152 -->`. Figures are missing (their image links are dead). Section headings carry numbers, for example `#### _1.3.5 Types of Data Stewards_`.

YOUR READING UNIT: unit 6 - Data quality
Read ONLY these line ranges of the DMBOK file, with the Read tool, at most 400 lines per call (use offset and limit): lines 12846-14254 (Chapter 13). You may also read lines 1-1004 (the table of contents) if you need chapter or section numbers. Read your whole range; do not skim and then generalise.

CONCEPTS ASSIGNED TO YOU
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
Open the listed repo files and read the passage around each anchor phrase so you know exactly what the project says before comparing.

TASK
For EACH assigned concept (one row each, no more and no fewer):
1. Find what the DMBOK2 says that is relevant: its terminology, definitions, roles, practices, deliverables.
2. Compare it with the project's position.
3. Propose a status and an action.
STATUS (exactly one): Aligned | Partial | Divergent | Missing | Out of DMBOK scope
- Aligned: concept and wording match DMBOK2 guidance.
- Partial: the concept is present but misses elements the DMBOK2 treats as essential, or uses different terms.
- Divergent: contradicts or conflicts with DMBOK2 guidance (needs a decision).
- Missing: the DMBOK2 treats it as part of stewardship in scope and the project has no artefact.
- Out of DMBOK scope: project-specific (for example AI-agent controls); the DMBOK2 is silent.
ACTION (exactly one): none | citation | wording | structural-proposal | record-deviation
- structural-proposal = adopting a DMBOK2 construct (a role vocabulary, a dimension set, a lifecycle, a field). Give at least two options when the DMBOK2 itself offers alternatives, and say which citation backs each.
- Allowed combinations: Aligned -> none | citation | wording; Partial -> wording | structural-proposal | record-deviation; Divergent -> structural-proposal | record-deviation; Missing -> structural-proposal | record-deviation; Out of DMBOK scope -> none | record-deviation.

CITATION RULES (machine-checked; a failing citation is dropped)
- Each citation is {"id", "chapter", "section", "pdf_page", "quote"}.
- id = DMBOK2-Cnn-nn, where nn counts 01, 02, ... separately for each chapter in your unit; chapter is the number in the id.
- section = the nearest heading ABOVE the quote, starting with its number, for example "1.3.5 Types of Data Stewards".
- pdf_page = the number in the nearest `<!-- PDF page N -->` marker ABOVE the quoted text.
- quote = contiguous text copied from the file: at most 25 words, entirely within one page, no ellipses, no bracketed edits. Plain words are fine (the check ignores markdown emphasis, HTML tags and curly versus straight quotes).
- Never reproduce more than 25 consecutive words. Everything else is your own paraphrase and must read as paraphrase.
- If a claim depends on a figure, add "unverifiable from text" to the row's caveats.
- If the DMBOK2 in your range does not address a concept, say so in dmbok_position and use status Out of DMBOK scope or Missing as the facts warrant.

OUTPUT
Write ONE JSON file, .dmbok-work/rows/unit-6.json (the only file you may create), with exactly this shape, then reply with the single line: WROTE .dmbok-work/rows/unit-6.json
{
  "unit": 6,
  "citations": [{"id": "DMBOK2-C03-01", "chapter": 3, "section": "1.3.5 Types of Data Stewards", "pdf_page": 152, "quote": "text copied from the file"}],
  "rows": [{
    "concept_id": "A-01",
    "dmbok_terms": ["DMBOK2 term for the concept"],
    "citation_ids": ["DMBOK2-C03-01"],
    "dmbok_position": "one or two sentences in your own words",
    "caveats": [],
    "proposed_status": "Partial",
    "status_rationale": "why, naming the project artefact you compared",
    "proposed_action": "wording",
    "proposal_options": []
  }],
  "additional_content": [{"topic": "short topic", "citation_ids": ["DMBOK2-C03-01"], "why_relevant": "one sentence"}],
  "source_caveats": ["anything about the converted text that limits what can be concluded"]
}
proposal_options is [] unless proposed_action is structural-proposal. additional_content lists at most 6 DMBOK2 topics in your range that matter for stewardship in this project but are covered by no assigned concept. Every status other than Out of DMBOK scope needs at least one citation id.
