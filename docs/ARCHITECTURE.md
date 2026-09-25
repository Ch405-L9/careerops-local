# CareerOps Local — Architecture (Phase 1A)

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
7. `docs/SCORING_DECISIONS.md` — owner-approved implementation decisions (2026-09-25).

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

Phase 1A implements the type and policy substrate for layer 4 only: enums, frozen domain
models, configuration schemas, and pure-function signatures. Layers 1, 2, 3, 5, 6, and 7 do not
exist yet.

## Design invariants

**Assessment is pure.** Assessment functions take `(job, dossier, config)` and return a value.
No I/O, no clock, no randomness. Identical inputs always produce identical output, which makes
every rule table-testable and the result auditable.

**Blockers outrank scoring structurally.** Hard blockers are computed before any score and
cannot be suppressed by one. Nothing downstream can mutate a blocker, so
`PROJECT_GUARDRAILS.md` ("an LLM cannot override hard blockers") holds by construction rather
than by policy.

**The dossier is read-only.** `careerops.dossier.loader` declares a `Protocol` and nothing else.
No write path to any canonical file exists anywhere in the package, so
`CONTEXT_UPDATE_PROTOCOL.md` ("never update a canonical file automatically") is a property of
the architecture.

**Unknown is preserved.** Absent listing values remain `UNKNOWN`. No normalization path
converts an unknown into a concrete value, and absence of evidence is never treated as negative
evidence.

**Contact data is unrepresentable.** No domain model has an email, phone, or address field
(D-9). This is enforced by the type system and asserted by a compliance test.

**No external-action surface.** The package declares no HTTP client, browser-automation,
database, or model-provider dependency. Compliance tests fail the build if one appears.

**Business mode is a boundary, not a feature.** The dossier loader is an interface with one
intended implementation (personal candidate). A future business-opportunity mode would be a
second implementation behind the same interface. No code merges the two sources (D-2).

## Configuration: two validation stages

1. **Structural validation** parses and type-checks the shipped configuration. It must pass, so
   import, lint, type check, test, and CLI help all work.
2. **Readiness validation** is requested only when full assessment execution is wanted. It
   fails with a clear error while `match_classification_thresholds` (A-3) and
   `evidence_tier_weighting` (A-4) remain `UNRESOLVED`.

This separation prevents assessment logic from being written before the policy decisions that
govern it are approved.

## Phase 1A exclusions

SQLite, SQLAlchemy, Alembic, migrations, persistence, job ingestion, platform adapters,
external-directory reads, network access, browser automation, scraping, login, authentication,
API calls, LLM/Ollama/cloud-provider code, MCP integration, applications, messaging, outreach,
social posting, reports, and any canonical-document modification.
