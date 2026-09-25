"""Tests against the shipped configuration in `config/`.

Structural validation must pass. Readiness validation must fail on exactly the two approved
unresolved keys, and on nothing else.
"""

from pathlib import Path

import pytest

from careerops.config.loader import load_assessment_config, load_ready_assessment_config
from careerops.config.schema import (
    APPROVED_REPORT_ORDER,
    REQUIRED_UNRESOLVED_POLICY_KEYS,
    AssessmentPolicyUnresolvedError,
)
from careerops.enums import (
    BlockerCode,
    EvidenceTier,
    MatchClassification,
    RiskFlag,
    SalaryCompatibility,
)

APPROVED_PHRASES = (
    "or equivalent experience",
    "or equivalent practical experience",
    "or equivalent professional experience",
    "or equivalent work experience",
    "or related experience",
    "equivalent combination of education and experience",
    "education or equivalent experience",
    "degree preferred",
    "bachelor's preferred",
    "or demonstrable experience",
)


def test_shipped_configuration_parses_structurally(config_dir: Path) -> None:
    """Stage 1 must succeed so import, lint, type check, test, and CLI help all work."""
    config = load_assessment_config(config_dir)
    assert sum(config.scoring.weights.values()) == 100


def test_shipped_configuration_is_not_ready(config_dir: Path) -> None:
    """Stage 2 must fail while the approved policy gate remains unresolved."""
    with pytest.raises(AssessmentPolicyUnresolvedError) as excinfo:
        load_ready_assessment_config(config_dir)
    assert excinfo.value.unresolved_keys == REQUIRED_UNRESOLVED_POLICY_KEYS
    for key in REQUIRED_UNRESOLVED_POLICY_KEYS:
        assert key in str(excinfo.value)


def test_unresolved_key_set_is_exact(config_dir: Path) -> None:
    """The exact named tuple in the approved order. Never merely a count."""
    assert load_assessment_config(config_dir).unresolved_keys() == (
        "technology_base_credit_allocation",
        "technology_matching_normalization",
        "required_vs_preferred_technology_handling",
        "seniority_band_selection_precedence",
        "compensation_range_selection_rule",
        "critical_unknown_detection_rule",
        "score_rounding_rule",
        "report_and_cli_score_display_scope",
    )


def test_seniority_dimension_uses_the_approved_name(config_dir: Path) -> None:
    """D-4."""
    weights = load_assessment_config(config_dir).scoring.weights
    assert weights["seniority_and_documented_evidence_compatibility"] == 15
    assert "seniority_years" not in weights


def test_bands_tile_the_range_without_gap_or_overlap(config_dir: Path) -> None:
    """D-3."""
    bands = load_assessment_config(config_dir).compensation.bands
    ordered = sorted(bands, key=lambda b: (b.min_usd is not None, b.min_usd or 0))
    assert ordered[0].min_usd is None
    assert ordered[-1].max_usd is None
    for lower, upper in zip(ordered, ordered[1:], strict=False):
        assert lower.max_usd == upper.min_usd


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        (79_999, SalaryCompatibility.BELOW_80K),
        (80_000, SalaryCompatibility.FALLBACK_80K_TO_85K),
        (85_999, SalaryCompatibility.FALLBACK_80K_TO_85K),
        (86_000, SalaryCompatibility.BELOW_PREFERRED_REVIEW),
        (89_999, SalaryCompatibility.BELOW_PREFERRED_REVIEW),
        (90_000, SalaryCompatibility.TARGET_90K_PLUS),
        (250_000, SalaryCompatibility.TARGET_90K_PLUS),
    ],
)
def test_every_boundary_amount_falls_in_exactly_one_band(
    config_dir: Path, amount: int, expected: SalaryCompatibility
) -> None:
    """Computed in the test, not in the package: Phase 1A implements no band lookup."""
    bands = load_assessment_config(config_dir).compensation.bands
    matched = [
        band
        for band in bands
        if (band.min_usd is None or amount >= band.min_usd)
        and (band.max_usd is None or amount < band.max_usd)
    ]
    assert len(matched) == 1
    assert matched[0].classification is expected


def test_only_below_80k_is_a_hard_blocker(config_dir: Path) -> None:
    """D-3, A-2: 86,000-89,999 is not a hard blocker."""
    bands = load_assessment_config(config_dir).compensation.bands
    blocking = {band.classification for band in bands if band.hard_blocker}
    assert blocking == {SalaryCompatibility.BELOW_80K}


def test_below_preferred_review_note_states_both_boundaries(config_dir: Path) -> None:
    """A-2 requires the report to state the position relative to both figures."""
    bands = load_assessment_config(config_dir).compensation.bands
    note = next(
        band.report_note
        for band in bands
        if band.classification is SalaryCompatibility.BELOW_PREFERRED_REVIEW
    )
    assert "90,000" in note
    assert "80,000" in note


