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
gated readiness as of this record; three were later resolved by the 2026-09-26 A-5 through A-7
record, leaving the five listed under "Unresolved policy keys" below. No scoring, blocker
detection, classification, report rendering, ingestion, persistence, or external behaviour may
be implemented or executed while any of those keys remains unresolved.

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

> **Superseded twice.** Reduced on 2026-09-26 by the technology-matching record below, then
> superseded again the same day by the dimension-allocation record, which added six
> allocation-rule keys.
> The active gate is the eleven-key set in "Gate keys after the dimension-allocation decision".
> This list is retained as historical context.
>
> **Reduced on 2026-09-26 by the owner-decision record below.** Three of the original eight
> keys are now resolved: `technology_base_credit_allocation` (A-5),
> `technology_matching_normalization` (A-6), and
> `required_vs_preferred_technology_handling` (A-7). The active gate is the five-key set in
> "Remaining unresolved policy keys after A-5 through A-7" within that record, and the list
> below has been reduced to match it.

These five keys gate assessment readiness. Structural configuration loading succeeds; full
readiness validation fails and lists every key below, in this order.

1. seniority_band_selection_precedence
2. compensation_range_selection_rule
3. critical_unknown_detection_rule
4. score_rounding_rule
5. report_and_cli_score_display_scope

No deterministic assessment behaviour may be added or executed while any key above remains
unresolved. No value may be invented.

---

# Owner-Decision Record — Technology Matching Policy A-5 through A-7

**Status:** approved
**Date:** 2026-09-26
**Owner:** Anthony Grant

## Standing of this record (A-5 through A-7)

This record resolves the first three gate keys listed in the P-1 through P-6 owner-decision
record: `technology_base_credit_allocation` (A-5), `technology_matching_normalization` (A-6),
and `required_vs_preferred_technology_handling` (A-7).

It **does not supersede or modify any canonical Markdown file.** `PROJECT_GUARDRAILS.md`,
`PROMPT_PHASE_0.md`, `README.md`, `JOB_CAPTURE_TEMPLATE.md`, `CONTEXT_UPDATE_PROTOCOL.md`,
`CANONICAL_CANDIDATE_DOSSIER.md`, `CANONICAL_BADGR_BUSINESS_CONTEXT.md`, and
`CANONICAL_CONFLICTS_AND_UNKNOWNS.md` are unchanged.
No canonical Markdown source is changed or superseded by this record.
Future canonical reconciliation requires a separate approved patch under
`CONTEXT_UPDATE_PROTOCOL.md`.

This record is the **active implementation authority** for A-5 through A-7 and for the
remaining-key gate. The Phase 1A standing section is retained as historical context. The
P-1 through P-6 record remains the active authority for P-1 through P-6; only its
unresolved-key section is superseded, and it is labelled accordingly.

Resolving A-5 through A-7 **does not unblock assessment implementation.** Five policy keys
continue to gate readiness. No scoring, blocker detection, classification, report rendering,
ingestion, persistence, or external behaviour may be implemented or executed while any of
those keys remains unresolved. No assessment behaviour is authorized by this record.

No rounding rule is established here; rounding remains `score_rounding_rule`. No general
critical-unknown rule is established here; A-7 defines only when the required-technologies
input counts as unknown. No new `RiskFlag` or `BlockerCode` member is created; both sets
remain parity-locked to `PROJECT_GUARDRAILS.md`.

## A-5 — Technology base credit allocation

Approved approach: required-only conservative allocation.

### Approved allocation formula

Let `R` be the set of required technology slots, with `n = |R|`. Let `m(r)` be the best-tier
multiplier for slot `r`, drawn from the approved P-1 multiplier table, and equal to `0.00`
where no evidence exists.

    points = 20 × ( sum of required-slot best-tier multipliers ) / n     when n >= 1
    points = 0                                                          when n = 0

Required slots are determined only after approved normalization, any-of grouping, and
deduplication.

Preferred technologies never enter the numerator or the denominator.

The score remains exact and unrounded until `score_rounding_rule` is separately resolved.

### Approved required-slot credit and gap rules

- A required technology with no evidence receives 0 and raises `REQUIRED_SKILL_GAP`.
- A required technology supported only by Tier 2 or Tier 4 receives partial credit and raises
  `REQUIRED_SKILL_GAP`. Credit and flags are decoupled: partial credit never suppresses the
  gap.
