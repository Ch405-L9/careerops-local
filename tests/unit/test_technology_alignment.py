"""Technology matching and the A-5 allocation.

Mechanics are tested against invented candidate terms, so nothing here depends on the real
dossier. The calibration figures at the end use the approved transcription, because those are
the numbers the first true run must reproduce.

Every expected value is computed by hand in the test, never by calling the code under test.
"""

import pytest

from careerops.assess.evidence import lookup_key, match_technologies, resolve_job_phrase
from careerops.assess.scoring import score_technology_alignment
from careerops.config.loader import load_assessment_config
from careerops.domain.assessment import TechnologyAlignmentResult
from careerops.dossier.approved_dossier import CandidateTerm, candidate_terms
from careerops.enums import (
    EvidenceTier,
    MatchMethod,
    RequirementKind,
    TechnologyGapReason,
)

T1 = EvidenceTier.TIER_1_VERIFIED_SKILL
T2 = EvidenceTier.TIER_2_PROJECT_EVIDENCE
T3 = EvidenceTier.TIER_3_EMPLOYMENT_EVIDENCE
T4 = EvidenceTier.TIER_4_TRAINING

SYNTHETIC_TERMS: tuple[CandidateTerm, ...] = (
    CandidateTerm("Python", T1, "Synthetic skills — Sample section"),
    CandidateTerm("React", T1, "Synthetic skills — Sample section"),
    CandidateTerm("REST APIs", T1, "Synthetic skills — Sample section"),
    CandidateTerm("Kotlin", T2, "Synthetic project — Sample project"),
    CandidateTerm("SQLite", T4, "Synthetic training — Sample course"),
)


@pytest.fixture(scope="module")
def normalization():
    return load_assessment_config().scoring.technology_matching_normalization


@pytest.fixture(scope="module")
def config():
    return load_assessment_config()


# =========================================================== A-6 lookup-key derivation


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Python", "python"),
        ("PYTHON", "python"),
        ("  Python  ", "python"),
        ("REST   APIs", "rest apis"),
        ("React.js", "react.js"),
        ("Python 3", "python 3"),
        ("C++", "c++"),
        ("C#", "c#"),
        (".NET", ".net"),
        ("TCP/IP", "tcp/ip"),
    ],
)
def test_lookup_key_applies_only_the_four_approved_steps(raw: str, expected: str) -> None:
    """NFC, casefold, whitespace collapse, trim. Nothing else.

    Punctuation and version suffixes survive on purpose: stripping them would collide C++
    with C#, mangle .NET, and split TCP/IP.
    """
    assert lookup_key(raw) == expected


def test_lookup_key_is_nfc_stable() -> None:
    """A decomposed and a composed form must produce the same key."""
    assert lookup_key("Rückblick") == lookup_key("Rückblick")


# ================================================================= A-6 phrase resolution


def test_display_name_resolves_exact(normalization) -> None:
    identifier, method, family = resolve_job_phrase("REST APIs", normalization)
    assert (identifier, method, family) == ("REST_APIS", MatchMethod.EXACT, None)


def test_alias_variant_resolves_through_its_family(normalization) -> None:
    identifier, method, family = resolve_job_phrase("React.js", normalization)
    assert (identifier, method, family) == ("REACT", MatchMethod.ALIAS, "REACT")


@pytest.mark.parametrize(
    ("phrase", "identifier"),
    [
        ("reactjs", "REACT"),
        ("RESTful APIs", "REST_APIS"),
        ("model context protocol", "MCP"),
        ("Retrieval-Augmented Generation", "RAG"),
        ("Chroma", "CHROMADB"),
        ("Okapi BM25", "BM25"),
        ("python3", "PYTHON"),
        ("SQLite3", "SQLITE"),
        ("bash shell", "BASH"),
    ],
)
def test_every_approved_alias_variant_resolves(
    normalization, phrase: str, identifier: str
) -> None:
    resolved, method, family = resolve_job_phrase(phrase, normalization)
    assert resolved == identifier
    assert method is MatchMethod.ALIAS
    assert family == identifier


