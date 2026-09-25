# CareerOps Local — Approved Implementation Decision Record

**Status:** owner-approved implementation decision record
**Date:** 2026-09-25
**Owner:** Anthony Grant
**Scope:** Phase 1A and later implementation work, until superseded by an approved canonical patch

## Standing of this document

- This is an owner-approved implementation decision record dated 2026-09-25.
- It temporarily supersedes **only** the specific conflicting future-implementation policy
  statements in `PROMPT_PHASE_0.md`. No other document is affected.
- It does **not** alter historical source content and does **not** silently mutate canonical
  context. Every canonical Markdown file is unchanged.
- Future canonical-document reconciliation requires a separate approved patch under
  `CONTEXT_UPDATE_PROTOCOL.md`, using the `APPROVE PATCH <ID>` procedure.
- Its scope is limited to Phase 1A and later implementation until superseded by an approved
  canonical patch.

For Phase 1A code and tests, this document is the policy source for: `SalaryCompatibility`
bands and enum names; seniority-and-documented-evidence compatibility terminology;
work-authorization handling; company-verification handling; salary-override deferral;
degree-equivalency handling; and evidence-tier design.

`PROJECT_GUARDRAILS.md` remains the parity source for `RiskFlag`, `Recommendation`, and
`ValidationStatus`.

## D-1 — Founder and business dates

Candidate employment chronology and legal business formation date are separate facts.

- Approved résumé employment record: *Founder & Applied AI Engineer, BADGRTechnologies LLC,
  January 2025–Present*.
- A business formation date is never used for seniority calculation, candidate scoring, or
  résumé claims.
- The exact legal formation/start date remains unresolved under V-001 for future
  business/legal context.

## D-2 — Owner and founder identity

- The candidate dossier employment claim remains usable as approved résumé evidence.
- Business ownership, legal officer identity, equity ownership, and LLC membership are never
  evaluated, exposed, inferred, or modelled.
- V-003 is a business/public-representation concern, not a job-matching blocker.
- No business-ownership field exists in any MVP domain model.

## D-3 — Compensation policy

Configurable future policy. Implemented as configuration in `config/compensation.yaml`;
no scoring logic exists in Phase 1A.

| Base salary (USD) | Classification | Hard blocker |
|---|---|---|
| 90,000 and above | `TARGET_90K_PLUS` | No |
| 80,000 – 85,999 | `FALLBACK_80K_TO_85K` | No |
| 86,000 – 89,999 | `BELOW_PREFERRED_REVIEW` | No |
| Below 80,000 (explicit) | `BELOW_80K` | Yes |
| Contract / hourly | `CONTRACT_REQUIRES_REVIEW` | No |
| Absent | `UNKNOWN` plus `MISSING_COMPENSATION` | No |

Hourly and contract compensation is never annualized and never equated to salary
automatically. A listing is never rejected solely because compensation is absent.

This supersedes the `SalaryCompatibility` member list in `PROMPT_PHASE_0.md`, which named
`FALLBACK_80K_TO_89K` and had no `BELOW_PREFERRED_REVIEW` member.

### Approved SalaryCompatibility enum members

- `TARGET_90K_PLUS`
- `FALLBACK_80K_TO_85K`
- `BELOW_PREFERRED_REVIEW`
- `BELOW_80K`
- `CONTRACT_REQUIRES_REVIEW`
- `UNKNOWN`

### A-2 — Handling of 86,000 – 89,999

- Not a hard blocker.
- Not a salary conflict. No new risk flag is created and `SALARY_CONFLICT` is not reused.
- Negative compensation-score effect when scoring is implemented later.
- Reports must state that the figure is below Anthony's preferred 90,000 base target but above
  the 80,000 exclusion floor.
- Phase 1A records this in `config/compensation.yaml` and here only.

## D-4 — Seniority scoring

The 15-point dimension is named **seniority and documented-evidence compatibility**
(config key `seniority_and_documented_evidence_compatibility`).

- Total years of experience is never calculated.
- Experience years are never inferred from job dates.
- No overall years-of-experience field exists on any candidate model, and no date-arithmetic
  helper exists in the source package.
- Evaluation inputs: title level, stated years requirement, leadership/architecture/research
  scope, role responsibilities, verified projects/skills/employment evidence, and
  equivalent-experience language.
- A role requiring 5+ years is not automatically blocked solely because total years are unknown.
- Normally a concern or partial match, unless the role is clearly senior/staff/principal/lead
  or requires materially unsupported scope.

