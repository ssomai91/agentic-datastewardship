# Glossary System and Tool Mapping (Definition & CDE Agent)

**Status:** Draft. The organisation's glossary/catalogue system has **not been selected** (see `GOVERNANCE-DECISIONS.md`, GD-05, Open). This document fixes everything that does not depend on the choice, and leaves the system-specific column empty until the Project Owner decides.

## 1. Capability map

The agent contract (`agents/operational/definition-and-cde-agent.md`, Permitted Tools) names five read-only capabilities. The mocked interface in `tools/mock_glossary.py` implements them one-to-one, so the evaluation harness exercises the same shape a real system must provide.

| Contract capability | Mock method | What the real tool must return | Real system tool |
|---|---|---|---|
| Search glossary terms | `search_terms(query)` | Matching terms with id, name, definition | _pending system selection_ |
| Get glossary term detail | `get_term(term_id)` | One term with definition, owner (if any), status, version, CDE flag (if recorded) | _pending_ |
| Get glossary categories | `get_categories()` | Category ids and names | _pending_ |
| Get glossary term links | `get_term_links(term_id)` | Relationships and synonyms for a term | _pending_ |
| Bulk glossary export | `bulk_export()` | All terms, for conflict detection | _pending_ |

## 2. Prohibited actions that must stay unreachable

Whatever system is chosen, no tool in the agent's permitted set may be able to do any of the following (contract `prohibited_tools_or_actions`). `tests/test_definition_eval.py` checks that the mock refuses each.

- create, update or delete a term
- change a term's status
- create term-to-term links
- create a glossary
- create a glossary category

Enforcement belongs in the tool allow-list, not in the agent's good behaviour: expose only the five read tools, with credentials that have read-only rights on the system.

## 3. Selection criteria for the system (for the Project Owner)

1. A read-only service account or token can be issued, with no write scope at all.
2. Each of the five capabilities above is available, or can be composed from available calls.
3. Term records carry owner, status and version fields, so ownership gaps can be reported rather than guessed.
4. Calls are logged, so every glossary read can be traced to an evidence record.
5. Nothing in this repository connects to production (`docs/REPO-CONVENTIONS.md`): connecting the agent to the real system is a separate, approved step.

## 4. When a system is chosen

1. Fill in the "Real system tool" column with the system's exact tool identifiers, and record GD-05 as Decided.
2. Re-express the P4-01 Factory pass condition (`evals/factory-test-scenarios.md`) against those identifiers, as that scenario itself says.
3. Add a thin adapter with the same five method names as `MockGlossary`, then run `python tools/definition_eval.py` against recorded responses from the real tool before any use on real data.
4. Update the contract's *Assumptions Pending Human Confirmation* and the Definition & CDE prompt's limitation note.