# Glossary: codes, acronyms and how to read them

For anyone reading this repository for the first time. The codes below appear across the contracts, evaluations, decisions and status documents. If a code is not here, search the repository for it: most are defined where they are first used. `docs/BUILD-STATUS.md` shows where everything stands.

## 1. Status words

| Word | Meaning |
|---|---|
| **Draft** | Written, reviewed by the Factory, but not approved. Every agent contract is Draft. Only the Project Owner can change that. |
| **Decided** | The Project Owner chose it (recorded in `GOVERNANCE-DECISIONS.md`). |
| **Open** | A decision still waiting on the Project Owner. Nothing downstream should assume an answer. |
| **Proposed** | Someone (often Claude) suggested it. It is not a decision until the owner says so. |
| **Accepted / Applied** | Accepted means the owner agreed. Applied means the change was made, usually as a Draft document. |
| **Stand-in** | A simplified placeholder for something that does not exist yet. Never a real system. |
| **Synthetic / `SYN-`** | Made-up data. Anything starting `SYN-` is fabricated. The repository holds synthetic data only. |
| **Frozen** | Expected results written down and committed before a test run, so they cannot be adjusted after seeing the result. |
| **Open point** | A place where a contract is ambiguous or has no approved threshold. Listed for the owner; none is decided by the code. |

## 2. Roles

| Role | Meaning |
|---|---|
| **Project Owner** | The human governance owner. Approves contracts and designs, adjudicates contested findings, resolves holds. (`GD-01`) |
| **Deputy** | Acts for the Project Owner when unavailable. Whether the deputy may resolve a hold is an unresolved assumption. |
| **Data Steward** | Evaluates and recommends. Never approves. |
| **Data Owner** | The business owner of a data set, who decides on quality issues about it. |
| **SME** | Subject-matter expert. |
| **Executive sponsor** | Sponsors the capability and removes blockers; not a day-to-day approver. |

Role names are titles. The people's names are still blank.

## 3. Decisions (`GOVERNANCE-DECISIONS.md`)

| Code | Decision | State |
|---|---|---|
| **GD-01** | Who approves Factory outputs and who may override a Risk Reviewer finding | Decided, names pending |
| **GD-02** | Evidence retention and redaction | Decided: synthetic data only |
| **GD-03** | Whether DMBOK2 alignment stays in scope | Decided: yes, and done |
| **GD-04** | Data-quality taxonomy | Decided as a working default (DAMA UK six dimensions) |
| **GD-05** | Which glossary or catalogue system the Definition & CDE Agent reads from | **Open** |
| **GD-06** | The 14 DMBOK alignment proposals | Accepted and applied as Drafts |
| **GD-07** | Assurance Reviewer scope and hold semantics | Scope decided (full v0); hold semantics deferred |

## 4. Agents

| Agent | Layer | Role |
|---|---|---|
| Stewardship Agent Architect | Factory | Designs a candidate agent and classifies the capability |
| Agent Risk & Governance Reviewer | Factory | Challenges a design; never approves |
| Agent Evaluation Designer | Factory | Writes the test specification for an agent |
| Claude Agent Builder | Factory | Turns a contract into a draft prompt, with a coverage trace |
| Definition & CDE Agent | Operational | Compares glossary definitions and prepares CDE evidence |
| Assurance Reviewer | Operational | Independently challenges another agent's output pack |

Designed but not built: Investment Operations Context Agent, Mapping & Lineage Agent, Data Quality Agent, Exception & Root-Cause Agent and the Stewardship Orchestrator.

**Factory** = the four design-time agents. **Authority chain** = Markdown contract (source of truth) then JSON contract then prompt (`docs/AUTHORITY-CHAIN.md`).

## 5. Domain terms

| Term | Meaning |
|---|---|
| **CDE** | Critical Data Element: a data field the organisation formally designates as critical. |
| **DMBOK / DMBOK2** | DAMA's *Data Management Body of Knowledge*, 2nd edition: an industry reference. Aligned to, never binding. |
| **DAMA** | The professional body that publishes it. |
| **DMBOK2-C13-12** | A citation: chapter 13, item 12, checked against its PDF page in `docs/dmbok2-citations.json`. |
| **ITSM** | IT service management: an existing ticketing or case-management platform. Relevant to the case-store decision. |
| **Case store** | Where case records and gate recommendations would be kept. Not chosen. |
| **Hold** | A `HOLD_RECOMMENDED` gate. Whether a hold blocks progress or only advises is undecided. |