## D-5 — Work authorization

Candidate work authorization remains `UNKNOWN` in tracked canonical project data.

When a listing states a specific authorization, citizenship, visa, or location-eligibility
condition:

- Add `WORK_AUTHORIZATION_RESTRICTION`.
- Mark the assessment `INSUFFICIENT_EVIDENCE`.
- Recommend `RESEARCH_COMPANY_FIRST` or `HOLD_FOR_MISSING_COMPENSATION_OR_LOCATION` only when
  it must be resolved before applying.
- Never hard-block on a candidate `UNKNOWN`.
- A hard blocker may exist only if a future approved private local profile contains a confirmed
  conflicting fact.
- No work-authorization value is created, requested, or stored in tracked files.

## D-6 — Company verification

Plain absence of an official website, careers page, or external company evidence is not a hard
blocker.

- Missing or incomplete company evidence: `MISSING_COMPANY_WEBSITE` and/or
  `UNVERIFIABLE_COMPANY`, plus `RESEARCH_COMPANY_FIRST`.
- `DO_NOT_APPLY` only for affirmative fraud, identity contradiction, a suspicious
  payment/identity-document scenario, or an employer that remains non-credible after explicitly
  approved research.
- The difference between missing evidence and negative evidence is preserved.

## D-7 — Technology evidence tiers

A technology demonstrated in a verified project counts as candidate evidence, but is not
automatically equivalent to broad professional production experience.

### Approved EvidenceTier enum members

- `TIER_1_VERIFIED_SKILL`
- `TIER_2_PROJECT_EVIDENCE`
- `TIER_3_EMPLOYMENT_EVIDENCE`
- `TIER_4_TRAINING`

Tier 1 is the explicit verified skills list; Tier 2 verified project technologies and work;
Tier 3 verified employment technologies and responsibilities; Tier 4 training and coursework.

Reports must disclose which tier produced every technology match. No tier may create an
unverified skill. Tier weighting is `UNRESOLVED` (see A-4).

## D-8 — Degree equivalency

Owner-reviewable phrase list, stored in `config/blockers.yaml`:

- or equivalent experience
- or equivalent practical experience
- or equivalent professional experience
- or equivalent work experience
- or related experience
- equivalent combination of education and experience
- education or equivalent experience
- degree preferred
- bachelor's preferred
- or demonstrable experience

Rules:

- Explicit mandatory degree with no recognized equivalent phrase: degree hard blocker.
- Explicit degree with a recognized equivalent phrase: no degree hard blocker; the degree may
  remain a non-blocking concern.
- Degree preferred: no hard blocker.
- Ambiguous degree wording: `INSUFFICIENT_EVIDENCE` and `RESEARCH_COMPANY_FIRST`; never a
  hard block.

## D-9 — Contact details

Professional email and phone remain in the candidate dossier for now. No canonical-document
update is approved.

Matching, scoring, persistence, logs, and reports must not read, score, persist, or display
contact details. Phase 1A enforces this in the type system: no contact field exists on any
domain model. A future repository-hardening pass may move contact details to an ignored local
profile.

## D-10 — Salary override

No below-80,000 override feature in Phase 1A. Explicit base salary below 80,000 remains a hard
blocker. The override data model, configuration, CLI, storage, and logic are deferred to a
later, separately approved phase. `config/blockers.yaml` contains no override key.

## D-11 — README filename typo

`README.md` refers to `CANONICAL_CONFLICTS_AND_UNKNOWNs.md`; the actual file is
`CANONICAL_CONFLICTS_AND_UNKNOWNS.md`. Acknowledged, not modified. Correction requires a future
approved patch.

## D-12 — Local data

When persistence is later approved, the SQLite database, raw captures, generated reports, logs,
and any local profile live under a gitignored local data directory. Only synthetic fixtures may
be committed. Real job captures, résumé files, personal exports, business/legal records, and
generated reports are never committed.

## A-1 — Canonical policy divergence

Owner decisions recorded in this document are the controlling policy for Phase 1A, including
where they intentionally supersede older wording in `PROMPT_PHASE_0.md`. No canonical Markdown
file is modified in Phase 1A.

Parity tests do not parse line numbers from Markdown. They parse stable labelled Markdown
sections, or compare against a code-owned expected list documented as derived from
`PROJECT_GUARDRAILS.md`. Tests fail if `RiskFlag`, `Recommendation`, or `ValidationStatus`
drifts from the approved guardrails list.

