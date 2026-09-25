"""Single definition site for every CareerOps Local enum.

`RiskFlag`, `Recommendation`, and `ValidationStatus` are derived from PROJECT_GUARDRAILS.md.
`SalaryCompatibility` and `EvidenceTier` are derived from docs/SCORING_DECISIONS.md, the
owner-approved implementation decision record dated 2026-09-25.

tests/parity/test_canonical_enum_parity.py fails if any of these drift from their source
document. No enum may be defined or aliased anywhere else in this package.
"""

from enum import StrEnum

__all__ = [
    "BlockerCode",
    "EmploymentType",
    "EvidenceTier",
    "MatchClassification",
    "Recommendation",
    "RelocationStatus",
    "RiskFlag",
    "SalaryCompatibility",
    "ValidationStatus",
    "WorkArrangementType",
]


class ValidationStatus(StrEnum):
    """Evidence status. Source: PROJECT_GUARDRAILS.md, "Evidence statuses"."""

    VERIFIED = "VERIFIED"
    CONCERN = "CONCERN"
    UNVERIFIED = "UNVERIFIED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class MatchClassification(StrEnum):
    """Overall match classification. Thresholds are UNRESOLVED (A-3)."""

    STRONG_MATCH = "STRONG_MATCH"
    PLAUSIBLE_MATCH = "PLAUSIBLE_MATCH"
    STRETCH = "STRETCH"
    AVOID = "AVOID"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class Recommendation(StrEnum):
    """Human review label. Source: PROJECT_GUARDRAILS.md, "Human-in-the-loop rule".

    No recommendation means "apply automatically".
    """

    REVIEW_FOR_APPLICATION = "REVIEW_FOR_APPLICATION"
    RESEARCH_COMPANY_FIRST = "RESEARCH_COMPANY_FIRST"
    REQUEST_DETAILS_FROM_RECRUITER = "REQUEST_DETAILS_FROM_RECRUITER"
    HOLD_FOR_MISSING_COMPENSATION_OR_LOCATION = "HOLD_FOR_MISSING_COMPENSATION_OR_LOCATION"
    DO_NOT_APPLY = "DO_NOT_APPLY"


class WorkArrangementType(StrEnum):
    US_REMOTE = "US_REMOTE"
    STATE_RESTRICTED_REMOTE = "STATE_RESTRICTED_REMOTE"
    TIME_ZONE_RESTRICTED_REMOTE = "TIME_ZONE_RESTRICTED_REMOTE"
    HYBRID = "HYBRID"
    ON_SITE = "ON_SITE"
    UNKNOWN = "UNKNOWN"


class RelocationStatus(StrEnum):
    PROVIDED = "PROVIDED"
    REQUIRED = "REQUIRED"
    PREFERRED = "PREFERRED"
    NOT_MENTIONED = "NOT_MENTIONED"
    UNKNOWN = "UNKNOWN"


