# Critical Data Element Criteria Policy

**Status:** Draft, pending owner review. Applies proposal P-05 (option 1). The criteria below start from the DMBOK2 common criticality drivers, which are GENERAL INDUSTRY CONTEXT; the DMBOK2 notes the drivers vary by industry, so the organisation tailors the list [DMBOK2-C13-04]. The structure follows the DMBOK2 policy outline [DMBOK2-C13-60].

## 1. Purpose

To give the Data Steward a consistent, evidence-based checklist for judging whether a data element is critical, so that CDE evidence is comparable across requests.

## 2. Scope and applicability

Applies to any request to identify, evidence or review Critical Data Elements in Investment Operations. It covers how evidence is gathered and judged. It does not cover who may designate a CDE (see section 5).

## 3. Definitions

A **Critical Data Element (CDE)** is a data element that the organisation has formally designated as critical. A data element may *meet criteria* without being *designated*. Designation is a human decision.

## 4. Criticality drivers (starting checklist)

A data element is a candidate when the answer to any driver is yes [DMBOK2-C13-05, DMBOK2-C13-06]. Master Data is treated as critical by definition [DMBOK2-C13-07].

| Driver | Question |
|---|---|
| Regulatory reporting | Is it required for regulatory reporting? |
| Financial reporting | Is it required for financial reporting? |
| Business policy | Is it required to apply a business policy? |
| Ongoing operations | Is it required to run operations day to day? |
| Business strategy | Is it needed to support business strategy? |
| Master Data | Is it Master Data? (critical by definition) |

Assess each driver through the consuming processes, the reports the data appears in, and the financial, regulatory or reputational risk of the data being wrong [DMBOK2-C13-05]. Record the evidence for every yes with its source, location and whether it is direct or inferred.

## 5. Responsibilities

- **Agents** locate and compare existing evidence and present it labelled by evidence category and confidence label. They never designate a CDE, mark one as approved, or assign ownership.
- **Data Steward** evaluates the evidence against this checklist and recommends.
- **Project Owner or the relevant Data Owner** makes any designation (`docs/STEWARDSHIP-FRAMEWORK.md` section 2).

## 6. Reporting

Each assessment lists, per driver, yes / no / unable to determine, with evidence. Drivers marked unable to determine are open questions for the Data Steward, not assumed answers.

## 7. Implementation

This policy takes effect as a draft for the Definition & CDE Agent's evidence work only once the Project Owner approves it. Tailoring of the driver list to the organisation is an open item for the owner.