- A Tier 3 technology receives its approved multiplier unless it would require a prohibited
  inference.
- Best tier wins: a slot's multiplier is the maximum over every matching evidence tier.
- Zero required technologies yields 0 of 20, but that fact alone never produces `AVOID` or
  `DO_NOT_APPLY`.
- Long required lists dilute credit proportionally; no extra penalty is added.

### Approved score-eligibility rule

Only structured technology fields are eligible for the technology-score numerator and
denominator. Raw listing prose is never token-scanned for score.

## A-6 — Technology matching normalization

Approved approach: controlled alias families with review queue.

### Approved normalization mechanics

Lookup keys are normalized using only Unicode NFC normalization, casefolding, whitespace
collapse, and trim.

There is no automatic punctuation stripping, version stripping, acronym expansion, token
matching, substring matching, fuzzy matching, semantic matching, embedding matching, LLM
matching, external taxonomy lookup, or API lookup.

Alias matching is whole-phrase only. Alias rows are one-way: variant to canonical identifier.
Unknown aliases never auto-match.

No bare two-letter acronym becomes an alias.

### Approved scope of alias application

Aliases apply only to future structured technology fields and to explicitly represented
candidate evidence terms.

**Candidate-side compound and parenthetical parsing is deferred.** This record does not
normalize, and does not claim to normalize, any compound or parenthetical candidate phrase.
Parsing of the following is explicitly deferred and must not be implemented:

- `Model Context Protocol (MCP)`
- `JavaScript/TypeScript`
- `Ubuntu/Linux`
- `Windows 10/11`
- course titles, for Tier 4 evidence

Consequently, a canonical identifier below becomes reachable on the candidate side only once
that technology exists as an explicitly represented candidate evidence term. Until then a
matching job requirement finds no evidence and is handled by the A-5 no-evidence rule. No
inference fills that gap.

### Approved prohibited-inference protection

A canonical alias target is **not** rejected merely because that technology is currently
absent from candidate evidence. A canonical identifier may exist for a technology the dossier
does not contain; a job requirement normalizing to it simply finds no evidence, receives 0,
and raises `REQUIRED_SKILL_GAP`.

Instead, any alias that attempts to create unsupported candidate evidence from a broader
category, related technology, capability phrase, or implication is rejected. A broader
category, adjacent technology, protocol/implementation distinction, capability phrase,
hierarchy, or implication may not be converted into a target technology through an alias.

A future approved candidate-evidence update may directly add a technology currently absent
from the dossier without changing the alias framework.

This protection is a human judgment applied when approving each alias family. It is not a
load-time check, and no automated validator is claimed to enforce it.

### Approved canonical identifiers and display names

Canonical identifiers are internal, stable, uppercase-snake, one display name each.
Human-facing output uses the approved display name; an identifier is never displayed alone.

| Canonical identifier | Display name |
|---|---|
| `REACT` | React |
| `REST_APIS` | REST APIs |
| `MCP` | MCP |
| `RAG` | RAG |
| `CHROMADB` | ChromaDB |
| `BM25` | BM25 |
| `PYTHON` | Python |
| `SQLITE` | SQLite |
| `BASH` | Bash |

Nine canonical identifiers. `CRON` is not added in this record.

### Approved alias registry

Nine alias families, fifteen variant lookup keys, nine canonical identifiers. Matching is
exact and whole-phrase.

| Canonical identifier | Variant lookup keys |
|---|---|
| `REACT` | `react.js`, `reactjs` |
| `REST_APIS` | `rest api`, `rest apis`, `restful api`, `restful apis` |
| `MCP` | `model context protocol` |
| `RAG` | `retrieval-augmented generation`, `retrieval augmented generation` |
| `CHROMADB` | `chroma` |
| `BM25` | `okapi bm25` |
| `PYTHON` | `python 3`, `python3` |
| `SQLITE` | `sqlite3` |
| `BASH` | `bash shell` |

Every alias family requires an approval date and a short owner-approved defense statement.

### Explicitly deferred aliases