def test_degree_equivalency_phrases_are_the_approved_list(config_dir: Path) -> None:
    """D-8."""
    phrases = load_assessment_config(config_dir).blockers.degree_equivalency_phrases
    assert phrases == APPROVED_PHRASES


def test_blocker_set_is_complete_and_expected(config_dir: Path) -> None:
    """D-5, D-6, D-10 shape this set."""
    codes = {rule.code for rule in load_assessment_config(config_dir).blockers.blockers}
    assert codes == set(BlockerCode)
    assert len(codes) == 7


def test_risk_flag_registry_is_complete(config_dir: Path) -> None:
    flags = {rule.flag for rule in load_assessment_config(config_dir).risk_flags.flags}
    assert flags == set(RiskFlag)
    assert len(flags) == 24


def test_blockers_config_declares_no_salary_override(repo_root: Path) -> None:
    """D-10: the override is deferred, so no key may hint at one."""
    text = (repo_root / "config" / "blockers.yaml").read_text(encoding="utf-8")
    keys = [
        line.split(":", 1)[0].strip().lstrip("- ")
        for line in text.splitlines()
        if ":" in line and not line.strip().startswith("#")
    ]
    assert not [key for key in keys if "override" in key.lower()]


def test_risk_flag_config_declares_no_detection_patterns(repo_root: Path) -> None:
    """Detection patterns are Phase 3 work and must be absent."""
    text = (repo_root / "config" / "risk_flags.yaml").read_text(encoding="utf-8")
    directives = "\n".join(
        line for line in text.splitlines() if not line.strip().startswith("#")
    )
    assert "pattern" not in directives.lower()


def test_missing_config_file_is_reported_clearly(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_assessment_config(tmp_path)


# =========================================================================== P-1


def test_evidence_tier_multipliers_are_the_approved_values(config_dir: Path) -> None:
    """P-1."""
    weights = load_assessment_config(config_dir).scoring.evidence_tier_weighting
    assert weights.TIER_1_VERIFIED_SKILL == 1.00
    assert weights.TIER_2_PROJECT_EVIDENCE == 0.70
    assert weights.TIER_3_EMPLOYMENT_EVIDENCE == 0.90
    assert weights.TIER_4_TRAINING == 0.30


def test_every_evidence_tier_has_a_multiplier(config_dir: Path) -> None:
    weights = load_assessment_config(config_dir).scoring.evidence_tier_weighting
    for tier in EvidenceTier:
        assert getattr(weights, tier.value) > 0


def test_tier_3_outranks_tier_2(config_dir: Path) -> None:
    """E-8: tier ordinal does not imply weight order."""
    weights = load_assessment_config(config_dir).scoring.evidence_tier_weighting
    assert weights.TIER_3_EMPLOYMENT_EVIDENCE > weights.TIER_2_PROJECT_EVIDENCE


def test_tier_1_is_the_reference_multiplier(config_dir: Path) -> None:
    weights = load_assessment_config(config_dir).scoring.evidence_tier_weighting
    values = [getattr(weights, tier.value) for tier in EvidenceTier]
    assert weights.TIER_1_VERIFIED_SKILL == 1.00 == max(values)


def test_evidence_tier_cap_is_the_skill_dimension_weight(config_dir: Path) -> None:
    """E-1: multipliers are capped at verified_technical_skill_alignment."""
    config = load_assessment_config(config_dir)
    assert config.evidence_tier_cap_points() == 20
    assert config.evidence_tier_cap_points() == (
        config.scoring.weights["verified_technical_skill_alignment"]
    )


# =========================================================================== P-2


def test_classification_bands_are_the_approved_values(config_dir: Path) -> None:
    """P-2."""
    bands = load_assessment_config(config_dir).scoring.match_classification_thresholds.bands
    actual = {band.classification: (band.min_score, band.max_score) for band in bands}
    assert actual == {
        MatchClassification.STRONG_MATCH: (72, 100),
        MatchClassification.PLAUSIBLE_MATCH: (58, 71),
        MatchClassification.STRETCH: (42, 57),
        MatchClassification.AVOID: (0, 41),
    }


def test_classification_bands_tile_zero_to_one_hundred(config_dir: Path) -> None:
    bands = load_assessment_config(config_dir).scoring.match_classification_thresholds.bands
    ordered = sorted(bands, key=lambda b: b.min_score)
    assert ordered[0].min_score == 0
    assert ordered[-1].max_score == 100
    for lower, upper in zip(ordered, ordered[1:], strict=False):
        assert lower.max_score + 1 == upper.min_score


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (0, MatchClassification.AVOID),
        (41, MatchClassification.AVOID),
        (42, MatchClassification.STRETCH),
        (57, MatchClassification.STRETCH),
        (58, MatchClassification.PLAUSIBLE_MATCH),
        (71, MatchClassification.PLAUSIBLE_MATCH),
        (72, MatchClassification.STRONG_MATCH),
        (100, MatchClassification.STRONG_MATCH),
    ],
)
def test_classification_boundary_scores_fall_in_exactly_one_band(
    config_dir: Path, score: int, expected: MatchClassification
) -> None:
    """Computed in the test: Phase 1A implements no classification lookup."""
    bands = load_assessment_config(config_dir).scoring.match_classification_thresholds.bands
    matched = [b for b in bands if b.min_score <= score <= b.max_score]
    assert len(matched) == 1
    assert matched[0].classification is expected


