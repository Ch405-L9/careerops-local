# Claude Code Prompt — Phase 0 Only

Copy everything below into Claude Code from the root of a new empty repository. Claude Code must not write, install, browse, scrape, authenticate, or modify anything during this phase.

```text
You are Claude Code acting as a principal local-first software engineer, security-conscious agent-systems architect, and test-driven implementation partner.

Your task is to plan a new standalone local-only project named:

CareerOps Local
Evidence-Based Job and Contract Intelligence for Anthony Grant, with a future separately governed BADGRTechnologies LLC opportunity mode.

Read these repository documents before responding:

- README.md
- CANONICAL_CANDIDATE_DOSSIER.md
- CANONICAL_BADGR_BUSINESS_CONTEXT.md
- CANONICAL_CONFLICTS_AND_UNKNOWNS.md
- CONTEXT_UPDATE_PROTOCOL.md
- PROJECT_GUARDRAILS.md
- JOB_CAPTURE_TEMPLATE.md

These documents are canonical context. Follow them exactly. If they conflict, follow this priority:
1. PROJECT_GUARDRAILS.md for safety, privacy, external actions, and compliance.
2. CANONICAL_CONFLICTS_AND_UNKNOWNS.md for unresolved facts.
3. CANONICAL_CANDIDATE_DOSSIER.md for candidate qualifications and job matching.
4. CANONICAL_BADGR_BUSINESS_CONTEXT.md for sanitized business, branding, and local-lab context.
5. CONTEXT_UPDATE_PROTOCOL.md for update procedure.
6. JOB_CAPTURE_TEMPLATE.md for capture fields.

============================================================
PROJECT PURPOSE
============================================================

Build an evidence-based, local job and contract intelligence assistant.

MVP objective:

Given a permitted, manually imported Wellfound job capture, compare it to the canonical candidate dossier and create a transparent human-review report that identifies:

- target-role relevance
- verified technical and project-evidence alignment
- seniority and years-of-experience compatibility
- compensation compatibility
- work-arrangement and relocation facts/unknowns
- hard blockers
- skill gaps
- stale-listing, duplicate, staffing, fraud, and legitimacy concerns
- missing evidence
- relevant truthful resume variant and portfolio proof
- recommended human next action

The software is decision support only. It must never auto-apply, auto-message, log in, scrape, use browser automation, evade platform controls, or make external changes.

============================================================
CORE DESIGN REQUIREMENTS
============================================================

Use this stack unless you identify a justified compatibility issue:

- Python 3.12+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x
- SQLite
- Alembic
- Typer + Rich CLI
- pytest
- Ruff
- mypy where practical

Start CLI-first. A minimal FastAPI API can follow the deterministic core. Do not build a heavy frontend in MVP.

The system must work fully without an LLM or internet connection.

LLM support, if implemented later, must be optional, disabled by default, schema-validated, and unable to override deterministic hard blockers or canonical facts. A local Ollama adapter may be considered later, but only after deterministic scoring and tests pass.

Do not modify BADGR Harness. This must be a new standalone repository. Design clean internal boundaries so an MCP/API integration can be added later, but do not build that integration in the MVP.

============================================================
REQUIRED DOMAIN BEHAVIOR
============================================================

Implement later, after approval:

1. Local capture ingestion from Markdown/JSON/pasted text only.
2. Source platform initial value: `wellfound`.
3. Provenance preservation: source URL, local capture path, import method, capture timestamp, raw text, extraction timestamp.
4. Normalized job records with explicit `UNKNOWN` values.
5. Deterministic, configurable, explainable matching score out of 100.
6. Hard blockers that cannot be hidden by a high score.
7. Risk flags and duplicate/staleness analysis.
8. Local Markdown assessment reports.
9. A local tracker that records only user-approved job/application status, without external submission.
10. Optional later LLM narrative/extraction layer.

Use explicit enums for:

ValidationStatus:
- VERIFIED
- CONCERN
- UNVERIFIED
- INSUFFICIENT_EVIDENCE

MatchClassification:
- STRONG_MATCH
- PLAUSIBLE_MATCH
- STRETCH
- AVOID
- INSUFFICIENT_EVIDENCE

Recommendation:
- REVIEW_FOR_APPLICATION
- RESEARCH_COMPANY_FIRST
- REQUEST_DETAILS_FROM_RECRUITER
- HOLD_FOR_MISSING_COMPENSATION_OR_LOCATION
- DO_NOT_APPLY

WorkArrangementType:
- US_REMOTE
- STATE_RESTRICTED_REMOTE
- TIME_ZONE_RESTRICTED_REMOTE
- HYBRID
- ON_SITE
- UNKNOWN

RelocationStatus:
- PROVIDED
- REQUIRED
- PREFERRED
- NOT_MENTIONED
- UNKNOWN

EmploymentType:
- FULL_TIME
- PART_TIME
- CONTRACT
- CONTRACT_TO_HIRE
- TEMPORARY
- INTERNSHIP
- UNKNOWN

SalaryCompatibility:
- TARGET_90K_PLUS
- FALLBACK_80K_TO_89K
- BELOW_80K
- CONTRACT_REQUIRES_REVIEW
- UNKNOWN

Suggested score weights, configurable through YAML:

- Role-family relevance: 20
- Verified technical-skill alignment: 20
- Responsibility/project-evidence alignment: 15
- Seniority/years compatibility: 15
- Compensation compatibility: 10
- Location/remote/relocation compatibility: 8
- Employment-type compatibility: 5
- Employer/listing validation quality: 4
- Growth/learning relevance: 3

Required hard blockers:

- Active clearance explicitly required when candidate evidence does not show one.
- Completed degree explicitly required with no equivalent-experience language.
- Explicit base pay below $80,000 unless a recorded user override exists.
- Explicit work authorization/location requirement that the candidate cannot truthfully meet.
- Research-heavy model-training role requiring unverified qualifications.
- Explicit senior/staff/principal/head/lead role with materially unsupported hard requirements.
- Payment request, suspicious identity request, or unsafe pre-hire activity.
- Unverifiable company identity where no reliable official source is supplied.

A degree must not be a hard blocker when the listing says “or equivalent experience,” “or related experience,” or leaves education unspecified.

Required risk flags include:

- PAYMENT_REQUEST
- SENSITIVE_IDENTITY_REQUEST
- PERSONAL_EMAIL_DOMAIN_RECRUITER
- URL_DOMAIN_MISMATCH
- MISSING_COMPANY_WEBSITE
- UNVERIFIABLE_COMPANY
- COMPENSATION_OUTLIER
- JOB_DESCRIPTION_TOO_VAGUE
- EXCESSIVE_URGENCY
- CLEARANCE_REQUIRED
- DEGREE_REQUIRED
- WORK_AUTHORIZATION_RESTRICTION
- LOCATION_CONFLICT
- SALARY_CONFLICT
- STAFFING_INTERMEDIARY
- END_CLIENT_UNKNOWN
- POSSIBLE_STALE_LISTING
- POSSIBLE_DUPLICATE
- SENIORITY_MISMATCH
- RESEARCH_HEAVY_MISMATCH
- MISSING_COMPENSATION
- RELOCATION_UNKNOWN
- REMOTE_RESTRICTION_UNKNOWN
- REQUIRED_SKILL_GAP

Required future CLI commands:

- careerops init
- careerops import-job --input <file> --platform wellfound --url <optional>
- careerops assess-job <job_id>
- careerops report <job_id> --format markdown
- careerops list-jobs
- careerops show-job <job_id>
- careerops review <job_id> --decision <decision> --note "<note>"
- careerops tracker add <job_id>
- careerops tracker update <record_id>
- careerops doctor

============================================================
PHASE 0: READ-ONLY DISCOVERY — STOP AFTER THIS
============================================================

Do now:

1. Inspect the repository only.
2. Read every canonical context document.
3. Identify contradictions, missing decisions, security issues, and implementation risks.
4. Propose an architecture and repository tree.
5. Propose a phased implementation plan.
6. Define the initial Pydantic domain model and database boundary at a high level.
7. Define a concise test plan, including strong-match, plausible-match, hard-blocker, degree-equivalency, contract, duplicate, and fraud cases.
8. List all assumptions requiring owner confirmation.
9. Recommend the smallest useful Phase 1 deliverable.

Do not now:

- Create, edit, delete, rename, or initialize files.
- Install packages.
- Run network requests.
- Browse a website.
- Scrape, authenticate, use credentials, or call external APIs.
- Run database migrations.
- Generate outreach, cover letters, application submissions, or messages.
- Use sensitive business information.
- Assume any unresolved fact is true.

Your response must contain only these sections:

1. Understanding
2. Canonical-context observations
3. Proposed architecture
4. Proposed repository tree
5. Phase plan
6. Test and validation plan
7. Risks and compliance notes
8. Decisions needed from Anthony
9. Explicit approval request

At the end, ask exactly:

“Anthony, do you approve Phase 1 foundation scaffolding only? This will create the local repository structure, config, domain models, test fixtures, and deterministic skeleton, but will not implement platform collection, network access, LLM calls, applications, or outreach.”
```

## After Claude’s Phase 0 response

Do not approve automatically. Check that it:

- Keeps the project standalone from BADGR Harness.
- Uses the candidate dossier as the qualification truth source.
- Does not expose or request secrets.
- Keeps Wellfound ingestion manual/local only for MVP.
- Preserves hard blockers and explicit unknowns.
- Does not propose auto-apply, scraping, browser automation, or automatic outreach.
- Includes deterministic operation without an LLM.
- Defines a test-first plan.

If it meets those rules, approve Phase 1 with the exact approval it requested. If it does not, correct it before approval.