- `crontab -> CRON`
- `openssh -> SSH`
- `JS/TS`
- `javascript/typescript`
- bare `js`
- bare `ts`
- `react native -> React`
- `ubuntu -> Linux`
- `vector database -> ChromaDB`
- `RAG -> LangChain`
- `MCP -> Azure OpenAI`
- any broad category, related technology, capability phrase, hierarchy, implication,
  protocol/implementation pair, fuzzy match, semantic match, embedding match, LLM match, or
  external taxonomy or API lookup

### Approved unknown required-term rule

An unrecognized required technology phrase remains a required slot. It receives zero credit.
It stays in the denominator. It raises `REQUIRED_SKILL_GAP`. It may appear in a future
owner-review report section. It is never removed from the denominator and never silently
ignored.

Worked example. Required: Weaviate, Python. Evidence: Python only.

    20 × (0.00 + 1.00) / 2 = 10.00

before rounding. `REQUIRED_SKILL_GAP` applies to Weaviate.

Unknown terms never change score automatically, and no persistent queue is added now. Listing
a term for owner review changes nothing about the outcome above. A later approved alias
affects future assessments only; it never retroactively rewrites a completed assessment.

### Approved audit and provenance retention

A future audit model must retain: raw job phrase; normalized job identifier; raw candidate
evidence phrase; normalized candidate identifier; match method; alias family identifier;
requirement kind; evidence tier; evidence reference.

Evidence references cite a dossier section label, never a line number.

### Approved compound-slot policy for JS/TS

- `JS/TS` is an ALL-OF compound requirement meaning JavaScript AND TypeScript.
- It is not an alias-registry row.
- Its slot multiplier is the minimum multiplier among its component technologies.
- If a component lacks evidence, the missing component receives zero treatment and
  `REQUIRED_SKILL_GAP` is raised.
- The compound-slot schema is deferred. This behaviour must not be implemented; it is
  recorded as a policy decision requiring a future compound-slot schema.

## A-7 — Required versus preferred technology handling

Approved approach: required-primary with preferred informational only.

### Approved required and preferred treatment

- Required technologies are the only input to the 20-point technical-alignment dimension.
- Preferred technologies have no score, classification, recommendation, or flag effect.
- Preferred technologies never raise `REQUIRED_SKILL_GAP`.
- A future report must show a preferred-evidence map, including matched tier and evidence,
  and explicit no-evidence entries.
- Preferred alignment may influence only the narrative wording of Human next action, never
  any score or enum outcome.
- A listing with no explicit required technologies scores 0 in the technical-alignment
  dimension.
- Required technologies count as a critical unknown only when a structured requirement field
  exists but yields no explicit technology. Broader critical-unknown behaviour remains
  unresolved under `critical_unknown_detection_rule`.
- A listing with only preferred technologies scores 0 in this dimension but still receives a
  future preferred-evidence map.
- "X, Y, or equivalent" is one any-of slot. Only explicitly named X or Y may satisfy it;
  "equivalent" never invents a new technology.
- Generic wording such as "modern AI tooling", "familiarity with cloud", or "strong technical
  background" never becomes a technology slot.

Preferred-technology extraction, its schema, and any capture-template change remain deferred.

## Remaining unresolved policy keys after A-5 through A-7

> **Superseded on 2026-09-26 by the dimension-allocation record below,** which added six
> allocation-rule keys. These five remain unresolved and are still part of the active gate;
> they are no longer the whole of it.
> The active gate is the eleven-key set in "Gate keys after the dimension-allocation decision".

These five keys gate assessment readiness. Structural configuration loading succeeds; full
readiness validation fails and lists every key below, in this order.

1. seniority_band_selection_precedence
2. compensation_range_selection_rule
3. critical_unknown_detection_rule
4. score_rounding_rule
5. report_and_cli_score_display_scope

No deterministic assessment behaviour may be added or executed while any key above remains
unresolved. No value may be invented.

---

# Owner-Decision Record — Dimension Allocation Gate

**Status:** approved
**Date:** 2026-09-26
**Owner:** Anthony Grant

## Standing of this record (dimension-allocation gate)

This record adds six policy keys to the readiness gate and establishes a three-state policy
mechanism. It resolves nothing. It makes already-missing work visible.

