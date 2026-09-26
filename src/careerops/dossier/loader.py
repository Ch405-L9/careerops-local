"""Dossier loader interface and the approved read-only implementation.

There is deliberately:

* no filesystem call, no path constant, and no I/O of any kind. The approved dossier is a
  transcription in `careerops.dossier.approved_dossier`, bound to
  CANONICAL_CANDIDATE_DOSSIER.md by tests/parity/test_canonical_dossier_parity.py;
* no write path to any canonical document (CONTEXT_UPDATE_PROTOCOL.md);
* no mutation surface. `CandidateDossier` is frozen, and a listing can never modify it.

A future business-opportunity mode would supply a second implementation of this same Protocol
against a separately approved capabilities document. No implementation may merge personal and
business sources (D-2).
"""

from typing import Protocol, runtime_checkable

from careerops.domain.candidate import CandidateDossier
from careerops.dossier.approved_dossier import (
    CANONICAL_DOCUMENT,
    CANONICAL_VERSION,
    approved_dossier,
)

__all__ = ["ApprovedDossierLoader", "DossierLoader", "load_approved_dossier"]


@runtime_checkable
class DossierLoader(Protocol):
    """Supplies the approved candidate dossier.

    Implementations must be read-only. An implementation that writes to a canonical document
    violates CONTEXT_UPDATE_PROTOCOL.md.
    """

    def load(self) -> CandidateDossier:
        """Return the approved candidate dossier."""
        ...


class ApprovedDossierLoader:
    """Serves the transcribed canonical dossier. Read-only, and performs no I/O.

    `source_document` and `source_version` name what this loader is a copy of, so a report
    can cite provenance without the loader reading anything.
    """

    source_document: str = CANONICAL_DOCUMENT
    source_version: str = CANONICAL_VERSION

    def load(self) -> CandidateDossier:
        """Return the approved candidate dossier. Pure and deterministic."""
        return approved_dossier()


def load_approved_dossier() -> CandidateDossier:
    """Convenience accessor for the approved dossier."""
    return ApprovedDossierLoader().load()
