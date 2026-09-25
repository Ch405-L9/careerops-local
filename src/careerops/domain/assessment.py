"""Assessment result models.

`TechnologyMatch.tier` has no default, so an untiered technology match cannot be constructed
(D-7). Reports must disclose the tier behind every match.

`Assessment.score` is optional and unset in Phase 1A: no scoring logic exists, and
classification thresholds remain UNRESOLVED (A-3).
"""

from careerops.domain import FrozenModel
from careerops.enums import (
    BlockerCode,
    EvidenceTier,
    MatchClassification,
    Recommendation,
    RiskFlag,
    SalaryCompatibility,
    ValidationStatus,
)

__all__ = [
    "Assessment",
    "BlockerFinding",
    "CompensationAssessment",
    "RiskFlagFinding",
    "TechnologyMatch",
]


class TechnologyMatch(FrozenModel):
    """A technology the listing requires, matched to candidate evidence.

    `tier` is mandatory. No tier may create an unverified skill.
    """

    technology: str
    tier: EvidenceTier
    evidence_reference: str


class BlockerFinding(FrozenModel):
    """A hard blocker. Cannot be suppressed by any score."""

    code: BlockerCode
    rationale: str


class RiskFlagFinding(FrozenModel):
    """A raised risk flag and the reason it was raised."""

    flag: RiskFlag
    rationale: str


class CompensationAssessment(FrozenModel):
    """Compensation band outcome and the note a report must display."""

    classification: SalaryCompatibility
    report_note: str


class Assessment(FrozenModel):
    """A complete human-review assessment.

    Blockers are rendered before the score and are never hidden by one. No recommendation
    means "apply automatically".
    """

    job_id: str
    validation_status: ValidationStatus
    classification: MatchClassification
    recommendation: Recommendation
    blockers: tuple[BlockerFinding, ...] = ()
    risk_flags: tuple[RiskFlagFinding, ...] = ()
    technology_matches: tuple[TechnologyMatch, ...] = ()
    skill_gaps: tuple[str, ...] = ()
    unknowns: tuple[str, ...] = ()
    compensation: CompensationAssessment | None = None
    score: int | None = None
