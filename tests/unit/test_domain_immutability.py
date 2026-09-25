"""Domain-model invariants: frozen, closed, and tier-mandatory."""

import pytest
from pydantic import ValidationError

from careerops.domain import UNKNOWN
from careerops.domain.assessment import Assessment, TechnologyMatch
from careerops.domain.candidate import WorkPreferences
from careerops.domain.job import (
    CompanyFacts,
    CompensationFacts,
    JobProvenance,
    NormalizedJob,
    WorkArrangementFacts,
)
from careerops.enums import (
    EvidenceTier,
    MatchClassification,
    Recommendation,
    ValidationStatus,
)
from fixtures.dossier_synthetic import synthetic_dossier


def test_candidate_dossier_is_frozen() -> None:
    dossier = synthetic_dossier()
    with pytest.raises(ValidationError):
        dossier.name = "Changed"  # type: ignore[misc]


def test_domain_models_forbid_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        CompanyFacts(company_name="Synthetic Systems", surprise_field="x")  # type: ignore[call-arg]


def test_technology_match_requires_a_tier() -> None:
    """D-7: an untiered technology match must be unconstructable."""
    with pytest.raises(ValidationError):
        TechnologyMatch(technology="Python", evidence_reference="ref")  # type: ignore[call-arg]

    match = TechnologyMatch(
        technology="Python",
        tier=EvidenceTier.TIER_1_VERIFIED_SKILL,
        evidence_reference="verified skills list",
    )
    assert match.tier is EvidenceTier.TIER_1_VERIFIED_SKILL


def test_work_authorization_accepts_only_unknown() -> None:
    """D-5: no authorization value may be stored in tracked project data."""
    preferences = WorkPreferences(
        target_country="United States",
        remote_preference="Preferred",
        relocation_willing=True,
        relocation_assistance_preferred=True,
        preferred_base_salary_min_usd=90_000,
        exclusion_floor_base_salary_usd=80_000,
    )
    assert preferences.work_authorization == UNKNOWN

    with pytest.raises(ValidationError):
        WorkPreferences(
            target_country="United States",
            remote_preference="Preferred",
            relocation_willing=True,
            relocation_assistance_preferred=True,
            preferred_base_salary_min_usd=90_000,
            exclusion_floor_base_salary_usd=80_000,
            work_authorization="AUTHORIZED",  # type: ignore[arg-type]
        )


def test_absent_listing_values_default_to_unknown() -> None:
    job = NormalizedJob(
        job_id="synthetic-1",
        job_title="Applied Engineer",
        provenance=JobProvenance(source_platform="wellfound"),
        company=CompanyFacts(company_name="Synthetic Systems"),
        work=WorkArrangementFacts(),
        compensation=CompensationFacts(),
    )
    assert job.company.company_website == UNKNOWN
    assert job.compensation.base_salary_min_usd == UNKNOWN
    assert job.education_requirements == UNKNOWN
    assert job.required_technologies == ()


def test_assessment_defaults_carry_no_score() -> None:
    """Phase 1A has no scoring, so an assessment must be constructable without one."""
    assessment = Assessment(
        job_id="synthetic-1",
        validation_status=ValidationStatus.INSUFFICIENT_EVIDENCE,
        classification=MatchClassification.INSUFFICIENT_EVIDENCE,
        recommendation=Recommendation.HOLD_FOR_MISSING_COMPENSATION_OR_LOCATION,
    )
    assert assessment.score is None
    assert assessment.blockers == ()
    assert assessment.compensation is None