## A-3 — Match classification thresholds

> **Resolved on 2026-09-25 by P-2 in the owner-decision record below.** The text that
> follows is retained as historical context describing the Phase 1A position.

`UNRESOLVED`. No score cutoffs are invented and no classification behaviour is implemented.
Structural configuration parsing succeeds; readiness validation for full assessment execution
fails with a clear error naming the unresolved key. Package import and CLI help remain
functional.

## A-4 — Evidence-tier weighting

> **Resolved on 2026-09-25 by P-1 in the owner-decision record below.** The text that
> follows is retained as historical context describing the Phase 1A position.

`UNRESOLVED`. No numeric tier weights are invented and no scoring behaviour is implemented. The
`EvidenceTier` enum exists and the tier field is required on technology-match domain models.
Reports are not implemented in Phase 1A. Full assessment configuration fails clearly until tier
weights are approved.

## Unresolved policy keys as of this record

> **Superseded on 2026-09-25 by the owner-decision record below.** Both keys
> listed here are now resolved (P-1 and P-2). The active gate is the eight-key set in
> "Unresolved policy keys" within that record. This table is retained as historical
> context and no longer governs readiness validation.

| Key | Location | Gate | Status |
|---|---|---|---|
| `match_classification_thresholds` | `config/scoring.yaml` | A-3 | Resolved by P-2 |
| `evidence_tier_weighting` | `config/scoring.yaml` | A-4 | Resolved by P-1 |

---

# Owner-Decision Record — Scoring Policy P-1 through P-6

**Status:** approved
**Date:** 2026-09-25
**Owner:** Anthony Grant

## Standing of this record

This record resolves the prior **A-3** (`match_classification_thresholds`) and **A-4**
(`evidence_tier_weighting`) policy decisions, and adds **P-3 through P-6**.

It **does not supersede or modify any canonical Markdown file.** `PROJECT_GUARDRAILS.md`,
`PROMPT_PHASE_0.md`, `README.md`, `JOB_CAPTURE_TEMPLATE.md`, `CONTEXT_UPDATE_PROTOCOL.md`,
`CANONICAL_CANDIDATE_DOSSIER.md`, `CANONICAL_BADGR_BUSINESS_CONTEXT.md`, and
`CANONICAL_CONFLICTS_AND_UNKNOWNS.md` are unchanged.
No canonical Markdown source is changed or superseded by this record.
Future canonical reconciliation requires a separate approved patch under
`CONTEXT_UPDATE_PROTOCOL.md`.

This record is the **active implementation authority** for P-1 through P-6 and for the
unresolved-key gate. The Phase 1A standing section earlier in this file is retained as
historical context; it is labelled superseded only where this record explicitly governs.

Resolving A-3 and A-4 **does not unblock assessment implementation.** Eight new policy keys
now gate readiness (see "Unresolved policy keys" below). No scoring, blocker detection,
classification, report rendering, ingestion, persistence, or external behaviour may be
implemented or executed while any of those keys remains unresolved.

## P-1 — Evidence-tier weighting (resolves A-4)

### Approved evidence-tier multipliers

- TIER_1_VERIFIED_SKILL: 1.00
- TIER_2_PROJECT_EVIDENCE: 0.70
- TIER_3_EMPLOYMENT_EVIDENCE: 0.90
- TIER_4_TRAINING: 0.30

Rules E-1 through E-8, adopted in full:

- **E-1** Multipliers apply only within `verified_technical_skill_alignment`, capped at 20 points.
- **E-2** No double counting between technology credit and
  `responsibility_and_project_evidence_alignment`, which scores responsibilities, scope, and
  outcomes rather than technology tokens.
- **E-3** Best tier wins. A technology scores once, at its strongest approved evidence tier.
- **E-4** No evidence gives zero technology credit, plus `REQUIRED_SKILL_GAP` when the listing
  marks the technology required.
- **E-5** Every technology match must disclose its evidence tier and its exact supporting
  evidence reference.
- **E-6** A Tier 3 match can never satisfy a prohibited-inference requirement.
- **E-7** A required technology supported only by Tier 2 or Tier 4 raises `REQUIRED_SKILL_GAP`.
- **E-8** Tier ordinal does not imply weight order. Tier 3 outranks Tier 2 under this policy.

## P-2 — Match classification thresholds (resolves A-3)

### Approved classification thresholds

