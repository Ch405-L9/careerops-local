"""Enum membership tests.

These assert the shape the rest of the system depends on. Parity against the source
documents is asserted separately in tests/parity/.
"""

from careerops import enums
from careerops.enums import (
    BlockerCode,
    EvidenceTier,
    MatchClassification,
    Recommendation,
    RiskFlag,
    SalaryCompatibility,
    ValidationStatus,
)

EXPECTED_RISK_FLAGS = 24


def test_risk_flag_count() -> None:
    assert len(RiskFlag) == EXPECTED_RISK_FLAGS


def test_salary_bands_match_owner_decision() -> None:
    """D-3: the approved band set, superseding PROMPT_PHASE_0.md."""
    assert {member.value for member in SalaryCompatibility} == {
        "TARGET_90K_PLUS",
        "FALLBACK_80K_TO_85K",
        "BELOW_PREFERRED_REVIEW",
        "BELOW_80K",
        "CONTRACT_REQUIRES_REVIEW",
        "UNKNOWN",
    }


def test_superseded_salary_member_is_absent() -> None:
    """The pre-decision member name must not survive anywhere."""
    assert "FALLBACK_80K_TO_89K" not in {member.value for member in SalaryCompatibility}


def test_evidence_tiers_are_the_four_approved_tiers() -> None:
    """D-7."""
    assert [member.value for member in EvidenceTier] == [
        "TIER_1_VERIFIED_SKILL",
        "TIER_2_PROJECT_EVIDENCE",
        "TIER_3_EMPLOYMENT_EVIDENCE",
        "TIER_4_TRAINING",
    ]


def test_work_authorization_is_not_a_blocker_code() -> None:
    """D-5: a candidate UNKNOWN can never hard-block."""
    assert not [code for code in BlockerCode if "AUTHORIZATION" in code.value]


def test_missing_company_evidence_is_not_a_blocker_code() -> None:
    """D-6: missing evidence is not negative evidence."""
    assert not [code for code in BlockerCode if "MISSING" in code.value]


def test_no_salary_override_blocker_code() -> None:
    """D-10: the override is deferred, so no code may exist for it."""
    assert not [code for code in BlockerCode if "OVERRIDE" in code.value]


def test_recommendation_has_no_automatic_apply_member() -> None:
    """No recommendation means "apply automatically"."""
    assert not [r for r in Recommendation if "AUTO" in r.value]


def test_insufficient_evidence_available_on_both_status_enums() -> None:
    """D-5 requires marking an assessment INSUFFICIENT_EVIDENCE."""
    assert ValidationStatus.INSUFFICIENT_EVIDENCE
    assert MatchClassification.INSUFFICIENT_EVIDENCE


def test_enums_module_is_the_only_definition_site() -> None:
    """No enum may be defined or aliased outside careerops.enums."""
    import pkgutil
    from enum import Enum

    import careerops

    declared = {name for name in enums.__all__}
    for module_info in pkgutil.walk_packages(careerops.__path__, "careerops."):
        if module_info.name == "careerops.enums":
            continue
        module = __import__(module_info.name, fromlist=["_"])
        for attr_name, attr in vars(module).items():
            if isinstance(attr, type) and issubclass(attr, Enum) and attr.__module__ != "enum":
                assert attr.__module__ == "careerops.enums", (
                    f"{module_info.name}.{attr_name} defines an enum outside careerops.enums"
                )
                assert attr_name in declared or attr_name.startswith("_")
