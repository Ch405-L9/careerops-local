"""Dossier loader behaviour.

The loader is read-only, performs no I/O, and is deterministic. Parity against
CANONICAL_CANDIDATE_DOSSIER.md is asserted separately in
tests/parity/test_canonical_dossier_parity.py.
"""

import ast
from pathlib import Path

import pytest
from pydantic import ValidationError

from careerops.domain.candidate import CandidateDossier
from careerops.dossier.approved_dossier import (
    EMPLOYMENT_EVIDENCE,
    EXPLICIT_SKILL_TERMS,
    PROJECT_EVIDENCE,
    approved_dossier,
    candidate_terms,
)
from careerops.dossier.loader import (
    ApprovedDossierLoader,
    DossierLoader,
    load_approved_dossier,
)
from careerops.enums import EvidenceTier

DOSSIER_MODULES = ("approved_dossier.py", "loader.py")


def _dossier_source(src_dir: Path) -> list[tuple[str, str]]:
    package = src_dir / "careerops" / "dossier"
    return [
        (name, (package / name).read_text(encoding="utf-8")) for name in DOSSIER_MODULES
    ]


# ------------------------------------------------------------------- the interface


def test_loader_satisfies_the_protocol() -> None:
    assert isinstance(ApprovedDossierLoader(), DossierLoader)


def test_loader_returns_a_candidate_dossier() -> None:
    assert isinstance(ApprovedDossierLoader().load(), CandidateDossier)


def test_convenience_accessor_agrees_with_the_loader() -> None:
    assert load_approved_dossier() == ApprovedDossierLoader().load()


def test_loader_names_what_it_is_a_copy_of() -> None:
    """A report must be able to cite provenance without the loader reading anything."""
    loader = ApprovedDossierLoader()
    assert loader.source_document == "CANONICAL_CANDIDATE_DOSSIER.md"
    assert loader.source_version == "1.0.0"


# ----------------------------------------------------------------------- purity


def test_loading_twice_yields_an_equal_dossier() -> None:
    """Pure: no clock, no randomness, no accumulated state."""
    assert approved_dossier() == approved_dossier()


def test_the_dossier_is_frozen_and_a_listing_cannot_change_it() -> None:
    dossier = load_approved_dossier()
    with pytest.raises(ValidationError):
        dossier.name = "Someone Else"  # type: ignore[misc]
    with pytest.raises(ValidationError):
        dossier.verified_skills = ()  # type: ignore[misc]


def test_the_dossier_package_performs_no_io(src_dir: Path) -> None:
    """No filesystem call, no path constant, no environment read (D-12, PROJECT_GUARDRAILS)."""
    for name, text in _dossier_source(src_dir):
        for token in (".open(", "open(", "Path(", "read_text", "os.environ", "getenv"):
            assert token not in text, f"{name} performs I/O via {token!r}"