def test_insufficient_evidence_has_no_score_band(config_dir: Path) -> None:
    """C-4: reachable only through the critical-unknown cap."""
    bands = load_assessment_config(config_dir).scoring.match_classification_thresholds.bands
    assert MatchClassification.INSUFFICIENT_EVIDENCE not in {b.classification for b in bands}


# =========================================================================== P-3


def test_seniority_bands_are_the_approved_point_values(config_dir: Path) -> None:
    """P-3."""
    bands = load_assessment_config(config_dir).scoring.seniority_bands.bands
    assert [band.points for band in bands] == [15, 11, 7, 3, 0]
    assert all(band.description.strip() for band in bands)


def test_seniority_band_maximum_equals_dimension_weight(config_dir: Path) -> None:
    config = load_assessment_config(config_dir)
    top = max(band.points for band in config.scoring.seniority_bands.bands)
    assert top == config.scoring.weights["seniority_and_documented_evidence_compatibility"] == 15


# =========================================================================== P-4


def test_compensation_points_are_the_approved_values(config_dir: Path) -> None:
    """P-4."""
    config = load_assessment_config(config_dir)
    points = {band.classification: band.points for band in config.compensation.bands}
    assert points == {
        SalaryCompatibility.TARGET_90K_PLUS: 10,
        SalaryCompatibility.BELOW_PREFERRED_REVIEW: 7,
        SalaryCompatibility.FALLBACK_80K_TO_85K: 5,
        SalaryCompatibility.BELOW_80K: 0,
    }
    assert config.compensation.contract_points == 0
    assert config.compensation.unknown_points == 0


def test_compensation_points_are_non_decreasing_as_the_band_rises(config_dir: Path) -> None:
    bands = load_assessment_config(config_dir).compensation.bands
    ordered = sorted(bands, key=lambda b: (b.min_usd is not None, b.min_usd or 0))
    points = [band.points for band in ordered]
    assert points == sorted(points)


def test_compensation_maximum_equals_dimension_weight(config_dir: Path) -> None:
    config = load_assessment_config(config_dir)
    top = max(band.points for band in config.compensation.bands)
    assert top == config.scoring.weights["compensation_compatibility"] == 10


# =========================================================================== P-5


def test_senior_scope_rule_requires_two_unsupported_requirements(config_dir: Path) -> None:
    """P-5: a senior title alone is never an automatic hard blocker."""
    rule = load_assessment_config(config_dir).blockers.senior_scope
    assert rule.requires_explicit_senior_scope is True
    assert rule.minimum_unsupported_requirements == 2
    assert len(rule.unsupported_requirement_categories) == 7
    assert "Senior" in rule.senior_title_tokens


def test_senior_scope_adds_no_blocker_code(config_dir: Path) -> None:
    codes = {rule.code for rule in load_assessment_config(config_dir).blockers.blockers}
    assert codes == set(BlockerCode)
    assert len(codes) == 7


# =========================================================================== P-6


def test_report_display_order_is_the_approved_sequence(config_dir: Path) -> None:
    """P-6."""
    display = load_assessment_config(config_dir).scoring.report_display
    assert display.order == APPROVED_REPORT_ORDER
    assert display.score_never_headline is True


def test_score_appears_at_position_five(config_dir: Path) -> None:
    """C-5: the score is never a headline."""
    order = load_assessment_config(config_dir).scoring.report_display.order
    assert order.index("Match classification and score") == 4
    assert order[0] == "Recommendation"
    assert order[1] == "Hard blockers"


# ================================================================ no implementation


def test_no_assessment_behaviour_is_implemented() -> None:
    """The gate is meaningless if logic were added alongside the policy."""
    from careerops.assess import blockers, evidence, risk_flags, scoring

    for module, name, arity in (
        (blockers, "detect_blockers", 3),
        (blockers, "degree_requirement_is_blocking", 2),
        (risk_flags, "detect_risk_flags", 3),
        (evidence, "match_technologies", 2),
        (scoring, "assess_compensation", 2),
        (scoring, "assess_job", 3),
    ):
        with pytest.raises(NotImplementedError):
            getattr(module, name)(*[None] * arity)