It **does not supersede or modify any canonical Markdown file.** `PROJECT_GUARDRAILS.md`,
`PROMPT_PHASE_0.md`, `JOB_CAPTURE_TEMPLATE.md`, `CONTEXT_UPDATE_PROTOCOL.md`,
`CANONICAL_CANDIDATE_DOSSIER.md`, `CANONICAL_BADGR_BUSINESS_CONTEXT.md`, and
`CANONICAL_CONFLICTS_AND_UNKNOWNS.md` are unchanged. `README.md` was separately corrected under
approved canonical patch `D-11-README`; that patch is unrelated to this record.

This record is the **active implementation authority** for the readiness gate. The earlier gate
sections in this file are labelled superseded.

## The gap this record records

Nine weighted dimensions total 100 points. Two carry approved allocation rules: technology
alignment (P-1, A-5, A-6, A-7) and, in part, compensation and seniority, whose point tables are
approved (P-3, P-4) while their selection rules remain unresolved.

Six dimensions carry an approved **weight** and no rule at all for turning facts into points:

| Dimension | Points |
|---|---|
| role_family_relevance | 20 |
| responsibility_and_project_evidence_alignment | 15 |
| location_remote_relocation_compatibility | 8 |
| employment_type_compatibility | 5 |
| employer_listing_validation_quality | 4 |
| growth_learning_relevance | 3 |

That is **55 of the 100 points**, and none of it was tracked by any gate key. A total score was
therefore further away than the previously listed five keys implied. `PROMPT_PHASE_0.md` calls
these "suggested score weights"; a weight is not an allocation rule.

## Approved policy states

Every policy decision holds exactly one of three states, represented by the `PolicyStatus` enum:

1. `UNRESOLVED` — no rule exists. The key appears in `unresolved_policy`, where the UNRESOLVED
   sentinel is the only permitted value.
2. `PROVISIONAL` — a rule exists and the owner approved it as a working default, knowing it will
   be revisited. A provisional rule must be labelled provisional wherever its result is
   displayed.
3. `APPROVED` — the owner settled it.

There is deliberately no state for a derived, inferred, or defaulted rule. A rule is
owner-approved or it does not exist.

## Approved gate-integrity rule

A key is **not** resolved by changing its value in `unresolved_policy`. It is resolved by
removing it from that block and from `REQUIRED_UNRESOLVED_POLICY_KEYS` together, and adding a
typed policy block that carries its own status. Configuration validation rejects any value in
`unresolved_policy` other than the UNRESOLVED sentinel, so a key cannot be silently released by
writing "approved" or a typo over it.

## Gate keys after the dimension-allocation decision

These eleven keys gate assessment readiness. Structural configuration loading succeeds; full
readiness validation fails and lists every key below, in this order.

1. seniority_band_selection_precedence
2. compensation_range_selection_rule
3. critical_unknown_detection_rule
4. score_rounding_rule
5. report_and_cli_score_display_scope
6. role_family_allocation_rule
7. responsibility_evidence_allocation_rule
8. location_remote_relocation_allocation_rule
9. employment_type_allocation_rule
10. growth_learning_allocation_rule
11. employer_listing_validation_allocation_rule

No deterministic assessment behaviour may be added or executed while any key above remains
unresolved. No value may be invented.

## Approved consequence for classification

Two dimensions have no deterministic input at all. `responsibility_and_project_evidence_alignment`
can be scored only from prose, and every deterministic proxy either double-counts technologies
(E-2) or requires semantic matching, which A-6 forbids. `growth_learning_relevance` has no
capture-template field whatsoever.

Under rule C-2 an unevaluated dimension scores zero and stays in the denominator, so while those
two are unevaluated the highest achievable total is **82 of 100**. The P-2 thresholds were set
assuming all nine dimensions are evaluated, and `STRONG_MATCH` begins at 72.

Therefore, while any dimension is unevaluated:
no `MatchClassification` is produced or displayed.
A partial total may be reported only as a count of evaluable points, stating the ceiling. Thresholds are re-derived once the missing dimensions carry rules, consistent with rule
C-6, which requires 30 to 50 assessed listings before reconsidering them.

---

# Owner-Decision Record — Technology Categories and Soft Salary Floor

**Status:** approved
**Date:** 2026-09-26
**Owner:** Anthony Grant

## Standing of this record (categories and soft floor)

