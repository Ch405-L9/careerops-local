"""Technology-evidence matching (A-5, A-6, A-7).

Deterministic and pure: `(inputs, config)` in, values out. No I/O, no clock, no randomness.
Identical inputs always produce identical output.

Matching is whole-phrase equality of lookup keys, and nothing else. There is no token
matching, substring matching, fuzzy matching, semantic matching, embedding matching, LLM
matching, or external taxonomy or API lookup. A lookup key is derived using only the four
approved A-6 steps: Unicode NFC, casefold, whitespace collapse, trim.

Every match carries the nine audit values `TechnologyMatch` requires, so an undisclosed match
is unconstructable (E-5). Best tier wins (E-3). A required technology with no evidence scores
zero and raises a gap (E-4); one supported only at Tier 2 or Tier 4 receives partial credit
and still raises a gap (E-7).

Preferred technologies are not accepted here at all: required technologies are the only input
to the dimension (A-7), and preferred extraction is deferred.
"""

import unicodedata

from careerops.config.schema import TechnologyNormalizationPolicy
from careerops.domain.assessment import (
    PARTIAL_CREDIT_TIERS,
    TechnologyGap,
    TechnologyMatch,
)
from careerops.dossier.approved_dossier import CandidateTerm
from careerops.enums import EvidenceTier, MatchMethod, RequirementKind, TechnologyGapReason

__all__ = [
    "REQUIRED_SLOT_TIER_ORDER",
    "lookup_key",
    "match_technologies",
    "resolve_job_phrase",
]

REQUIRED_SLOT_TIER_ORDER: tuple[EvidenceTier, ...] = (
    EvidenceTier.TIER_1_VERIFIED_SKILL,
    EvidenceTier.TIER_3_EMPLOYMENT_EVIDENCE,
    EvidenceTier.TIER_2_PROJECT_EVIDENCE,
    EvidenceTier.TIER_4_TRAINING,
)
"""Best-to-worst tier order (E-3), taken from the approved P-1 multipliers.

Tier ordinal deliberately does not track weight: Tier 3 (0.90) outranks Tier 2 (0.70), per
rule E-8. Nothing here may sort by tier name or ordinal.
"""


def lookup_key(value: str) -> str:
    """Derive a lookup key using only the four approved A-6 steps, in order.

    NFC, casefold, whitespace collapse, trim. No punctuation stripping, no version stripping,
    and no acronym expansion: every such variant is an explicit alias row instead.
    """
    return " ".join(unicodedata.normalize("NFC", value).casefold().split())


def _registry(
    normalization: TechnologyNormalizationPolicy,
) -> tuple[dict[str, str], dict[str, str]]:
    """Return (key -> canonical id) for display names, and (key -> alias family id).

    Both the job side and the candidate side resolve through this same one-way table, which
    gives symmetric matching without bidirectional edges (A-6).
    """
    display: dict[str, str] = {
        lookup_key(entry.display_name): entry.id
        for entry in normalization.canonical_technologies
    }
    alias: dict[str, str] = {}
    for family in normalization.alias_families:
        for variant in family.variants:
            alias[lookup_key(variant)] = family.canonical_id
    return display, alias


def resolve_job_phrase(
    phrase: str,
    normalization: TechnologyNormalizationPolicy,
) -> tuple[str, MatchMethod, str | None]:
    """Resolve one phrase to (identifier, method, alias family), by whole-phrase equality.

    An approved canonical display name resolves EXACT to its identifier. An approved alias
    variant resolves ALIAS to its family's identifier. Any other phrase resolves EXACT to its
    own lookup key: the approved registry covers only the technologies that needed a variant
    row, so a technology with no variants still matches itself. Such an identifier is the
    lowercase lookup key rather than an approved uppercase identifier, which is how a report
    can tell the two apart.

    Nothing is ever guessed. An unapproved alias never matches, and a phrase that reaches no
    candidate evidence simply finds none.
    """
    key = lookup_key(phrase)
    display, alias = _registry(normalization)
    if key in display:
        return display[key], MatchMethod.EXACT, None
    if key in alias:
        return alias[key], MatchMethod.ALIAS, alias[key]
    return key, MatchMethod.EXACT, None


def _candidate_index(
    normalization: TechnologyNormalizationPolicy,
    terms: tuple[CandidateTerm, ...],
) -> dict[str, list[CandidateTerm]]:
    """Group candidate terms by the identifier they resolve to through the same table."""
    index: dict[str, list[CandidateTerm]] = {}
    for entry in terms:
        identifier, _, _ = resolve_job_phrase(entry.term, normalization)
        index.setdefault(identifier, []).append(entry)
    return index


def _best(candidates: list[CandidateTerm]) -> CandidateTerm:
    """Return the highest-weighted evidence for a slot (E-3), never the first or the newest."""
    return min(candidates, key=lambda entry: REQUIRED_SLOT_TIER_ORDER.index(entry.tier))


def match_technologies(
    required_technologies: tuple[str, ...],
    terms: tuple[CandidateTerm, ...],
    normalization: TechnologyNormalizationPolicy,
) -> tuple[tuple[TechnologyMatch, ...], tuple[TechnologyGap, ...]]:
    """Match required technologies to candidate evidence, with tier and audit trail.

    Returns matched slots and unsatisfied slots. Required slots are deduplicated by resolved
    identifier, so a listing repeating a technology yields one slot. Any-of grouping is not
    applied: the capture format carries no any-of marker, so each entry is one slot until a
    grouped requirement source exists.

    `terms` is the candidate evidence index, normally
    `careerops.dossier.approved_dossier.candidate_terms()`. It is passed rather than fetched
    so the dependency is explicit and so synthetic terms can be supplied in tests. A listing
    can never modify it.
    """
    index = _candidate_index(normalization, terms)
    display, _ = _registry(normalization)
    approved_identifiers = set(display.values())

    matches: list[TechnologyMatch] = []
    gaps: list[TechnologyGap] = []
    seen: set[str] = set()

    for phrase in required_technologies:
        if not phrase.strip():
            continue
        identifier, method, family = resolve_job_phrase(phrase, normalization)
        if identifier in seen:
            continue
        seen.add(identifier)

        evidence = index.get(identifier)
        if evidence is None:
            gaps.append(
                TechnologyGap(
                    raw_job_phrase=phrase,
                    normalized_job_identifier=(
                        identifier if identifier in approved_identifiers else None
                    ),
                    reason=(
                        TechnologyGapReason.NO_EVIDENCE
                        if identifier in approved_identifiers
                        else TechnologyGapReason.UNRECOGNIZED_TERM
                    ),
                    best_tier_found=None,
                )
            )
            continue

        best = _best(evidence)
        matches.append(
            TechnologyMatch(
                technology=phrase.strip(),
                raw_job_phrase=phrase,
                normalized_job_identifier=identifier,
                raw_candidate_evidence_phrase=best.term,
                normalized_candidate_identifier=identifier,
                match_method=method,
                alias_family_identifier=family,
                requirement_kind=RequirementKind.REQUIRED,
                tier=best.tier,
                evidence_reference=best.evidence_reference,
            )
        )
        if best.tier in PARTIAL_CREDIT_TIERS:
            gaps.append(
                TechnologyGap(
                    raw_job_phrase=phrase,
                    normalized_job_identifier=identifier,
                    reason=TechnologyGapReason.TIER_2_OR_TIER_4_ONLY,
                    best_tier_found=best.tier,
                )
            )

    return tuple(matches), tuple(gaps)