- STRONG_MATCH: 72-100
- PLAUSIBLE_MATCH: 58-71
- STRETCH: 42-57
- AVOID: 0-41

Applied globally to all role families initially. `INSUFFICIENT_EVIDENCE` has no score band; it
is reachable only through rule C-4.

Rules C-1 through C-6, adopted in full:

- **C-1** Any hard blocker forces `DO_NOT_APPLY` regardless of score.
- **C-2** Unknown dimensions score zero and remain in the denominator.
- **C-3** Missing evidence alone never produces `AVOID` or `DO_NOT_APPLY`.
- **C-4** Three or more critical unknowns — among compensation, work arrangement,
  company/careers verification, education requirements, and required technologies — cap
  classification at `INSUFFICIENT_EVIDENCE` regardless of score.
- **C-5** Score is never a headline. It appears only after blockers, flags, unknowns, and the
  per-dimension breakdown.
- **C-6** Global thresholds are reconsidered only after 30-50 assessed listings and a
  documented human calibration review.

## P-3 — Seniority and documented-evidence compatibility (15 points)

### Approved seniority point bands

- 15: Intermediate / Engineer I-II / associate role; responsibilities strongly match documented evidence; no unsupported leadership or research scope.
- 11: Mid-level role with one moderate gap, including stated 3+ years where actual scope remains practical and applied.
- 7: Broad or unclear role, or multiple moderate evidence gaps.
- 3: Explicit 5+ years or senior-style scope, without enough evidence to establish the hard blocker.
- 0: Materially unsupported senior/staff/principal/lead/research scope; then evaluate the separate P-5 blocker.

Binding prohibitions, restating D-4: never calculate total years of experience; never infer
years from employment dates; never add aggregate years-of-experience to candidate models or
reports.

## P-4 — Compensation compatibility (10 points)

### Approved compensation point mapping

- TARGET_90K_PLUS: 10
- BELOW_PREFERRED_REVIEW: 7
- FALLBACK_80K_TO_85K: 5
- CONTRACT_REQUIRES_REVIEW: 0
- UNKNOWN: 0
- BELOW_80K: 0

`BELOW_PREFERRED_REVIEW` covers $86,000-$89,999 and `FALLBACK_80K_TO_85K` covers
$80,000-$85,999. Contract and hourly compensation is never annualized and requires manual
review. `UNKNOWN` additionally raises `MISSING_COMPENSATION`; a listing is never rejected
solely because compensation is absent. `BELOW_80K` retains its existing hard blocker.

## P-5 — SENIOR_SCOPE_MATERIALLY_UNSUPPORTED

### Approved senior-scope firing conditions

- requires_explicit_senior_scope: true
- minimum_unsupported_requirements: 2
- category: leadership_or_ownership
- category: five_plus_years_required
- category: mlops_cloud_or_platform_ownership
- category: kubernetes_terraform_docker_core
- category: research_training_or_publications
- category: unsupported_scale_or_ownership_claims
- category: clearance_or_independent_blocker

The blocker fires only when both conditions hold: the role is explicitly Senior, Staff,
Principal, Lead, Head, or equivalent senior scope; **and** it contains at least two materially
unsupported requirements drawn from the categories above. A senior title alone remains a
`SENIORITY_MISMATCH` concern, not an automatic hard blocker.

### Cross-reference: P-3 and P-5 are not equivalent

P-3's 0-point seniority band and P-5's hard blocker are not equivalent. A role may score 0 for
seniority without firing a blocker, because the blocker additionally requires an explicit
senior scope plus at least two enumerated materially unsupported requirements. No
implementation may couple the two.

## P-6 — Score display

### Approved report display order

1. Recommendation
2. Hard blockers
3. Validation status and risk flags
4. Critical unknowns / missing evidence
5. Match classification and score
6. Per-dimension score breakdown
7. Evidence-tier map with candidate-proof references
8. Human next action

The score must never appear alone in a report title, filename, alert label, sort label, or
first sentence.

## Unresolved policy keys

These eight keys gate assessment readiness. Structural configuration loading succeeds; full
readiness validation fails and lists every key below, in this order.

1. technology_base_credit_allocation
2. technology_matching_normalization
3. required_vs_preferred_technology_handling
4. seniority_band_selection_precedence
5. compensation_range_selection_rule
6. critical_unknown_detection_rule
7. score_rounding_rule
8. report_and_cli_score_display_scope

No deterministic assessment behaviour may be added or executed while any key above remains
unresolved. No value may be invented.
