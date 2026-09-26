# CareerOps Local — Architecture

CareerOps Local is a local-first, evidence-based job and contract intelligence assistant. It is
decision support. It is not an autonomous hiring agent. It never applies, messages, logs in,
scrapes, or takes any external action.

## Controlling documents

1. `PROJECT_GUARDRAILS.md` — safety, privacy, external actions, compliance.
2. `CANONICAL_CONFLICTS_AND_UNKNOWNS.md` — unresolved facts.
3. `CANONICAL_CANDIDATE_DOSSIER.md` — candidate qualifications.
4. `CANONICAL_BADGR_BUSINESS_CONTEXT.md` — sanitized business and brand context.
5. `CONTEXT_UPDATE_PROTOCOL.md` — update procedure.
6. `JOB_CAPTURE_TEMPLATE.md` — capture fields.
7. `docs/SCORING_DECISIONS.md` — owner-approved implementation decisions. Three dated
   records: Phase 1A (D-1 through D-12), scoring policy P-1 through P-6 (2026-09-25), and
   technology matching policy A-5 through A-7 (2026-09-26).

## Layering

Dependencies point one way only. Each layer is independently testable and knows nothing about
the layer above it.

```
capture file (Markdown / JSON / pasted text)      [Phase 2, not implemented]
        |
        v
  1. Ingestion adapters        preserve raw text and provenance; no network, no browser
        |
        v
  2. Normalization             template fields -> typed model; absent values stay UNKNOWN
        |
        v
  3. Redaction gate            reject or redact secrets and high-risk personal data at import
        |
        v
  4. Assessment (pure)         blockers -> risk flags -> scoring -> classification
        |
        v
  5. Persistence               [Phase 4+, not implemented; gitignored local data directory]
        |
        v
  6. Reporting                 Markdown; facts, risk signals, and unknowns kept separate
        |
        v
  7. Tracker                   records only owner-approved decisions
```

Layer 4 is partially implemented. The type and policy substrate is complete: enums, frozen
domain models, configuration schemas, and pure-function signatures. Within it, exactly one
scoring dimension is implemented — `verified_technical_skill_alignment`, per the approved A-5
allocation and A-6 normalization. Blocker detection, risk-flag detection, compensation
assessment, classification, and full assessment remain signatures that refuse to run.

Layers 1, 2, 3, 5, 6, and 7 do not exist yet, so a capture file cannot currently reach layer 4
through the pipeline. The implemented dimension is reachable only by supplying required
technologies and a candidate term index directly.

## Design invariants

**Assessment is pure.** Assessment functions take `(job, dossier, config)` and return a value.
No I/O, no clock, no randomness. Identical inputs always produce identical output, which makes
every rule table-testable and the result auditable.

**Blockers outrank scoring structurally.** Hard blockers are computed before any score and
cannot be suppressed by one. Nothing downstream can mutate a blocker, so
`PROJECT_GUARDRAILS.md` ("an LLM cannot override hard blockers") holds by construction rather
than by policy.