class EmploymentType(StrEnum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    CONTRACT_TO_HIRE = "CONTRACT_TO_HIRE"
    TEMPORARY = "TEMPORARY"
    INTERNSHIP = "INTERNSHIP"
    UNKNOWN = "UNKNOWN"


class SalaryCompatibility(StrEnum):
    """Compensation band. Source: docs/SCORING_DECISIONS.md, decision D-3.

    Supersedes the member list in PROMPT_PHASE_0.md, which named FALLBACK_80K_TO_89K and had
    no BELOW_PREFERRED_REVIEW member. Hourly and contract compensation is never annualized.
    """

    TARGET_90K_PLUS = "TARGET_90K_PLUS"
    FALLBACK_80K_TO_85K = "FALLBACK_80K_TO_85K"
    BELOW_PREFERRED_REVIEW = "BELOW_PREFERRED_REVIEW"
    BELOW_80K = "BELOW_80K"
    CONTRACT_REQUIRES_REVIEW = "CONTRACT_REQUIRES_REVIEW"
    UNKNOWN = "UNKNOWN"


class EvidenceTier(StrEnum):
    """Provenance tier of a technology match. Source: docs/SCORING_DECISIONS.md, decision D-7.

    Reports must disclose which tier produced every technology match. No tier may create an
    unverified skill. Relative tier weighting is UNRESOLVED (A-4).
    """

    TIER_1_VERIFIED_SKILL = "TIER_1_VERIFIED_SKILL"
    TIER_2_PROJECT_EVIDENCE = "TIER_2_PROJECT_EVIDENCE"
    TIER_3_EMPLOYMENT_EVIDENCE = "TIER_3_EMPLOYMENT_EVIDENCE"
    TIER_4_TRAINING = "TIER_4_TRAINING"


class BlockerCode(StrEnum):
    """The complete hard blocker set.

    Work authorization is deliberately absent: a candidate UNKNOWN can never hard-block (D-5).
    Plain absence of company evidence is deliberately absent: missing evidence is not negative
    evidence (D-6). No salary-override code exists (D-10).
    """

    CLEARANCE_REQUIRED_WITHOUT_CANDIDATE_EVIDENCE = "CLEARANCE_REQUIRED_WITHOUT_CANDIDATE_EVIDENCE"
    MANDATORY_DEGREE_WITHOUT_EQUIVALENCY = "MANDATORY_DEGREE_WITHOUT_EQUIVALENCY"
    EXPLICIT_BASE_SALARY_BELOW_80K = "EXPLICIT_BASE_SALARY_BELOW_80K"
    RESEARCH_HEAVY_UNVERIFIED_QUALIFICATIONS = "RESEARCH_HEAVY_UNVERIFIED_QUALIFICATIONS"
    SENIOR_SCOPE_MATERIALLY_UNSUPPORTED = "SENIOR_SCOPE_MATERIALLY_UNSUPPORTED"
    PAYMENT_OR_IDENTITY_REQUEST = "PAYMENT_OR_IDENTITY_REQUEST"
    AFFIRMATIVE_COMPANY_IDENTITY_CONTRADICTION = "AFFIRMATIVE_COMPANY_IDENTITY_CONTRADICTION"


class RiskFlag(StrEnum):
    """Mandatory risk flags. Source: PROJECT_GUARDRAILS.md, "Mandatory risk flags".

    Exactly 24 members. The band 86,000-89,999 raises no flag from this set and does not
    reuse SALARY_CONFLICT (A-2).
    """

    PAYMENT_REQUEST = "PAYMENT_REQUEST"
    SENSITIVE_IDENTITY_REQUEST = "SENSITIVE_IDENTITY_REQUEST"
    PERSONAL_EMAIL_DOMAIN_RECRUITER = "PERSONAL_EMAIL_DOMAIN_RECRUITER"
    URL_DOMAIN_MISMATCH = "URL_DOMAIN_MISMATCH"
    MISSING_COMPANY_WEBSITE = "MISSING_COMPANY_WEBSITE"
    UNVERIFIABLE_COMPANY = "UNVERIFIABLE_COMPANY"
    COMPENSATION_OUTLIER = "COMPENSATION_OUTLIER"
    JOB_DESCRIPTION_TOO_VAGUE = "JOB_DESCRIPTION_TOO_VAGUE"
    EXCESSIVE_URGENCY = "EXCESSIVE_URGENCY"
    CLEARANCE_REQUIRED = "CLEARANCE_REQUIRED"
    DEGREE_REQUIRED = "DEGREE_REQUIRED"
    WORK_AUTHORIZATION_RESTRICTION = "WORK_AUTHORIZATION_RESTRICTION"
    LOCATION_CONFLICT = "LOCATION_CONFLICT"
    SALARY_CONFLICT = "SALARY_CONFLICT"
    STAFFING_INTERMEDIARY = "STAFFING_INTERMEDIARY"
    END_CLIENT_UNKNOWN = "END_CLIENT_UNKNOWN"
    POSSIBLE_STALE_LISTING = "POSSIBLE_STALE_LISTING"
    POSSIBLE_DUPLICATE = "POSSIBLE_DUPLICATE"
    SENIORITY_MISMATCH = "SENIORITY_MISMATCH"
    RESEARCH_HEAVY_MISMATCH = "RESEARCH_HEAVY_MISMATCH"
    MISSING_COMPENSATION = "MISSING_COMPENSATION"
    RELOCATION_UNKNOWN = "RELOCATION_UNKNOWN"
    REMOTE_RESTRICTION_UNKNOWN = "REMOTE_RESTRICTION_UNKNOWN"
    REQUIRED_SKILL_GAP = "REQUIRED_SKILL_GAP"
