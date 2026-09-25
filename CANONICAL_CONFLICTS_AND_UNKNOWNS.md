---
document_id: canonical-conflicts-and-unknowns
title: Canonical Conflicts, Unknowns, and Validation Queue
version: 1.0.0
status: active_validation_queue
last_reviewed: 2026-09-25
owner: Anthony Grant
change_policy: human_approval_required
sensitivity: confidential
---

# Conflicts, Unknowns, and Validation Queue

This document prevents an AI from silently selecting whichever fact appears most convenient. A contradiction is not a defect to “fix” autonomously. It is a question requiring owner confirmation.

## Resolution rules

1. Use a `VERIFIED` fact only when it appears in an approved canonical document or an owner-approved source.
2. When two sources disagree, retain both in this queue and use `CONCERN` or `UNKNOWN` until Anthony approves one value.
3. Never infer missing facts from titles, file names, URLs, assumptions, or prior model output.
4. AI may draft a patch but may not update a canonical document without explicit human approval.
5. When a fact affects public representation, job eligibility, financial/legal records, credentials, or identity, require direct owner confirmation.

## High-priority validation queue

| ID | Topic | Conflicting / incomplete information | Current handling | Required owner action |
|---|---|---|---|---|
| V-001 | BADGR founding/start date | Supplied materials include February 3, 2025 and January 27, 2025; another statement describes February 2025 generally. | Use `February 2025` only in general narrative; exact date is `UNKNOWN`. | Confirm the legal formation/start date to use in public or official records. |
| V-002 | BADGR legal/display naming | `BADGRTechnologies LLC` and `BADGR Technologies LLC` both appear. | Use legal name `BADGRTechnologies LLC`; use display style only after owner preference confirmation. | Confirm preferred public display style and whether spacing is intentional. |
| V-003 | Business founder/owner identity | Prior supplied business details named Brandon Grant, while résumé/career dossier identifies Anthony Grant. | Do not include founder/owner personal identity in CareerOps business context. | Confirm legal owner/officer wording if it will ever be used publicly. |
| V-004 | Company LinkedIn presence | A LinkedIn company-admin dashboard reference appeared, but no confirmed public company-page URL is retained. | Company LinkedIn = `UNKNOWN`. | Provide confirmed public company URL, if one exists. |
| V-005 | Social-account ownership | Several public URLs were provided but business-vs-personal association and login validity were not independently verified. | Treat every social link as owner-provided but operationally unverified. | Confirm active accounts, intended public links, and whether each is business-owned. |
| V-006 | Company website domains | `badgrtech.com` and `investors.badgrtech.com` appeared. | Use `badgrtech.com` only as the canonical public site; investor subdomain is `UNVERIFIED`. | Confirm whether investor subdomain is active and public. |
| V-007 | Typography | One source says no formal typography; another names Goldman Bold, Inter, and Satoshi. | Use system sans-serif in MVP; fonts are design-intent only. | Confirm brand typography, files, licenses, and allowed use. |
| V-008 | Candidate work authorization | Not provided in approved résumé. | `UNKNOWN`; require truthful manual entry per application. | Confirm only if needed in a secure local profile—not a public repository. |
| V-009 | Relocation assistance | Candidate prefers assistance; no employer-specific availability. | `UNKNOWN` per listing until stated or confirmed. | No global action; validate per role. |
| V-010 | Local hardware/model inventory | Reported August 29, 2026; can change. | `UNVERIFIED_AT_RUNTIME`. | Use runtime commands to refresh before model selection. |
| V-011 | Current job platform access/terms | Platform integrations may be limited by terms, robots controls, APIs, and authentication requirements. | Manual local capture only for MVP. | Approve a source only after compliance review. |
| V-012 | Sensitive credentials | Original business source contained exposed secrets and sensitive identifiers. | Excluded from all canonical docs and source control. | Rotate exposed credentials; move secrets to password manager; never re-add. |

## Known candidate gaps

These are not contradictions. They are important evidence boundaries.

- No verified completed associate or bachelor’s degree.
- No verified active clearance.
- No verified Docker, Kubernetes, Terraform, CI/CD ownership, MLOps ownership, or cloud-architecture ownership.
- No verified 5+ years of conventional software-engineering employment.
- No verified research publications or model-training credentials.
- No verified formal people-management record.
- No verified client/revenue/funding/employee-scale claims for BADGRTechnologies LLC.

## AI handling prompt

When an inconsistency, missing fact, or potential correction is discovered, the AI must respond in this structure:

```text
CONTEXT VALIDATION NOTICE

Document: <canonical document name>
Field or claim: <exact field>
Current canonical value: <value or UNKNOWN>
New/conflicting evidence: <verbatim short excerpt and source>
Impact: <why this matters>
Confidence: VERIFIED / CONCERN / UNVERIFIED / INSUFFICIENT_EVIDENCE
Recommended action: <keep / clarify / replace / remove>

Proposed patch: <unified diff or exact replacement text>

Approval required: No canonical file will be edited unless Anthony explicitly replies with APPROVE PATCH <ID>.
```

## Owner approval format

Use one of the following exact approvals:

```text
APPROVE PATCH V-001
```

```text
APPROVE PATCH V-001 with replacement: 2025-02-03
```

```text
REJECT PATCH V-001
```

```text
DEFER V-001
```