This record adds a technology-category lane and makes the salary floor soft. It changes no gate
key and resolves none.

It **does not supersede or modify any canonical Markdown file.** `PROJECT_GUARDRAILS.md`,
`PROMPT_PHASE_0.md`, `JOB_CAPTURE_TEMPLATE.md`, `CONTEXT_UPDATE_PROTOCOL.md`,
`CANONICAL_CANDIDATE_DOSSIER.md`, `CANONICAL_BADGR_BUSINESS_CONTEXT.md`, and
`CANONICAL_CONFLICTS_AND_UNKNOWNS.md` are unchanged.

It **does** amend two earlier decisions in this file, named explicitly below, because the
configuration now contradicts them and a record that contradicts the running system is worse than
no record.

## Approved technology categories

A-6 forbids aliasing an adjacent technology, a broader category, or a capability phrase to a
target technology. That prohibition stands: no alias row may do any of those things, and an
alias still means "the same technology under another name".

Category substitution is a separate mechanism and is not an alias. One boolean governs it:

- **substitutable** — operating one member transfers to another. An employee-facing CRM or
  ticketing system exists to get customer information to someone who can act on it; having run
  one, a person can run another. A requirement met by a peer earns **reduced** credit, and the
  match records the tool actually held, never the one requested. The gap is raised as well, so
  reduced credit can never be read as the requested tool.
- **non-substitutable** — membership transfers nothing. General-purpose programming languages are
  market-standard and not interchangeable: a language-specific role requires that language, and
  it cannot be learned in time for the application. A peer earns nothing and raises
  `CORE_LANGUAGE_GAP`, which is a stronger and more useful statement than mere absence.

Approved credit, three values only: direct 1.00, substitute 0.50, none 0.00.

Category membership is job-side recognition, not candidate evidence. Credit still requires the
candidate to hold a member, recorded in the approved dossier, at a disclosed tier. Listing a
product name in a category grants nothing.

### Amendment to A-6

A-6's forbidden-alias list is unchanged and remains binding for aliases. Substitution is added
alongside it as a distinct match method, `CATEGORY_SUBSTITUTE`, which earns partial credit and
always discloses both the substitution and the gap. It never claims the requested technology and
never suppresses a gap.

## Approved soft salary floor

### Amendment to D-3 and D-10

D-3 made an explicit base salary below 80,000 a hard blocker, and D-10 deferred any override
mechanism. Both are amended: **there is no hard salary blocker.**

A stated minimum is a preference, not a law. A listing a few thousand below it can still be a
good opportunity, and that judgement belongs to a human. A listing below the floor scores zero in
the compensation dimension and is reported with its shortfall. It is never dropped.

`BlockerCode.EXPLICIT_BASE_SALARY_BELOW_80K` is **disabled, not removed**: the blocker set is
parity-locked to `PROJECT_GUARDRAILS.md`, so the code remains defined and unused.

### Approved salary targets

Three figures, none of which blocks anything:

- hard floor 70,000
- soft minimum 85,000
- market target 120,000

85,000 is the owner's stated figure. 70,000 and 120,000 were proposed by the assistant and
approved by the owner on 2026-09-26. The market target is anchored to published wage statistics
rather than to preference, because a listing can clear a personal floor and still underpay for
the work.

Every market figure requires a source and an as-of date. Configuration loading rejects a figure
without them: an uncited number about pay is a guess, and a guess about pay is worse than no
number.

### Approved cost-of-living treatment

Regional price parity is applied **only** when a listing could require relocation. For a remote
role the candidate remains in Georgia, earns the listing's salary, and spends at Georgia prices,
so the listed figure stands. Adjusting a remote salary downward would penalise the strongest
offers, and configuration that would do so is rejected.

A state is recognized only in the standard "City, ST" position, against an individually verified
parity. An unlisted or ambiguous location yields no adjustment rather than an estimate.

## Canonical reconciliation still outstanding

`CANONICAL_CANDIDATE_DOSSIER.md` still records a 90,000 preference and an 80,000 general
exclusion, and records no CRM or ticketing tool. Both are open in `docs/VALIDATION_QUEUE.md` as
VQ-003 and VQ-004. Until those are approved, the configuration is the operating rule and the
dossier is stale on those two points.
