"""Hard blocker detection (signatures only).

Blockers are computed before any score and can never be suppressed by one.

Deliberately not blockers: a candidate work-authorization UNKNOWN (D-5), and plain absence of
company evidence (D-6). No salary-override path exists (D-10).
"""

from careerops.config.schema import BlockerConfig
from careerops.domain.assessment import BlockerFinding
from careerops.domain.candidate import CandidateDossier
from careerops.domain.job import NormalizedJob

__all__ = ["detect_blockers", "degree_requirement_is_blocking"]


def detect_blockers(
    job: NormalizedJob,
    dossier: CandidateDossier,
    config: BlockerConfig,
) -> tuple[BlockerFinding, ...]:
    """Return every hard blocker raised by this listing."""
    raise NotImplementedError(
        "Blocker detection is Phase 3 work and is not approved. Implementing it requires the "
        "owner decisions recorded in docs/SCORING_DECISIONS.md (D-5, D-6, D-8, D-10)."
    )


def degree_requirement_is_blocking(
    education_requirements: str,
    config: BlockerConfig,
) -> bool:
    """Return whether a stated degree requirement is a hard blocker (D-8).

    An explicit mandatory degree with none of the approved equivalency phrases blocks. With
    any approved phrase it does not. Ambiguous wording never blocks.
    """
    raise NotImplementedError(
        "Degree-equivalency evaluation is Phase 3 work and is not approved. The approved "
        "phrase list is in config/blockers.yaml (D-8)."
    )
