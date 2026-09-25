---
document_id: project-guardrails
title: CareerOps Local — Scope, Safety, Privacy, and Compliance Guardrails
version: 1.0.0
status: required
last_reviewed: 2026-09-25
owner: Anthony Grant
change_policy: human_approval_required
---

# CareerOps Local Guardrails

## Product purpose

CareerOps Local is a local, evidence-based job and contract intelligence assistant. Its purpose is to organize permitted job captures, assess fit against a user-approved candidate dossier, identify risks and unknowns, prepare human-review reports, and track user-approved application activity.

It is decision support. It is not an autonomous hiring agent.

## MVP scope

The MVP may:

- Import manually captured or otherwise permitted job listing text and metadata.
- Start with `source_platform=wellfound` as a local-capture adapter.
- Normalize listing fields and preserve raw captures/provenance.
- Score job fit with deterministic, visible rules.
- Identify seniority, salary, location, clearance, degree, skills, stale-listing, staffing, duplicate, and fraud-risk concerns.
- Generate local reports and local application-tracker records.
- Optionally use a local or cloud LLM only for structured extraction and evidence-grounded explanation after deterministic assessment is complete.

The MVP may not:

- Log in to any job platform.
- Scrape, crawl, or bypass robots controls, rate limits, authentication, CAPTCHAs, or terms of service.
- Submit applications.
- Send recruiter, founder, hiring-manager, or employer messages.
- Post to social media.
- Make payments or financial decisions.
- Collect/store passwords, identity documents, financial records, SSN, EIN, DUNS, date of birth, home address, recovery codes, or secret tokens.
- Claim that a listing is legitimate, active, funded, safe, or a guaranteed match.

## Platform compliance

For any source platform:

1. Prefer official APIs, permitted exports, email alerts, manual copy/paste, or user-supplied URLs.
2. Preserve platform name, source URL, capture timestamp, and import method.
3. Treat a platform listing as unverified until an employer-direct source or reliable company evidence is available.
4. Do not use browser automation without explicit, documented owner approval and a legal/terms review for that platform.
5. Do not make user credentials available to AI agents or source code.

## Human-in-the-loop rule

Any action that could affect an employer, platform, candidate record, external communication, application status, or money requires explicit user approval.

Required review labels:

- `REVIEW_FOR_APPLICATION`
- `RESEARCH_COMPANY_FIRST`
- `REQUEST_DETAILS_FROM_RECRUITER`
- `HOLD_FOR_MISSING_COMPENSATION_OR_LOCATION`
- `DO_NOT_APPLY`

No recommendation means “apply automatically.”

## Evidence statuses

| Status | Meaning |
|---|---|
| VERIFIED | Supported by approved source evidence relevant to the claim |
| CONCERN | Conflicting, suspicious, incomplete, or risk-bearing evidence exists |
| UNVERIFIED | Claimed or observed but not reliably confirmed |
| INSUFFICIENT_EVIDENCE | Not enough information to make a defensible assessment |

## Candidate-truth rule

The candidate dossier is the only source of truth for qualifications. Never infer skills, experience, certifications, degree completion, work authorization, clearance, business impact, revenue, leadership, or production scale.

## Data-minimization rule

Store only the data needed for matching and tracking. Keep source captures, normalized listing fields, match assessments, review decisions, and locally approved notes. Redact or reject secrets and high-risk personal data at import.

## Mandatory risk flags

At minimum, detect and report:

- `PAYMENT_REQUEST`
- `SENSITIVE_IDENTITY_REQUEST`
- `PERSONAL_EMAIL_DOMAIN_RECRUITER`
- `URL_DOMAIN_MISMATCH`
- `MISSING_COMPANY_WEBSITE`
- `UNVERIFIABLE_COMPANY`
- `COMPENSATION_OUTLIER`
- `JOB_DESCRIPTION_TOO_VAGUE`
- `EXCESSIVE_URGENCY`
- `CLEARANCE_REQUIRED`
- `DEGREE_REQUIRED`
- `WORK_AUTHORIZATION_RESTRICTION`
- `LOCATION_CONFLICT`
- `SALARY_CONFLICT`
- `STAFFING_INTERMEDIARY`
- `END_CLIENT_UNKNOWN`
- `POSSIBLE_STALE_LISTING`
- `POSSIBLE_DUPLICATE`
- `SENIORITY_MISMATCH`
- `RESEARCH_HEAVY_MISMATCH`
- `MISSING_COMPENSATION`
- `RELOCATION_UNKNOWN`
- `REMOTE_RESTRICTION_UNKNOWN`
- `REQUIRED_SKILL_GAP`

## Security baseline

- `.env`, secrets, local databases, raw private captures, and logs must be gitignored.
- Provide `.env.example` only, with blank values and no real secrets.
- Use secret scanning in CI/local checks.
- Do not log raw job captures containing contact details by default.
- Use local SQLite in an ignored data directory for MVP.
- Provide a `careerops doctor` command that checks permissions, migration state, ignored secrets, and unsafe tracked files.

## Model-provider policy

- Deterministic operation must be fully functional with no LLM configured.
- Local Ollama may be used as an optional provider after local validation.
- Cloud providers must be opt-in and configured only through local environment variables.
- LLM outputs must be structured, schema-validated, advisory, and grounded in supplied records.
- An LLM cannot override hard blockers, source facts, or deterministic score components.

## Quality gate

No phase is complete unless:

- Tests pass without network access or LLM credentials.
- Input provenance is preserved.
- Reports distinguish facts, risk signals, and unknowns.
- No external action exists in code paths.
- No secrets or sensitive identifiers appear in tracked files.
