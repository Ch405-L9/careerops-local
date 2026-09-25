"""Configuration schema tests, using in-memory configurations only."""

from typing import Any

import pytest
from pydantic import ValidationError

from careerops.config.schema import (
    REQUIRED_UNRESOLVED_POLICY_KEYS,
    UNRESOLVED,
    AssessmentPolicyUnresolvedError,
    BlockerConfig,
    ClassificationThresholds,
    CompensationConfig,
    EvidenceTierWeights,
    ReportDisplayPolicy,
    RiskFlagConfig,
    ScoringConfig,
    SeniorityBands,
    SeniorScopeRule,
)
from careerops.enums import BlockerCode, RiskFlag

VALID_WEIGHTS: dict[str, int] = {
    "role_family_relevance": 20,
    "verified_technical_skill_alignment": 20,
    "responsibility_and_project_evidence_alignment": 15,
    "seniority_and_documented_evidence_compatibility": 15,
    "compensation_compatibility": 10,
    "location_remote_relocation_compatibility": 8,
    "employment_type_compatibility": 5,
    "employer_listing_validation_quality": 4,
    "growth_learning_relevance": 3,
}

VALID_TIER_WEIGHTS: dict[str, float] = {
    "TIER_1_VERIFIED_SKILL": 1.00,
    "TIER_2_PROJECT_EVIDENCE": 0.70,
    "TIER_3_EMPLOYMENT_EVIDENCE": 0.90,
    "TIER_4_TRAINING": 0.30,
}

VALID_THRESHOLDS: dict[str, Any] = {
    "bands": [
        {"classification": "STRONG_MATCH", "min_score": 72, "max_score": 100},
        {"classification": "PLAUSIBLE_MATCH", "min_score": 58, "max_score": 71},
        {"classification": "STRETCH", "min_score": 42, "max_score": 57},
        {"classification": "AVOID", "min_score": 0, "max_score": 41},
    ]
}

VALID_SENIORITY: dict[str, Any] = {
    "bands": [
        {"points": 15, "description": "intermediate"},
        {"points": 11, "description": "mid-level with one moderate gap"},
        {"points": 7, "description": "broad or unclear"},
        {"points": 3, "description": "explicit 5+ years"},
        {"points": 0, "description": "materially unsupported senior scope"},
    ]
}

VALID_REPORT_DISPLAY: dict[str, Any] = {
    "order": [
        "Recommendation",
        "Hard blockers",
        "Validation status and risk flags",
        "Critical unknowns / missing evidence",
        "Match classification and score",
        "Per-dimension score breakdown",
        "Evidence-tier map with candidate-proof references",
        "Human next action",
    ],
    "score_never_headline": True,
}

VALID_SENIOR_SCOPE: dict[str, Any] = {
    "requires_explicit_senior_scope": True,
    "minimum_unsupported_requirements": 2,
    "senior_title_tokens": ["Senior", "Staff", "Principal", "Lead", "Head"],
    "unsupported_requirement_categories": [
        "leadership_or_ownership",
        "five_plus_years_required",
        "mlops_cloud_or_platform_ownership",
        "kubernetes_terraform_docker_core",
        "research_training_or_publications",
        "unsupported_scale_or_ownership_claims",
        "clearance_or_independent_blocker",
    ],
}


def _unresolved_policy(resolved: set[str] | None = None) -> dict[str, Any]:
    done = resolved or set()
    return {
        key: ("approved" if key in done else UNRESOLVED)
        for key in REQUIRED_UNRESOLVED_POLICY_KEYS
    }


def _scoring(
    weights: dict[str, int] | None = None,
    unresolved_policy: dict[str, Any] | None = None,
) -> ScoringConfig:
    return ScoringConfig.model_validate(
        {
            "weights": weights if weights is not None else dict(VALID_WEIGHTS),
            "evidence_tier_weighting": dict(VALID_TIER_WEIGHTS),
            "match_classification_thresholds": VALID_THRESHOLDS,
            "seniority_bands": VALID_SENIORITY,
            "report_display": VALID_REPORT_DISPLAY,
            "unresolved_policy": (
                unresolved_policy if unresolved_policy is not None else _unresolved_policy()
            ),
        }
    )


