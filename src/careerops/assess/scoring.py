"""Deterministic scoring and classification (signatures only).

Scoring never overrides a blocker. Classification thresholds are UNRESOLVED (A-3) and
evidence-tier weighting is UNRESOLVED (A-4); no cutoff or weight may be invented.

Total years of experience is never calculated and never inferred from job dates (D-4).
"""

from careerops.config.schema import AssessmentConfig, CompensationConfig
from careerops.domain.assessment import Assessment, CompensationAssessment
from careerops.domain.candidate import CandidateDossier
from careerops.domain.job import NormalizedJob

__all__ = ["assess_compensation", "assess_job"]


def assess_compensation(
    job: NormalizedJob,
    config: CompensationConfig,
) -> CompensationAssessment:
    """Classify the listing's compensation into an approved band (D-3, A-2).

    Hourly and contract compensation is never annualized. Absent compensation yields UNKNOWN
    and MISSING_COMPENSATION, never a rejection.
    """
    raise NotImplementedError(
        "Compensation assessment is Phase 3 work and is not approved. The approved bands are "
        "in config/compensation.yaml (D-3, A-2)."
    )


def assess_job(
    job: NormalizedJob,
    dossier: CandidateDossier,
    config: AssessmentConfig,
) -> Assessment:
    """Produce a complete assessment.

    Callers must obtain `config` from `load_ready_assessment_config`, which refuses to return
    a configuration while any policy key is UNRESOLVED.
    """
    raise NotImplementedError(
        "Job assessment is Phase 3 work and is not approved. Match classification thresholds "
        "(A-3) and evidence-tier weighting (A-4) remain UNRESOLVED."
    )
