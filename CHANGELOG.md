# Changelog

All notable changes to CareerOps Local are recorded here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

CareerOps Local is decision support. It never applies, messages, logs in, scrapes, or takes any
external action. Every release below preserves that boundary.

Policy changes are owner decisions recorded in `docs/SCORING_DECISIONS.md` and are cited by
their decision identifiers. No release may invent a policy value.

## [Unreleased]

### Added

- **Local operator runner** — `python -m careerops.tools.technology_alignment` reads one
  required technology per line from standard input and prints the
  `verified_technical_skill_alignment` dimension: provenance, the evidence-tier map, gaps, then
  points last. Deliberately not a CLI command, so `report_and_cli_score_display_scope` stays
  unresolved and the Typer CLI stays `doctor`-only. Writes no file, parses no capture file, and
  prints no classification, recommendation, or total.
- **`docs/VALIDATION_QUEUE.md`** — owner-supplied information that conflicts with an approved
  canonical document, recorded rather than applied, per `CONTEXT_UPDATE_PROTOCOL.md`. First
  entry: VQ-001, Kubernetes use during UVeye employment, which the dossier currently lists as a
  prohibited inference.

### Fixed

- `TechnologyMatch.technology` reported the listing's own spelling instead of the approved
  display name, so a listing asking for "React.js" displayed "React.js" rather than "React".
  No test asserted that field. Shipped in 0.2.0a0; now corrected with regression coverage
  across all nine alias families.
- `README.md` referenced `CANONICAL_CONFLICTS_AND_UNKNOWNs.md`; the actual filename ends in
  `UNKNOWNS.md`. Recorded as decision D-11 and deferred since Phase 0; corrected under approved
  canonical patch `D-11-README`, which also adds a current-state section and retains all
  original starter-pack text.

## [0.2.0a0] — 2026-09-26

First release in which the system computes anything. One of nine scoring dimensions is
implemented; a total match score remains unavailable by design.

### Readiness

The readiness gate falls from eight unresolved policy keys to **five**.
`load_ready_assessment_config()` still refuses, and full assessment, blocker detection,
risk-flag detection, classification, and reporting all remain unavailable. Five keys remain, in
approved order: `seniority_band_selection_precedence`, `compensation_range_selection_rule`,
`critical_unknown_detection_rule`, `score_rounding_rule`, `report_and_cli_score_display_scope`.

### Added

- **Technology matching policy A-5 through A-7**, approved 2026-09-26. Required-only
  conservative credit allocation; controlled alias families with an owner-review surface;
  required-primary scoring with preferred technologies informational only. Each is now a typed,
  validated configuration block rather than an `UNRESOLVED` sentinel.
- **Alias registry** — nine owner-approved families, fifteen variant lookup keys, nine canonical
  identifiers, each family carrying an approval date and a defense statement. Twelve alias
  mappings are explicitly deferred and rejected at load time.
- **`verified_technical_skill_alignment` scoring** — `score_technology_alignment()` implements
  the approved formula, `points = 20 × (sum of required-slot best-tier multipliers) ÷ required
  slots`, and `0` when a listing names none. Results are exact and unrounded, because rounding
  remains an unresolved key.
- **Deterministic technology matching** — `match_technologies()` compares whole-phrase lookup
  keys derived by exactly four steps: Unicode NFC, casefold, whitespace collapse, trim. No
  token, substring, fuzzy, semantic, embedding, LLM, or external-taxonomy matching exists.
- **Full audit trail per match** — `TechnologyMatch` requires all nine values rule E-5 implies,
  so an undisclosed match cannot be constructed. `TechnologyGap` records an unsatisfied required
  slot and its reason, distinguishing no evidence, an unrecognized term, and partial credit that
  still raises a gap.
- **`TechnologyAlignmentResult`** — a dimension-result type carrying no total score,
  classification, recommendation, or validation status, so a dimension figure cannot become a
  verdict while the gate stands.
- **Canonical dossier transcription** — a machine-readable copy of
  `CANONICAL_CANDIDATE_DOSSIER.md` and a read-only loader that performs no I/O, bound to the
  canonical document by a parity suite so an unmirrored canonical edit fails the build.
- **Three enums** — `MatchMethod`, `RequirementKind`, `TechnologyGapReason`.
- **Explicit enum parity partition** — every enum is declared either document-bound or
  self-declared, and a new enum fails the build until classified.
- **This changelog**, and a test binding the package version to `pyproject.toml`.

### Changed

- `REQUIRED_UNRESOLVED_POLICY_KEYS` reduced from eight entries to five. A resolved key
  reintroduced into the gate is rejected.
- `match_technologies()` signature now takes the candidate term index and the normalization
  policy, and returns matches **and** gaps. The previous signature accepted a dossier it did not
  read terms from.
- `assess_job()` now names the five keys that actually block it.
- `docs/ARCHITECTURE.md` records the implemented dimension and five known representational
  limits.

### Fixed

- Five enums had no membership assertion, or only a count. All eight self-declared enums now
  have exact member sets, so a renamed or swapped member fails as loudly as an added one.
- `MatchClassification` and `EvidenceTier` docstrings described A-3 and A-4 as unresolved; both
  were resolved by P-2 and P-1 on 2026-09-25.
- The P-1 through P-6 record described an eight-key gate that had since been reduced.

### Known limits

Recorded rather than worked around, because filling any of them would invent a value:

- Six of nine dimensions — 55 of 100 points — have approved weights but no allocation rule, and
  no gate key tracking that.
- Employment technologies are unavailable; the canonical employment entries state no explicit
  technology list. Tier 3 technology matching is therefore unreachable.
- Tier 4 technology evidence is unrepresentable; `TrainingEvidence` has no technologies field.
- Any-of grouping is approved policy but has no input format.
- No capture importer, report renderer, or persistence layer exists, so a listing cannot reach
  the implemented dimension through a pipeline.
- `README.md` still describes the original starter pack. It is a canonical document and needs an
  approved patch under `CONTEXT_UPDATE_PROTOCOL.md`.

## [0.1.0a0] — 2026-09-25

Deterministic foundation. No assessment behaviour.

### Added

- Frozen Pydantic domain models for listings, candidate evidence, and assessments, with contact
  fields, business-ownership fields, and years-of-experience fields unrepresentable by design
  (D-2, D-4, D-9).
- Single-definition-site enum module covering validation statuses, classifications,
  recommendations, work arrangements, compensation bands, evidence tiers, seven hard blockers,
  and twenty-four risk flags.
- Two-stage configuration validation: structural parsing always succeeds, readiness validation
  fails while any policy key is `UNRESOLVED`.
- Scoring, compensation, blocker, and risk-flag configuration with weights totalling 100.
- Owner-decision records D-1 through D-12 and scoring policy P-1 through P-6.
- Parity tests binding enums and configuration to their canonical source documents by labelled
  section, never by line number.
- Compliance tests failing the build on persistence dependencies, network dependencies, contact
  fields, external paths, or non-synthetic fixtures.
- Help-only CLI exposing a single `doctor` command that inspects nothing.