@pytest.mark.parametrize(
    "phrase", ["crontab", "OpenSSH", "JS/TS", "javascript/typescript", "js", "ts"]
)
def test_deferred_variants_never_resolve_to_an_approved_identifier(
    normalization, phrase: str
) -> None:
    """The owner deferred these, so none may reach a canonical identifier."""
    identifier, method, family = resolve_job_phrase(phrase, normalization)
    assert identifier == lookup_key(phrase)
    assert method is MatchMethod.EXACT
    assert family is None


def test_an_unapproved_alias_never_matches(normalization) -> None:
    """A-6: unknown aliases never auto-match. 'ReactJS Native' is not React."""
    identifier, _, family = resolve_job_phrase("ReactJS Native", normalization)
    assert identifier != "REACT"
    assert family is None


# ===================================================================== A-6 no fuzziness


def test_substring_containment_never_matches(normalization) -> None:
    """'React Native' contains 'React'; 'Azure OpenAI' contains 'OpenAI'."""
    matches, gaps = match_technologies(
        ("React Native", "Azure OpenAI"), SYNTHETIC_TERMS, normalization
    )
    assert matches == ()
    assert {gap.raw_job_phrase for gap in gaps} == {"React Native", "Azure OpenAI"}


def test_a_term_is_never_split_into_tokens(normalization) -> None:
    """'Python Django' must not match on the word 'Python'."""
    matches, _ = match_technologies(("Python Django",), SYNTHETIC_TERMS, normalization)
    assert matches == ()


# ============================================================ E-3 and E-8 tier selection


def test_best_tier_wins_when_a_term_holds_several(normalization) -> None:
    """E-3: the highest-weighted evidence, not the first or the last."""
    terms = (
        CandidateTerm("Python", T2, "Synthetic project — Sample project"),
        CandidateTerm("Python", T1, "Synthetic skills — Sample section"),
    )
    matches, gaps = match_technologies(("Python",), terms, normalization)
    assert matches[0].tier is T1
    assert gaps == ()


def test_tier_three_outranks_tier_two(normalization) -> None:
    """E-8: tier ordinal does not imply weight order. Tier 3 is 0.90, Tier 2 is 0.70."""
    terms = (
        CandidateTerm("Python", T2, "Synthetic project — Sample project"),
        CandidateTerm("Python", T3, "Synthetic employment — Sample employer"),
    )
    matches, _ = match_technologies(("Python",), terms, normalization)
    assert matches[0].tier is T3


def test_tier_four_is_the_weakest(normalization) -> None:
    terms = (
        CandidateTerm("Python", T4, "Synthetic training — Sample course"),
        CandidateTerm("Python", T2, "Synthetic project — Sample project"),
    )
    matches, _ = match_technologies(("Python",), terms, normalization)
    assert matches[0].tier is T2


# ================================================================== E-4 and E-7 gaps


def test_no_evidence_scores_nothing_and_raises_a_gap(normalization) -> None:
    """E-4."""
    matches, gaps = match_technologies(("Weaviate",), SYNTHETIC_TERMS, normalization)
    assert matches == ()
    assert len(gaps) == 1
    assert gaps[0].reason is TechnologyGapReason.UNRECOGNIZED_TERM
    assert gaps[0].best_tier_found is None


@pytest.mark.parametrize(("phrase", "tier"), [("Kotlin", T2), ("SQLite", T4)])
def test_partial_credit_still_raises_a_gap(normalization, phrase: str, tier) -> None:
    """E-7: credit and flags are decoupled. A Tier 2 or Tier 4 match scores and still flags."""
    matches, gaps = match_technologies((phrase,), SYNTHETIC_TERMS, normalization)
    assert len(matches) == 1
    assert matches[0].tier is tier
    assert len(gaps) == 1
    assert gaps[0].reason is TechnologyGapReason.TIER_2_OR_TIER_4_ONLY
    assert gaps[0].best_tier_found is tier


def test_tier_one_match_raises_no_gap(normalization) -> None:
    matches, gaps = match_technologies(("Python",), SYNTHETIC_TERMS, normalization)
    assert len(matches) == 1
    assert gaps == ()


# ========================================================== E-5 audit disclosure