# --------------------------------------------------------------------------- weights


def test_weights_totalling_100_are_accepted() -> None:
    assert sum(_scoring().weights.values()) == 100


@pytest.mark.parametrize("delta", [-1, 1])
def test_weights_not_totalling_100_are_rejected(delta: int) -> None:
    weights = dict(VALID_WEIGHTS)
    weights["growth_learning_relevance"] += delta
    with pytest.raises(ValidationError):
        _scoring(weights)


def test_superseded_seniority_key_is_rejected() -> None:
    """D-4: the dimension was renamed; the old key must not load."""
    weights = dict(VALID_WEIGHTS)
    weights["seniority_years"] = weights.pop("seniority_and_documented_evidence_compatibility")
    with pytest.raises(ValidationError):
        _scoring(weights)


# ------------------------------------------------------------------ unresolved gate


def test_unresolved_keys_are_reported() -> None:
    """The gate reports the exact approved key set, in the approved order."""
    assert _scoring().unresolved_keys() == REQUIRED_UNRESOLVED_POLICY_KEYS


def test_unresolved_policy_key_set_must_be_exact() -> None:
    """A key cannot be dropped to unblock readiness, nor an extra key smuggled in."""
    short = _unresolved_policy()
    short.pop("score_rounding_rule")
    with pytest.raises(ValidationError):
        _scoring(unresolved_policy=short)

    extra = _unresolved_policy()
    extra["invented_key"] = UNRESOLVED
    with pytest.raises(ValidationError):
        _scoring(unresolved_policy=extra)


def test_resolving_every_key_would_allow_readiness() -> None:
    """The mechanism still works: a fully resolved synthetic gate reports nothing."""
    resolved = _scoring(unresolved_policy=_unresolved_policy(set(REQUIRED_UNRESOLVED_POLICY_KEYS)))
    assert resolved.unresolved_keys() == ()


def test_partially_resolved_gate_reports_only_the_remainder() -> None:
    partial = _scoring(unresolved_policy=_unresolved_policy({"score_rounding_rule"}))
    assert "score_rounding_rule" not in partial.unresolved_keys()
    assert len(partial.unresolved_keys()) == len(REQUIRED_UNRESOLVED_POLICY_KEYS) - 1


def test_unresolved_error_names_every_key() -> None:
    error = AssessmentPolicyUnresolvedError(["a", "b"])
    assert error.unresolved_keys == ("a", "b")
    assert "a, b" in str(error)


# --------------------------------------------------------------- P-1 tier weighting


def test_tier_weights_require_every_tier() -> None:
    incomplete = dict(VALID_TIER_WEIGHTS)
    incomplete.pop("TIER_4_TRAINING")
    with pytest.raises(ValidationError):
        EvidenceTierWeights.model_validate(incomplete)


def test_tier_multiplier_above_one_is_rejected() -> None:
    weights = dict(VALID_TIER_WEIGHTS)
    weights["TIER_2_PROJECT_EVIDENCE"] = 1.2
    with pytest.raises(ValidationError):
        EvidenceTierWeights.model_validate(weights)


def test_tier_multiplier_of_zero_or_below_is_rejected() -> None:
    for bad in (0.0, -0.1):
        weights = dict(VALID_TIER_WEIGHTS)
        weights["TIER_4_TRAINING"] = bad
        with pytest.raises(ValidationError):
            EvidenceTierWeights.model_validate(weights)


def test_tier_1_must_be_the_reference_multiplier() -> None:
    weights = dict(VALID_TIER_WEIGHTS)
    weights["TIER_1_VERIFIED_SKILL"] = 0.95
    with pytest.raises(ValidationError):
        EvidenceTierWeights.model_validate(weights)


# ------------------------------------------------------------------ P-2 thresholds


