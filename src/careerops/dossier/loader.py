"""Dossier loader interface.

Phase 1A is interface-only by owner decision. There is deliberately:

* no implementation;
* no path constant and no filesystem call;
* no write path to any canonical document (CONTEXT_UPDATE_PROTOCOL.md).

A future business-opportunity mode would supply a second implementation of this same Protocol
against a separately approved capabilities document. No implementation may merge personal and
business sources (D-2).
"""

from typing import Protocol, runtime_checkable

from careerops.domain.candidate import CandidateDossier

__all__ = ["DossierLoader"]


@runtime_checkable
class DossierLoader(Protocol):
    """Supplies the approved candidate dossier.

    Implementations must be read-only. An implementation that writes to a canonical document
    violates CONTEXT_UPDATE_PROTOCOL.md.
    """

    def load(self) -> CandidateDossier:
        """Return the approved candidate dossier."""
        ...