def test_every_match_discloses_its_full_audit_trail(normalization) -> None:
    matches, _ = match_technologies(("React.js",), SYNTHETIC_TERMS, normalization)
    match = matches[0]
    assert match.raw_job_phrase == "React.js"
    assert match.normalized_job_identifier == "REACT"
    assert match.raw_candidate_evidence_phrase == "React"
    assert match.normalized_candidate_identifier == "REACT"
    assert match.match_method is MatchMethod.ALIAS
    assert match.alias_family_identifier == "REACT"
    assert match.requirement_kind is RequirementKind.REQUIRED
    assert match.tier is T1
    assert match.evidence_reference == "Synthetic skills — Sample section"


def test_an_exact_match_names_no_alias_family(normalization) -> None:
    matches, _ = match_technologies(("Python",), SYNTHETIC_TERMS, normalization)
    assert matches[0].match_method is MatchMethod.EXACT
    assert matches[0].alias_family_identifier is None


# ==================================================================== slot counting


def test_duplicate_phrases_collapse_to_one_slot(normalization, config) -> None:
    """Dedupe is by resolved identifier, so keyword repetition cannot inflate a score."""
    result = score_technology_alignment(
        "synthetic-1", ("Python", "python", "PYTHON  ", "python3"), SYNTHETIC_TERMS, config
    )
    assert result.required_slot_count == 1
    assert result.points == 20.0


def test_blank_entries_are_not_slots(normalization, config) -> None:
    result = score_technology_alignment(
        "synthetic-1", ("Python", "", "   "), SYNTHETIC_TERMS, config
    )
    assert result.required_slot_count == 1


# =============================================================== A-5 the formula


def test_the_worked_example_scores_ten_exactly(config) -> None:
    """A-5: Weaviate plus Python, Python evidence only. 20 × (0.00 + 1.00) / 2 = 10.00."""
    result = score_technology_alignment(
        "synthetic-1", ("Weaviate", "Python"), SYNTHETIC_TERMS, config
    )
    assert result.required_slot_count == 2
    assert result.multiplier_sum == 1.00
    assert result.points == 10.00
    assert len(result.gaps) == 1


def test_zero_required_slots_scores_zero_with_no_gap(config) -> None:
    """A-5: and that alone can never produce AVOID or DO_NOT_APPLY (C-3)."""
    result = score_technology_alignment("synthetic-1", (), SYNTHETIC_TERMS, config)
    assert result.required_slot_count == 0
    assert result.points == 0.0
    assert result.gaps == ()
    assert result.matches == ()


def test_all_tier_one_reaches_the_full_dimension_weight(config) -> None:
    """E-1: the cap is the dimension weight, and the formula reaches it without clamping."""
    result = score_technology_alignment(
        "synthetic-1", ("Python", "React", "REST APIs"), SYNTHETIC_TERMS, config
    )
    assert result.multiplier_sum == 3.00
    assert result.points == 20.0
    assert result.points == result.dimension_weight


def test_points_are_exact_and_unrounded(config) -> None:
    """Rounding remains score_rounding_rule: 20 × 2.00 / 3 must stay 40/3."""
    result = score_technology_alignment(
        "synthetic-1", ("Python", "React", "Weaviate"), SYNTHETIC_TERMS, config
    )
    assert result.required_slot_count == 3
    assert result.multiplier_sum == 2.00
    assert result.points == 40 / 3
    assert result.points != round(result.points)


def test_long_required_lists_dilute_proportionally(config) -> None:
    """A-5: no extra penalty beyond proportional dilution."""
    result = score_technology_alignment(
        "synthetic-1",
        ("Python", "React", "REST APIs", "Weaviate", "Pinecone", "Milvus"),
        SYNTHETIC_TERMS,
        config,
    )
    assert result.required_slot_count == 6
    assert result.points == 20 * 3.00 / 6
    assert result.points == 10.0


def test_tier_two_only_scores_partial_credit(config) -> None:
    """20 × 0.70 / 1 = 14.00, and the gap is raised anyway (E-7)."""
    result = score_technology_alignment("synthetic-1", ("Kotlin",), SYNTHETIC_TERMS, config)
    assert result.multiplier_sum == 0.70
    assert result.points == 14.0
    assert len(result.gaps) == 1


