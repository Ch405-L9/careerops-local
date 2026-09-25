"""Configuration schemas.

Two distinct validation stages, kept separate on purpose:

1. Structural validation parses and type-checks the shipped configuration. It succeeds
   while policy decisions remain outstanding, so import, lint, type check, test, and CLI
   help all work.
2. Readiness validation is a separate, explicit step that fails while any key in
   `REQUIRED_UNRESOLVED_POLICY_KEYS` is still the UNRESOLVED sentinel.

Policy source: docs/SCORING_DECISIONS.md, owner-decision record dated 2026-09-25
(P-1 through P-6). No assessment behaviour is implemented here.
"""

from collections.abc import Sequence
from typing import Any, Final, Literal

from pydantic import field_validator, model_validator

from careerops.domain import FrozenModel
from careerops.enums import BlockerCode, MatchClassification, RiskFlag, SalaryCompatibility

__all__ = [
    "APPROVED_REPORT_ORDER",
    "REQUIRED_UNRESOLVED_POLICY_KEYS",
    "UNRESOLVED",
    "AssessmentConfig",
    "AssessmentPolicyUnresolvedError",
    "BlockerConfig",
    "BlockerRule",
    "ClassificationBand",
    "ClassificationThresholds",
    "CompensationBand",
    "CompensationConfig",
    "EvidenceTierWeights",
    "ReportDisplayPolicy",
    "RiskFlagConfig",
    "RiskFlagRule",
    "ScoringConfig",
    "SeniorScopeRule",
    "SeniorityBand",
    "SeniorityBands",
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
MIN_SCORE: Final = 0
MAX_SCORE: Final = 100

REQUIRED_UNRESOLVED_POLICY_KEYS: Final[tuple[str, ...]] = (
    "technology_base_credit_allocation",
    "technology_matching_normalization",
    "required_vs_preferred_technology_handling",
    "seniority_band_selection_precedence",
    "compensation_range_selection_rule",
    "critical_unknown_detection_rule",
    "score_rounding_rule",
    "report_and_cli_score_display_scope",
)
"""Policy decisions that gate assessment readiness. Order is the approved order."""

APPROVED_SENIORITY_POINTS: Final[tuple[int, ...]] = (15, 11, 7, 3, 0)
"""P-3 point bands, in descending order."""

APPROVED_REPORT_ORDER: Final[tuple[str, ...]] = (
    "Recommendation",
    "Hard blockers",
    "Validation status and risk flags",
    "Critical unknowns / missing evidence",
    "Match classification and score",
    "Per-dimension score breakdown",
    "Evidence-tier map with candidate-proof references",
    "Human next action",
)
"""P-6 report section order. The score sits at position 5 and is never a headline."""

APPROVED_SENIOR_SCOPE_CATEGORIES: Final[tuple[str, ...]] = (
    "leadership_or_ownership",
    "five_plus_years_required",
    "mlops_cloud_or_platform_ownership",
    "kubernetes_terraform_docker_core",
    "research_training_or_publications",
    "unsupported_scale_or_ownership_claims",
    "clearance_or_independent_blocker",
)
"""P-5 materially-unsupported requirement categories."""

MINIMUM_UNSUPPORTED_REQUIREMENTS: Final = 2
"""P-5: a senior title alone can never block."""

SCORED_CLASSIFICATIONS: Final[frozenset[MatchClassification]] = frozenset(
    {
        MatchClassification.STRONG_MATCH,
        MatchClassification.PLAUSIBLE_MATCH,
        MatchClassification.STRETCH,
        MatchClassification.AVOID,
    }
)
"""INSUFFICIENT_EVIDENCE is excluded: it is reachable only through the C-4 cap."""


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


class EvidenceTierWeights(FrozenModel):
    """P-1 evidence-tier multipliers.

    Applied only within `verified_technical_skill_alignment` and capped at that
    dimension's weight (E-1). Tier ordinal does not imply weight order: Tier 3 outranks
    Tier 2 under this policy (E-8).
    """

    TIER_1_VERIFIED_SKILL: float
    TIER_2_PROJECT_EVIDENCE: float
    TIER_3_EMPLOYMENT_EVIDENCE: float
    TIER_4_TRAINING: float

    @model_validator(mode="after")
    def _check_multipliers(self) -> "EvidenceTierWeights":
        values = {name: getattr(self, name) for name in self.__class__.model_fields}
        for name, value in values.items():
            if not 0.0 < value <= 1.0:
                raise ValueError(f"tier multiplier {name} must be in (0.0, 1.0], got {value}")
        if self.TIER_1_VERIFIED_SKILL != 1.0:
            raise ValueError("TIER_1_VERIFIED_SKILL is the reference tier and must equal 1.0")
        if max(values.values()) != self.TIER_1_VERIFIED_SKILL:
            raise ValueError("no tier may exceed TIER_1_VERIFIED_SKILL")
        return self


class ClassificationBand(FrozenModel):
    """One classification band. Both bounds inclusive."""

    classification: MatchClassification
    min_score: int
    max_score: int

    @model_validator(mode="after")
    def _check_band(self) -> "ClassificationBand":
        if self.min_score > self.max_score:
            raise ValueError(f"{self.classification}: min_score exceeds max_score")
        if self.min_score < MIN_SCORE or self.max_score > MAX_SCORE:
            raise ValueError(f"{self.classification}: band falls outside {MIN_SCORE}-{MAX_SCORE}")
        return self


class ClassificationThresholds(FrozenModel):
    """P-2 global classification bands. Must tile 0-100 with no gap and no overlap."""

    bands: tuple[ClassificationBand, ...]

    @model_validator(mode="after")
    def _check_tiling(self) -> "ClassificationThresholds":
        present = {band.classification for band in self.bands}
        if len(present) != len(self.bands):
            raise ValueError("duplicate classification in thresholds")
        if present != SCORED_CLASSIFICATIONS:
            missing = sorted(c.value for c in SCORED_CLASSIFICATIONS - present)
            unexpected = sorted(c.value for c in present - SCORED_CLASSIFICATIONS)
            raise ValueError(
                f"classification bands are wrong. missing={missing} unexpected={unexpected}"
            )
        ordered = sorted(self.bands, key=lambda b: b.min_score)
        if ordered[0].min_score != MIN_SCORE:
            raise ValueError(f"the lowest classification band must begin at {MIN_SCORE}")
        if ordered[-1].max_score != MAX_SCORE:
            raise ValueError(f"the highest classification band must end at {MAX_SCORE}")
        for lower, upper in zip(ordered, ordered[1:], strict=False):
            if lower.max_score + 1 != upper.min_score:
                raise ValueError(
                    "classification bands must tile with no gap and no overlap: "
                    f"{lower.classification} ends at {lower.max_score} but "
                    f"{upper.classification} begins at {upper.min_score}"
                )
        return self


class SeniorityBand(FrozenModel):
    """One P-3 seniority point band."""

    points: int
    description: str


class SeniorityBands(FrozenModel):
    """P-3 seniority and documented-evidence compatibility bands, 15 points."""

    bands: tuple[SeniorityBand, ...]

    @model_validator(mode="after")
    def _check_bands(self) -> "SeniorityBands":
        points = [band.points for band in self.bands]
        if tuple(points) != APPROVED_SENIORITY_POINTS:
            raise ValueError(
                f"seniority point bands must be {list(APPROVED_SENIORITY_POINTS)} "
                f"in descending order, got {points}"
            )
        if any(not band.description.strip() for band in self.bands):
            raise ValueError("every seniority band requires a description")
        return self


class ReportDisplayPolicy(FrozenModel):
    """P-6 report section order and the anti-headline rule."""

    order: tuple[str, ...]
    score_never_headline: bool

    @model_validator(mode="after")
    def _check_order(self) -> "ReportDisplayPolicy":
        if self.order != APPROVED_REPORT_ORDER:
            raise ValueError(
                "report display order must be the approved eight-step sequence, "
                f"got {list(self.order)}"
            )
        if not self.score_never_headline:
            raise ValueError("score_never_headline must be true; the score is never a headline")
        return self


class ScoringConfig(FrozenModel):
    """Weighted dimensions plus the approved P-1, P-2, P-3, and P-6 policy."""

    weights: dict[str, int]
    evidence_tier_weighting: EvidenceTierWeights
    match_classification_thresholds: ClassificationThresholds
    seniority_bands: SeniorityBands
    report_display: ReportDisplayPolicy
    unresolved_policy: dict[str, Any]

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

    @field_validator("unresolved_policy")
    @classmethod
    def _check_policy_keys(cls, value: dict[str, Any]) -> dict[str, Any]:
        expected = frozenset(REQUIRED_UNRESOLVED_POLICY_KEYS)
        keys = frozenset(value)
        if keys != expected:
            missing = sorted(expected - keys)
            unexpected = sorted(keys - expected)
            raise ValueError(
                "unresolved_policy must declare exactly the approved gate keys. "
                f"missing={missing} unexpected={unexpected}"
            )
        return value

    def unresolved_keys(self) -> tuple[str, ...]:
        """Return gate keys still awaiting owner approval, in the approved order."""
        return tuple(
            name
            for name in REQUIRED_UNRESOLVED_POLICY_KEYS
            if self.unresolved_policy.get(name) == UNRESOLVED
        )


class CompensationBand(FrozenModel):
    """One compensation band. Lower bound inclusive, upper bound exclusive."""

    classification: SalaryCompatibility
    min_usd: int | None
    max_usd: int | None
    hard_blocker: bool
    points: int
    report_note: str


class CompensationConfig(FrozenModel):
    """Compensation policy (D-3, A-2, P-4). Bands tile the range with no gap or overlap."""

    currency: Literal["USD"]
    bands: tuple[CompensationBand, ...]
    contract_points: int
    unknown_points: int
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

    @model_validator(mode="after")
    def _check_points(self) -> "CompensationConfig":
        for value, label in (
            (self.contract_points, "contract_points"),
            (self.unknown_points, "unknown_points"),
        ):
            if value != 0:
                raise ValueError(f"{label} must be 0 under owner decision P-4, got {value}")
        ordered = sorted(self.bands, key=lambda b: (b.min_usd is not None, b.min_usd or 0))
        for band in ordered:
            if band.points < 0:
                raise ValueError(f"{band.classification}: points must not be negative")
        for lower, upper in zip(ordered, ordered[1:], strict=False):
            if lower.points > upper.points:
                raise ValueError(
                    "compensation points must not decrease as the band rises: "
                    f"{lower.classification}={lower.points} exceeds "
                    f"{upper.classification}={upper.points}"
                )
        blocking = [band for band in self.bands if band.hard_blocker]
        for band in blocking:
            if band.points != 0:
                raise ValueError(f"{band.classification}: a blocking band must score 0 points")
        return self


class BlockerRule(FrozenModel):
    """One hard blocker and whether it is enabled."""

    code: BlockerCode
    enabled: bool


class SeniorScopeRule(FrozenModel):
    """P-5 firing conditions for SENIOR_SCOPE_MATERIALLY_UNSUPPORTED.

    Both conditions are required. A senior title alone is a SENIORITY_MISMATCH concern,
    never an automatic hard blocker. This rule is NOT equivalent to P-3's 0-point
    seniority band: a role may score 0 for seniority without firing this blocker.
    """

    requires_explicit_senior_scope: bool
    minimum_unsupported_requirements: int
    senior_title_tokens: tuple[str, ...]
    unsupported_requirement_categories: tuple[str, ...]

    @model_validator(mode="after")
    def _check_rule(self) -> "SeniorScopeRule":
        if not self.requires_explicit_senior_scope:
            raise ValueError(
                "requires_explicit_senior_scope must be true: the blocker requires an "
                "explicit senior scope in addition to unsupported requirements"
            )
        if self.minimum_unsupported_requirements < MINIMUM_UNSUPPORTED_REQUIREMENTS:
            raise ValueError(
                "minimum_unsupported_requirements must be at least "
                f"{MINIMUM_UNSUPPORTED_REQUIREMENTS}: a senior title alone can never block"
            )
        if not self.senior_title_tokens:
            raise ValueError("senior_title_tokens must not be empty")
        if self.unsupported_requirement_categories != APPROVED_SENIOR_SCOPE_CATEGORIES:
            raise ValueError(
                "unsupported_requirement_categories must be the seven approved categories, "
                f"got {list(self.unsupported_requirement_categories)}"
            )
        return self


class BlockerConfig(FrozenModel):
    """Hard blocker policy (D-5, D-6, D-8, D-10, P-5)."""

    degree_equivalency_phrases: tuple[str, ...]
    blockers: tuple[BlockerRule, ...]
    senior_scope: SeniorScopeRule

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
    """The complete assessment policy: structurally valid, not necessarily ready to run."""

    scoring: ScoringConfig
    compensation: CompensationConfig
    blockers: BlockerConfig
    risk_flags: RiskFlagConfig

    @model_validator(mode="after")
    def _check_dimension_ceilings(self) -> "AssessmentConfig":
        weights = self.scoring.weights
        seniority_max = max(band.points for band in self.scoring.seniority_bands.bands)
        if seniority_max != weights["seniority_and_documented_evidence_compatibility"]:
            raise ValueError(
                "the highest seniority band must equal the dimension weight "
                f"({weights['seniority_and_documented_evidence_compatibility']}), "
                f"got {seniority_max}"
            )
        compensation_max = max(band.points for band in self.compensation.bands)
        if compensation_max != weights["compensation_compatibility"]:
            raise ValueError(
                "the highest compensation band must equal the dimension weight "
                f"({weights['compensation_compatibility']}), got {compensation_max}"
            )
        return self

    def evidence_tier_cap_points(self) -> int:
        """The point ceiling tier multipliers may reach (rule E-1)."""
        return self.scoring.weights["verified_technical_skill_alignment"]

    def unresolved_keys(self) -> tuple[str, ...]:
        """Return every policy key still awaiting owner approval, in the approved order."""
        return self.scoring.unresolved_keys()

    def require_ready(self) -> None:
        """Raise unless every policy decision needed to execute an assessment is approved."""
        unresolved = self.unresolved_keys()
        if unresolved:
            raise AssessmentPolicyUnresolvedError(unresolved)
