"""Technology-evidence matching (signatures only).

Every match carries the EvidenceTier that produced it, and reports must disclose it. No tier
may create an unverified skill. Relative tier weighting is UNRESOLVED (A-4).
"""

from careerops.domain.assessment import TechnologyMatch
from careerops.domain.candidate import CandidateDossier

__all__ = ["match_technologies"]


def match_technologies(
    required_technologies: tuple[str, ...],
    dossier: CandidateDossier,
) -> tuple[TechnologyMatch, ...]:
    """Match required technologies to candidate evidence, tagging each with its tier (D-7)."""
    raise NotImplementedError(
        "Technology matching is Phase 3 work and is not approved. Evidence-tier weighting "
        "remains UNRESOLVED in config/scoring.yaml (A-4)."
    )