def test_the_result_is_the_dimension_type_and_carries_no_verdict(config) -> None:
    """Ruling 2: a dimension figure can never become a full assessment."""
    result = score_technology_alignment("synthetic-1", ("Python",), SYNTHETIC_TERMS, config)
    assert isinstance(result, TechnologyAlignmentResult)
    assert result.dimension == "verified_technical_skill_alignment"
    assert not hasattr(result, "score")
    assert not hasattr(result, "classification")
    assert not hasattr(result, "recommendation")


def test_scoring_is_deterministic(config) -> None:
    args = ("synthetic-1", ("Python", "Kotlin", "Weaviate"), SYNTHETIC_TERMS, config)
    assert score_technology_alignment(*args) == score_technology_alignment(*args)


def test_a_preferred_match_cannot_be_smuggled_into_the_result(normalization) -> None:
    """A-7: the result type rejects any match that is not REQUIRED."""
    from pydantic import ValidationError

    matches, _ = match_technologies(("Python",), SYNTHETIC_TERMS, normalization)
    preferred = matches[0].model_copy(update={"requirement_kind": RequirementKind.PREFERRED})
    with pytest.raises(ValidationError, match="only required technologies"):
        TechnologyAlignmentResult(
            job_id="synthetic-1",
            dimension="verified_technical_skill_alignment",
            dimension_weight=20,
            required_slot_count=1,
            multiplier_sum=1.0,
            points=20.0,
            matches=(preferred,),
        )


# ================================================ calibration against the real dossier


def test_mcp_now_matches_at_tier_one(config) -> None:
    """The explicit-term declaration's whole purpose: Tier 1, no false gap."""
    result = score_technology_alignment("real-1", ("MCP",), candidate_terms(), config)
    assert result.matches[0].tier is T1
    assert result.matches[0].normalized_job_identifier == "MCP"
    assert result.gaps == ()
    assert result.points == 20.0


def test_a_strong_applied_ai_listing_scores_the_full_dimension(config) -> None:
    """All four required technologies are Tier 1 verified skills."""
    result = score_technology_alignment(
        "real-1", ("RAG", "Hybrid retrieval", "Python", "FastAPI"), candidate_terms(), config
    )
    assert result.required_slot_count == 4
    assert result.multiplier_sum == 4.00
    assert result.points == 20.0
    assert result.gaps == ()


def test_an_alias_heavy_listing_scores_the_full_dimension(config) -> None:
    """Without the approved alias table this would be three false gaps."""
    result = score_technology_alignment(
        "real-1",
        ("React.js", "RESTful APIs", "Model Context Protocol"),
        candidate_terms(),
        config,
    )
    assert result.points == 20.0
    assert {m.match_method for m in result.matches} == {MatchMethod.ALIAS}


def test_an_android_listing_scores_tier_two_with_gaps(config) -> None:
    """Kotlin and Android are project evidence only: 20 × 1.40 / 2 = 14.00, two gaps (E-7)."""
    result = score_technology_alignment(
        "real-1", ("Kotlin", "Android"), candidate_terms(), config
    )
    assert result.multiplier_sum == 1.40
    assert result.points == 14.0
    assert len(result.gaps) == 2
    assert {g.reason for g in result.gaps} == {TechnologyGapReason.TIER_2_OR_TIER_4_ONLY}


def test_an_adjacent_stack_listing_scores_zero(config) -> None:
    """Every requirement is a prohibited inference, and no alias may rescue it."""
    result = score_technology_alignment(
        "real-1",
        ("Kubernetes", "Terraform", "LangChain", "Azure OpenAI"),
        candidate_terms(),
        config,
    )
    assert result.required_slot_count == 4
    assert result.points == 0.0
    assert len(result.gaps) == 4
    assert result.matches == ()


def test_no_prohibited_inference_is_reachable_from_candidate_evidence() -> None:
    """Why PROHIBITED_INFERENCE is unreachable today: no candidate term names one."""
    terms = {entry.term.casefold() for entry in candidate_terms()}
    for target in (
        "docker",
        "kubernetes",
        "terraform",
        "langchain",
        "openai api",
        "azure openai",
        "gcp vertex ai",
    ):
        assert target not in terms