**The dossier is read-only, and is a copy under test.** `careerops.dossier.loader` declares a
`Protocol` and one implementation that performs no I/O at all: the approved dossier is a
transcription in `careerops.dossier.approved_dossier`. No write path to any canonical file
exists anywhere in the package, so `CONTEXT_UPDATE_PROTOCOL.md` ("never update a canonical file
automatically") is a property of the architecture rather than a policy.

Because the transcription is a second copy of canonical content, it is bound to
`CANONICAL_CANDIDATE_DOSSIER.md` by `tests/parity/test_canonical_dossier_parity.py`. A canonical
edit that is not mirrored fails the build. Deleting or weakening that parity suite reintroduces
drift risk; treat it as load-bearing.

**Unknown is preserved.** Absent listing values remain `UNKNOWN`. No normalization path
converts an unknown into a concrete value, and absence of evidence is never treated as negative
evidence.

**Contact data is unrepresentable.** No domain model has an email, phone, or address field
(D-9). This is enforced by the type system and asserted by a compliance test.

**No external-action surface.** The package declares no HTTP client, browser-automation,
database, or model-provider dependency. Compliance tests fail the build if one appears.

**Matching is deterministic and whole-phrase.** Technology matching compares lookup keys derived
by exactly four steps — Unicode NFC, casefold, whitespace collapse, trim — and nothing else.
There is no token matching, substring matching, fuzzy matching, semantic matching, embedding
matching, LLM matching, or external taxonomy lookup. Spelling and acronym variants are handled
only by explicit owner-approved alias rows, which are one-way and validated at load time.

**Every match is auditable.** A `TechnologyMatch` cannot be constructed without all nine audit
values: the raw job phrase, the normalized job identifier, the raw candidate evidence phrase,
the normalized candidate identifier, the match method, the alias family, the requirement kind,
the evidence tier, and an exact evidence reference. Rule E-5 therefore holds by construction.

**A dimension figure cannot become a verdict.** The implemented dimension returns a
`TechnologyAlignmentResult`, a type carrying no total score, `MatchClassification`,
`Recommendation`, or `ValidationStatus` field. Producing a full `Assessment` requires
`assess_job`, which still calls readiness validation. The gate is enforced by the type system,
not by convention.

**Business mode is a boundary, not a feature.** The dossier loader is an interface with one
intended implementation (personal candidate). A future business-opportunity mode would be a
second implementation behind the same interface. No code merges the two sources (D-2).

## Configuration: two validation stages

1. **Structural validation** parses and type-checks the shipped configuration. It must pass, so
   import, lint, type check, test, and CLI help all work.
2. **Readiness validation** is requested only when full assessment execution is wanted. It
   fails with a clear error while any key in `REQUIRED_UNRESOLVED_POLICY_KEYS` is still the
   `UNRESOLVED` sentinel.

This separation prevents assessment logic from being written before the policy decisions that
govern it are approved.

Eight keys originally gated readiness. Three are resolved: `technology_base_credit_allocation`,
`technology_matching_normalization`, and `required_vs_preferred_technology_handling`, each now a
typed and validated configuration block rather than a sentinel. Five remain, in approved order:

1. `seniority_band_selection_precedence`
2. `compensation_range_selection_rule`
3. `critical_unknown_detection_rule`
4. `score_rounding_rule`
5. `report_and_cli_score_display_scope`

Scores are therefore exact and unrounded wherever they are produced, because rounding is still
key 4.

## Known representational limits

These are recorded rather than worked around, because filling either would mean inventing a
value the owner has not approved.

**Employment technologies are unavailable.** The canonical employment entries state no explicit
technology list, unlike the project entries. Inferring one from responsibility prose would
invent a value, so `EmploymentEvidence.technologies` is empty and Tier 3 technology evidence
cannot currently be matched. Practical effect is small: the technologies named in that prose are
already Tier 1 verified skills, and best tier wins.

**Tier 4 technology evidence is unrepresentable.** `TrainingEvidence` carries no technologies
field, and course titles are never parsed, so the approved Tier 4 multiplier is unreachable.

**Candidate-side compound parsing is deferred.** Compound skill names are transcribed verbatim.
Where a compound must nonetheless be matchable, the owner declares its terms explicitly in
`EXPLICIT_SKILL_TERMS`, which is a declaration and not a parser. Three such entries exist.

**Any-of grouping has no source.** The capture template carries no any-of marker, so each
required entry counts as one slot. A grouped requirement such as "X, Y, or equivalent" is
approved policy as one slot, but cannot yet be expressed as input.

**Six dimensions have no allocation rule.** `role_family_relevance`,
`responsibility_and_project_evidence_alignment`, `location_remote_relocation_compatibility`,
`employment_type_compatibility`, `employer_listing_validation_quality`, and
`growth_learning_relevance` — 55 of the 100 points — have approved weights but no rule for
turning facts into points, and no gate key tracking that fact. A total score is therefore
further away than the five remaining keys suggest.

## Current exclusions

SQLite, SQLAlchemy, Alembic, migrations, persistence, job ingestion, platform adapters,
external-directory reads, network access, browser automation, scraping, login, authentication,
API calls, LLM/Ollama/cloud-provider code, MCP integration, applications, messaging, outreach,
social posting, reports, and any canonical-document modification.

No module reads any file except `config/*.yaml`, asserted by a compliance test. The dossier
package performs no I/O whatsoever.