def test_the_dossier_package_imports_no_io_module(src_dir: Path) -> None:
    banned = {"pathlib", "os", "io", "subprocess", "shutil", "glob", "urllib", "socket"}
    for name, text in _dossier_source(src_dir):
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots = {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                roots = {node.module.split(".")[0]}
            else:
                continue
            assert not roots & banned, f"{name} imports {sorted(roots & banned)}"


# ------------------------------------------------------------------- the content


def test_dossier_shape_is_exact() -> None:
    """Exact counts, never approximate: a dropped section must fail here."""
    dossier = load_approved_dossier()
    assert len(dossier.verified_skills) == 39
    assert len(dossier.project_evidence) == 3
    assert len(dossier.employment_evidence) == 4
    assert len(dossier.training_evidence) == 2
    assert len(dossier.target_role_families) == 11
    assert len(dossier.avoid_role_families) == 6
    assert len(dossier.prohibited_inferences) == 14


def test_every_verified_skill_is_tier_one() -> None:
    """D-7: the Verified skills section is Tier 1 evidence and nothing else."""
    tiers = {skill.tier for skill in load_approved_dossier().verified_skills}
    assert tiers == {EvidenceTier.TIER_1_VERIFIED_SKILL}


def test_project_evidence_carries_its_technologies() -> None:
    """Tier 2 evidence is available: each project declares an explicit technology line."""
    for project in PROJECT_EVIDENCE:
        assert project.technologies, f"{project.name} lost its technologies"
    assert "MCP" in dict((p.name, p.technologies) for p in PROJECT_EVIDENCE)[
        "C.Walts — Hybrid Retrieval and Evaluation System"
    ]


def test_employment_evidence_declares_no_technologies() -> None:
    """Recorded limit, not an oversight: see the approved_dossier module docstring.

    The canonical employment entries state no technology list, so transcribing one would
    invent a value. Tier 3 technology matching stays unavailable until an owner-approved
    explicit list exists.
    """
    for job in EMPLOYMENT_EVIDENCE:
        assert job.technologies == ()


def test_aws_never_appears_as_employment_technology_evidence() -> None:
    """E-6 and the prohibited-inference list: AWS is responsibility prose, not a match."""
    for job in EMPLOYMENT_EVIDENCE:
        assert not [tech for tech in job.technologies if "AWS" in tech]


def test_work_authorization_remains_unknown() -> None:
    """D-5: no authorization value may be stored, even in the approved dossier."""
    assert load_approved_dossier().preferences.work_authorization == "UNKNOWN"


def test_no_total_years_of_experience_is_derivable() -> None:
    """D-4: employment dates are opaque display strings, never subtracted."""
    for job in EMPLOYMENT_EVIDENCE:
        assert isinstance(job.start, str)
        assert isinstance(job.end, str)
    assert not [f for f in CandidateDossier.model_fields if "year" in f.lower()]


def test_the_transcription_still_holds_only_verbatim_skill_names() -> None:
    """Explicit terms live in EXPLICIT_SKILL_TERMS, never in the transcription itself."""
    tier_one = {skill.name for skill in load_approved_dossier().verified_skills}
    assert "Model Context Protocol (MCP)" in tier_one
    assert "MCP" not in tier_one


# ------------------------------------------------------------ the candidate index


def _index() -> dict[str, set]:
    index: dict[str, set] = {}
    for entry in candidate_terms():
        index.setdefault(entry.term, set()).add(entry.tier)
    return index


def test_explicit_terms_reach_tier_one() -> None:
    """The point of the approved table: MCP now matches at Tier 1, not Tier 2 with a gap."""
    index = _index()
    for term in ("MCP", "Model Context Protocol", "Ubuntu", "Windows 10", "Windows 11"):
        assert EvidenceTier.TIER_1_VERIFIED_SKILL in index[term], (
            f"{term!r} is not reachable at Tier 1"
        )


def test_verbatim_compound_names_remain_matchable() -> None:
    """Declaring explicit terms adds reachability; it never removes any."""
    index = _index()
    for term in ("Model Context Protocol (MCP)", "Ubuntu/Linux", "Windows 10/11"):
        assert EvidenceTier.TIER_1_VERIFIED_SKILL in index[term]


def test_project_technologies_reach_tier_two() -> None:
    index = _index()
    assert EvidenceTier.TIER_2_PROJECT_EVIDENCE in index["Kotlin"]
    assert EvidenceTier.TIER_2_PROJECT_EVIDENCE in index["ChromaDB"]


def test_a_term_may_hold_several_tiers_and_the_index_does_not_rank_them() -> None:
    """E-3 best-tier-wins is the matcher's job, not the index's."""
    assert _index()["MCP"] == {
        EvidenceTier.TIER_1_VERIFIED_SKILL,
        EvidenceTier.TIER_2_PROJECT_EVIDENCE,
    }


def test_no_employment_term_enters_the_index() -> None:
    """Tier 3 stays empty while employment technologies are untranscribed."""
    assert not [
        entry
        for entry in candidate_terms()
        if entry.tier is EvidenceTier.TIER_3_EMPLOYMENT_EVIDENCE
    ]


def test_every_index_entry_cites_a_dossier_section(repo_root: Path) -> None:
    """E-5: every match discloses an exact evidence reference, by label not line number."""
    markdown = (repo_root / "CANONICAL_CANDIDATE_DOSSIER.md").read_text(encoding="utf-8")
    for entry in candidate_terms():
        assert entry.evidence_reference.startswith(
            ("Verified skills — ", "Project evidence — ", "Employment evidence — ")
        )
        label = entry.evidence_reference.split(" — ", 1)[1]
        assert label in markdown, f"{label!r} is not a section of the canonical document"


def test_index_terms_are_never_normalized() -> None:
    """Normalization is the matcher's, using only the four approved A-6 steps."""
    raw = {entry.term for entry in candidate_terms()}
    assert "Python" in raw and "python" not in raw
    assert "ChromaDB" in raw and "chromadb" not in raw


def test_the_index_is_deterministic() -> None:
    assert candidate_terms() == candidate_terms()


def test_explicit_term_table_is_data_only() -> None:
    """No runtime derivation: the table is a literal dict of literal tuples."""
    assert isinstance(EXPLICIT_SKILL_TERMS, dict)
    assert all(isinstance(v, tuple) for v in EXPLICIT_SKILL_TERMS.values())
    assert len(EXPLICIT_SKILL_TERMS) == 3