def test_classification_gap_is_rejected() -> None:
    bands = [dict(b) for b in VALID_THRESHOLDS["bands"]]
    bands[1]["max_score"] = 70
    with pytest.raises(ValidationError):
        ClassificationThresholds.model_validate({"bands": bands})


def test_classification_overlap_is_rejected() -> None:
    bands = [dict(b) for b in VALID_THRESHOLDS["bands"]]
    bands[1]["max_score"] = 72
    with pytest.raises(ValidationError):
        ClassificationThresholds.model_validate({"bands": bands})


def test_classification_not_covering_zero_to_hundred_is_rejected() -> None:
    bands = [dict(b) for b in VALID_THRESHOLDS["bands"]]
    bands[3]["min_score"] = 1
    with pytest.raises(ValidationError):
        ClassificationThresholds.model_validate({"bands": bands})


def test_classification_band_outside_zero_to_hundred_is_rejected() -> None:
    bands = [dict(b) for b in VALID_THRESHOLDS["bands"]]
    bands[0]["max_score"] = 101
    with pytest.raises(ValidationError):
        ClassificationThresholds.model_validate({"bands": bands})


def test_insufficient_evidence_may_not_hold_a_score_band() -> None:
    """C-4: it is reachable only through the critical-unknown cap."""
    bands = [dict(b) for b in VALID_THRESHOLDS["bands"]]
    bands[2]["classification"] = "INSUFFICIENT_EVIDENCE"
    with pytest.raises(ValidationError):
        ClassificationThresholds.model_validate({"bands": bands})


# ------------------------------------------------------------------- P-3 seniority


def test_seniority_point_set_must_be_exact() -> None:
    bands = [dict(b) for b in VALID_SENIORITY["bands"]]
    bands[2]["points"] = 8
    with pytest.raises(ValidationError):
        SeniorityBands.model_validate({"bands": bands})


def test_seniority_bands_must_descend() -> None:
    bands = [dict(b) for b in VALID_SENIORITY["bands"]]
    bands.reverse()
    with pytest.raises(ValidationError):
        SeniorityBands.model_validate({"bands": bands})


# ---------------------------------------------------------------- P-4 compensation


def _bands() -> list[dict[str, Any]]:
    return [
        {
            "classification": "BELOW_80K",
            "min_usd": None,
            "max_usd": 80000,
            "hard_blocker": True,
            "points": 0,
            "report_note": "below floor",
        },
        {
            "classification": "FALLBACK_80K_TO_85K",
            "min_usd": 80000,
            "max_usd": 86000,
            "hard_blocker": False,
            "points": 5,
            "report_note": "fallback",
        },
        {
            "classification": "BELOW_PREFERRED_REVIEW",
            "min_usd": 86000,
            "max_usd": 90000,
            "hard_blocker": False,
            "points": 7,
            "report_note": "below preferred",
        },
        {
            "classification": "TARGET_90K_PLUS",
            "min_usd": 90000,
            "max_usd": None,
            "hard_blocker": False,
            "points": 10,
            "report_note": "target",
        },
    ]


def _compensation(bands: list[dict[str, Any]], **overrides: Any) -> CompensationConfig:
    payload: dict[str, Any] = {
        "currency": "USD",
        "bands": bands,
        "contract_points": 0,
        "unknown_points": 0,
        "contract_handling": "never annualize",
        "unknown_handling": "never reject on absence alone",
    }
    payload.update(overrides)
    return CompensationConfig.model_validate(payload)


def test_contiguous_bands_are_accepted() -> None:
    assert len(_compensation(_bands()).bands) == 4


def test_band_gap_is_rejected() -> None:
    bands = _bands()
    bands[2]["min_usd"] = 87000
    with pytest.raises(ValidationError):
        _compensation(bands)


def test_band_overlap_is_rejected() -> None:
    bands = _bands()
    bands[2]["min_usd"] = 85000
    with pytest.raises(ValidationError):
        _compensation(bands)


def test_open_lower_bound_is_required() -> None:
    bands = _bands()
    bands[0]["min_usd"] = 1
    with pytest.raises(ValidationError):
        _compensation(bands)