## 6. Assurance Reviewer

| Code | Meaning |
|---|---|
| **DC-1 to DC-8** | **D**eterministic **C**omponents: pieces that must exist outside the agent. |
| DC-1 | Packet assembly (builds the evidence packet and manifest independently of the producer) |
| DC-2 | Packet-scoped read (the agent can read only the packet) |
| DC-3 | Validator and boundary checker |
| DC-4 | Approval-log lookup |
| DC-5 | Evidence-request tracker (deferred) |
| DC-6 | Provenance flag (synthetic or real, set by assembly) |
| DC-7 | Coverage register (deferred) |
| DC-8 | Status recorder and output checker |
| **Packet / manifest** | The evidence bundle the agent may read, and its contents list (who produced, assembled and approved it) |

**Gate values** (the agent's recommendation, never a clearance or approval):

| Gate | Meaning |
|---|---|
| `HOLD_RECOMMENDED` | A blocking problem was found |
| `NO_BLOCKING_FINDINGS_IDENTIFIED` | None found. This does not mean the pack is correct |
| `INCOMPLETE` | It cannot judge: something is missing or cannot be trusted |

**Rank 1 to 4** is the order the gate is decided in. The first match wins: **1** a stop condition (for example provenance missing), **2** a blocking finding, **3** a gap (missing input or an `Unable to determine` claim), **4** clean.

**Blocking** means a claim assessed `Unsupported` or `Contradictory`, or a finding of type `missing_approval`, `boundary_breach`, `embedded_instruction` or `source_id_collision`.

**handoff.status** is the agent's work state: `completed`, `in_progress` or `escalated`. `blocked` is never used. `Draft` is not a status.

## 7. Confidence labels

Five labels on any claim: **Supported**, **Partially supported**, **Unsupported**, **Contradictory**, **Unable to determine**. Supported, Partially supported and Contradictory must cite evidence. A producer's own open question or human-decision claim is `Unable to determine`.

## 8. IDs you will see in files

| Pattern | Means |
|---|---|
| `GL-101` | A term in the synthetic glossary |
| `S01` to `S10` | The ten Definition & CDE test scenarios |
| `A1` to `A6` | The six packets in the first Assurance Reviewer run |
| `AR-T01` to `AR-T66` | The 66 test cases for the Assurance Reviewer |
| `P0-01` and similar | Items from the build backlog list (P0 to P4) |
| `P-01` to `P-14` | The 14 DMBOK alignment proposals (not backlog items) |
| `AR-EV-…` | An evidence record the Assurance Reviewer wrote itself |
| `AR-C-GATE` | The agent's own claim stating its gate |
| `AR-<case>-<pack>-001` | A finding id: case, pack, then a number |
| `C1`, `CL-0001`, `CL-SEED-1` | Claim ids inside a pack. `CL-SEED-1` is a deliberately planted bad claim |

## 9. Phases and runs

| Term | Meaning |
|---|---|
| **Phase 0 to 8** | The build sequence in `docs/IMPLEMENTATION-SEQUENCE.md`. `docs/BUILD-STATUS.md` shows each one's state |
| **Pass 1, 2, 3** | Repeated test runs. The numbering restarts in each evaluation: for the Definition & CDE Agent (`evals/definition-and-cde-runs/`) and separately for the Assurance Reviewer (`evals/assurance-runs/`) |
| **Seeded** | A pack with one deliberate defect added, to see whether the agent catches it |
| **Stopping rule** | A rule fixed in advance for when a model review loop ends (`evals/factory-runs/p6-assurance-reviewer.STOPPING-RULE.md`) |
| **CI** | Continuous integration: GitHub runs the test suite on every push (`.github/workflows/tests.yml`) |
| **PR** | Pull request: a request on GitHub to merge a branch |
| **Amendment** | A change to a contract. Goes in the Markdown contract first, then the JSON, then the prompt, with a version bump |

## 10. How to read a result

- A **match against a frozen expectation** means the agent behaved as predicted. It is not proof the agent is reliable: the runs so far are six packets, one run each.
- A **recorder rejection** means the deterministic checker found a difference from what the contract's rules compute. Read the problem text before deciding who is wrong: in the first run several rejections were the checker being stricter than the contract.
- **Unable to determine** is the correct answer when evidence is missing. It is not a failure.