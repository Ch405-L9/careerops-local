"""Configuration schema tests, using in-memory configurations only."""

from typing import Any

import pytest
from pydantic import ValidationError

from careerops.config.schema import (
    UNRESOLVED,
    AssessmentPolicyUnresolvedError,
    BlockerConfig,
    CompensationConfig,
    RiskFlagConfig,
    ScoringConfig,
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


def _scoring(weights: dict[str, int]) -> ScoringConfig:
    return ScoringConfig(
        weights=weights,
        match_classification_thresholds=UNRESOLVED,
        evidence_tier_weighting=UNRESOLVED,
    )


def test_weights_totalling_100_are_accepted() -> None:
    assert sum(_scoring(dict(VALID_WEIGHTS)).weights.values()) == 100


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


def test_unresolved_keys_are_reported() -> None:
    assert _scoring(dict(VALID_WEIGHTS)).unresolved_keys() == (
        "match_classification_thresholds",
        "evidence_tier_weighting",
    )


def test_unresolved_error_names_every_key() -> None:
    error = AssessmentPolicyUnresolvedError(["a", "b"])
    assert error.unresolved_keys == ("a", "b")
    assert "a, b" in str(error)


def _bands() -> list[dict[str, Any]]:
    return [
        {
            "classification": "BELOW_80K",
            "min_usd": None,
            "max_usd": 80000,
            "hard_blocker": True,
            "report_note": "below floor",
        },
        {
            "classification": "FALLBACK_80K_TO_85K",
            "min_usd": 80000,
            "max_usd": 86000,
            "hard_blocker": False,
            "report_note": "fallback",
        },
        {
            "classification": "BELOW_PREFERRED_REVIEW",
            "min_usd": 86000,
            "max_usd": 90000,
            "hard_blocker": False,
            "report_note": "below preferred",
        },
        {
            "classification": "TARGET_90K_PLUS",
            "min_usd": 90000,
            "max_usd": None,
            "hard_blocker": False,
            "report_note": "target",
        },
    ]


def _compensation(bands: list[dict[str, Any]]) -> CompensationConfig:
    return CompensationConfig.model_validate(
        {
            "currency": "USD",
            "bands": bands,
            "contract_handling": "never annualize",
            "unknown_handling": "never reject on absence alone",
        }
    )


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


def test_incomplete_blocker_set_is_rejected() -> None:
    codes = [c for c in BlockerCode][:-1]
    with pytest.raises(ValidationError):
        BlockerConfig.model_validate(
            {
                "degree_equivalency_phrases": ["or equivalent experience"],
                "blockers": [{"code": c.value, "enabled": True} for c in codes],
            }
        )


def test_empty_phrase_list_is_rejected() -> None:
    with pytest.raises(ValidationError):
        BlockerConfig.model_validate(
            {
                "degree_equivalency_phrases": [],
                "blockers": [{"code": c.value, "enabled": True} for c in BlockerCode],
            }
        )


def test_duplicate_risk_flag_is_rejected() -> None:
    rules = [{"flag": f.value, "enabled": True} for f in RiskFlag]
    rules.append({"flag": RiskFlag.PAYMENT_REQUEST.value, "enabled": True})
    with pytest.raises(ValidationError):
        RiskFlagConfig.model_validate({"flags": rules})


def test_incomplete_risk_flag_set_is_rejected() -> None:
    rules = [{"flag": f.value, "enabled": True} for f in RiskFlag][:-1]
    with pytest.raises(ValidationError):
        RiskFlagConfig.model_validate({"flags": rules})