def test_compensation_points_must_not_decrease_as_the_band_rises() -> None:
    bands = _bands()
    bands[2]["points"] = 3
    with pytest.raises(ValidationError):
        _compensation(bands)


def test_below_80k_must_be_zero_points_and_blocking() -> None:
    bands = _bands()
    bands[0]["points"] = 4
    with pytest.raises(ValidationError):
        _compensation(bands)


def test_contract_and_unknown_must_score_zero() -> None:
    with pytest.raises(ValidationError):
        _compensation(_bands(), contract_points=4)
    with pytest.raises(ValidationError):
        _compensation(_bands(), unknown_points=2)


# ------------------------------------------------------------------ P-5 senior scope


def test_senior_scope_requires_exactly_seven_categories() -> None:
    rule = dict(VALID_SENIOR_SCOPE)
    rule["unsupported_requirement_categories"] = list(
        VALID_SENIOR_SCOPE["unsupported_requirement_categories"]
    )[:-1]
    with pytest.raises(ValidationError):
        SeniorScopeRule.model_validate(rule)


def test_senior_scope_minimum_below_two_is_rejected() -> None:
    rule = dict(VALID_SENIOR_SCOPE)
    rule["minimum_unsupported_requirements"] = 1
    with pytest.raises(ValidationError):
        SeniorScopeRule.model_validate(rule)


def test_senior_title_alone_cannot_be_configured_to_block() -> None:
    rule = dict(VALID_SENIOR_SCOPE)
    rule["requires_explicit_senior_scope"] = False
    with pytest.raises(ValidationError):
        SeniorScopeRule.model_validate(rule)


def test_senior_scope_requires_title_tokens() -> None:
    rule = dict(VALID_SENIOR_SCOPE)
    rule["senior_title_tokens"] = []
    with pytest.raises(ValidationError):
        SeniorScopeRule.model_validate(rule)


# --------------------------------------------------------------- P-6 report display


def test_report_order_must_be_the_approved_sequence() -> None:
    policy = {"order": list(VALID_REPORT_DISPLAY["order"]), "score_never_headline": True}
    policy["order"][0], policy["order"][4] = policy["order"][4], policy["order"][0]
    with pytest.raises(ValidationError):
        ReportDisplayPolicy.model_validate(policy)


def test_score_never_headline_must_be_true() -> None:
    policy = {"order": list(VALID_REPORT_DISPLAY["order"]), "score_never_headline": False}
    with pytest.raises(ValidationError):
        ReportDisplayPolicy.model_validate(policy)


# ------------------------------------------------------------------------ blockers


def _blocker_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "degree_equivalency_phrases": ["or equivalent experience"],
        "blockers": [{"code": c.value, "enabled": True} for c in BlockerCode],
        "senior_scope": VALID_SENIOR_SCOPE,
    }
    payload.update(overrides)
    return payload


def test_incomplete_blocker_set_is_rejected() -> None:
    codes = list(BlockerCode)[:-1]
    with pytest.raises(ValidationError):
        BlockerConfig.model_validate(
            _blocker_payload(blockers=[{"code": c.value, "enabled": True} for c in codes])
        )


def test_empty_phrase_list_is_rejected() -> None:
    with pytest.raises(ValidationError):
        BlockerConfig.model_validate(_blocker_payload(degree_equivalency_phrases=[]))


# ----------------------------------------------------------------------- risk flags


def test_duplicate_risk_flag_is_rejected() -> None:
    rules = [{"flag": f.value, "enabled": True} for f in RiskFlag]
    rules.append({"flag": RiskFlag.PAYMENT_REQUEST.value, "enabled": True})
    with pytest.raises(ValidationError):
        RiskFlagConfig.model_validate({"flags": rules})


def test_incomplete_risk_flag_set_is_rejected() -> None:
    rules = [{"flag": f.value, "enabled": True} for f in RiskFlag][:-1]
    with pytest.raises(ValidationError):
        RiskFlagConfig.model_validate({"flags": rules})
