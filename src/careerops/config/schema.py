"""Configuration schemas.

Structural validation is strict but tolerates the UNRESOLVED sentinel. Readiness validation
is a separate, explicit step that fails while any policy key is still UNRESOLVED.
"""

from collections.abc import Sequence
from typing import Final, Literal

from pydantic import field_validator, model_validator

from careerops.domain import FrozenModel
from careerops.enums import BlockerCode, RiskFlag, SalaryCompatibility

__all__ = [
    "UNRESOLVED",
    "AssessmentConfig",
    "AssessmentPolicyUnresolvedError",
    "BlockerConfig",
    "BlockerRule",
    "CompensationBand",
    "CompensationConfig",
    "RiskFlagConfig",
    "RiskFlagRule",
    "ScoringConfig",
    "Unresolved",
]

UNRESOLVED: Final = "UNRESOLVED"
"""Sentinel for a policy decision the owner has not yet approved. Never invent a value."""

Unresolved = Literal["UNRESOLVED"]

EXPECTED_WEIGHT_KEYS: Final[frozenset[str]] = frozenset(
    {
        "role_family_relevance",
        "verified_technical_skill_alignment",
        "responsibility_and_project_evidence_alignment",
        "seniority_and_documented_evidence_compatibility",
        "compensation_compatibility",
        "location_remote_relocation_compatibility",
        "employment_type_compatibility",
        "employer_listing_validation_quality",
        "growth_learning_relevance",
    }
)
"""The nine scoring dimensions. The 15-point dimension is named per D-4."""

TOTAL_WEIGHT: Final = 100


class AssessmentPolicyUnresolvedError(RuntimeError):
    """Raised when full assessment execution is requested before policy is approved."""

    def __init__(self, keys: Sequence[str]) -> None:
        self.unresolved_keys: tuple[str, ...] = tuple(keys)
        joined = ", ".join(self.unresolved_keys)
        super().__init__(
            f"Assessment policy is not ready. Unresolved keys: {joined}. "
            "These require explicit owner approval, recorded in docs/SCORING_DECISIONS.md, "
            "before assessment behaviour may be implemented or executed. "
            "No value may be invented."
        )


class ScoringConfig(FrozenModel):
    """Weighted scoring dimensions and the two unresolved policy keys."""

    weights: dict[str, int]
    match_classification_thresholds: Unresolved | dict[str, int]
    evidence_tier_weighting: Unresolved | dict[str, float]

    @field_validator("weights")
    @classmethod
    def _check_weights(cls, value: dict[str, int]) -> dict[str, int]:
        keys = frozenset(value)
        if keys != EXPECTED_WEIGHT_KEYS:
            missing = sorted(EXPECTED_WEIGHT_KEYS - keys)
            unexpected = sorted(keys - EXPECTED_WEIGHT_KEYS)
            raise ValueError(
                f"scoring weight keys are wrong. missing={missing} unexpected={unexpected}"
            )
        total = sum(value.values())
        if total != TOTAL_WEIGHT:
            raise ValueError(f"scoring weights must total {TOTAL_WEIGHT}, got {total}")
        return value

    def unresolved_keys(self) -> tuple[str, ...]:
        """Return the names of policy keys that are still UNRESOLVED."""
        found = [
            name
            for name in ("match_classification_thresholds", "evidence_tier_weighting")
            if getattr(self, name) == UNRESOLVED
        ]
        return tuple(found)


class CompensationBand(FrozenModel):
    """One compensation band. Lower bound inclusive, upper bound exclusive."""

    classification: SalaryCompatibility
    min_usd: int | None
    max_usd: int | None
    hard_blocker: bool
    report_note: str


class CompensationConfig(FrozenModel):
    """Compensation policy (D-3, A-2). Bands must tile the range with no gap and no overlap."""

    currency: Literal["USD"]
    bands: tuple[CompensationBand, ...]
    contract_handling: str
    unknown_handling: str

    @model_validator(mode="after")
    def _check_tiling(self) -> "CompensationConfig":
        if not self.bands:
            raise ValueError("compensation bands must not be empty")
        ordered = sorted(self.bands, key=lambda b: (b.min_usd is not None, b.min_usd or 0))
        if ordered[0].min_usd is not None:
            raise ValueError("the lowest compensation band must be open below (min_usd: null)")
        if ordered[-1].max_usd is not None:
            raise ValueError("the highest compensation band must be open above (max_usd: null)")
        for lower, upper in zip(ordered, ordered[1:], strict=False):
            if lower.max_usd != upper.min_usd:
                raise ValueError(
                    "compensation bands must tile with no gap and no overlap: "
                    f"{lower.classification} ends at {lower.max_usd} but "
                    f"{upper.classification} begins at {upper.min_usd}"
                )
        return self


class BlockerRule(FrozenModel):
    """One hard blocker and whether it is enabled."""

    code: BlockerCode
    enabled: bool


class BlockerConfig(FrozenModel):
    """Hard blocker policy (D-5, D-6, D-8, D-10)."""

    degree_equivalency_phrases: tuple[str, ...]
    blockers: tuple[BlockerRule, ...]

    @model_validator(mode="after")
    def _check_complete(self) -> "BlockerConfig":
        codes = [rule.code for rule in self.blockers]
        if len(codes) != len(set(codes)):
            raise ValueError("duplicate blocker code in configuration")
        if set(codes) != set(BlockerCode):
            missing = sorted(c.value for c in set(BlockerCode) - set(codes))
            raise ValueError(f"blocker configuration is incomplete. missing={missing}")
        if not self.degree_equivalency_phrases:
            raise ValueError("degree_equivalency_phrases must not be empty")
        return self


class RiskFlagRule(FrozenModel):
    """One risk flag and whether it is enabled."""

    flag: RiskFlag
    enabled: bool


class RiskFlagConfig(FrozenModel):
    """Risk flag registry. Must carry every flag in PROJECT_GUARDRAILS.md."""

    flags: tuple[RiskFlagRule, ...]

    @model_validator(mode="after")
    def _check_complete(self) -> "RiskFlagConfig":
        names = [rule.flag for rule in self.flags]
        if len(names) != len(set(names)):
            raise ValueError("duplicate risk flag in configuration")
        if set(names) != set(RiskFlag):
            missing = sorted(f.value for f in set(RiskFlag) - set(names))
            raise ValueError(f"risk flag configuration is incomplete. missing={missing}")
        return self


class AssessmentConfig(FrozenModel):
    """The complete assessment policy: structurally valid, not necessarily ready to execute."""

    scoring: ScoringConfig
    compensation: CompensationConfig
    blockers: BlockerConfig
    risk_flags: RiskFlagConfig

    def unresolved_keys(self) -> tuple[str, ...]:
        """Return every policy key still awaiting owner approval."""
        return self.scoring.unresolved_keys()

    def require_ready(self) -> None:
        """Raise unless every policy decision needed to execute an assessment is approved."""
        unresolved = self.unresolved_keys()
        if unresolved:
            raise AssessmentPolicyUnresolvedError(unresolved)
