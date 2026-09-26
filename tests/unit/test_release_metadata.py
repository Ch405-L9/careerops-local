"""Release metadata consistency.

The version string exists in two places, and the changelog is a third record of it. These tests
make divergence a build failure rather than something a reader discovers later.

`pyproject.toml` is parsed with `tomllib` from the standard library. No dependency is added.
"""

import re
import tomllib
from pathlib import Path

import careerops

SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:a\d+|b\d+|rc\d+)?$")
RELEASE_HEADING = re.compile(r"^## \[(\d+\.\d+\.\d+(?:a\d+|b\d+|rc\d+)?)\] — (\d{4}-\d{2}-\d{2})$", re.MULTILINE)


def _pyproject(repo_root: Path) -> dict:
    with (repo_root / "pyproject.toml").open("rb") as handle:
        return tomllib.load(handle)


def _changelog(repo_root: Path) -> str:
    return (repo_root / "CHANGELOG.md").read_text(encoding="utf-8")


def test_package_version_matches_pyproject(repo_root: Path) -> None:
    assert careerops.__version__ == _pyproject(repo_root)["project"]["version"]


def test_version_is_a_valid_semver_prerelease(repo_root: Path) -> None:
    assert SEMVER.match(careerops.__version__), careerops.__version__


def test_changelog_exists_and_declares_its_format(repo_root: Path) -> None:
    text = _changelog(repo_root)
    assert "Keep a Changelog" in text
    assert "Semantic Versioning" in text


def test_changelog_documents_the_current_version(repo_root: Path) -> None:
    releases = dict(RELEASE_HEADING.findall(_changelog(repo_root)))
    assert careerops.__version__ in releases, (
        f"CHANGELOG.md has no entry for {careerops.__version__}; releases found: "
        f"{sorted(releases)}"
    )


def test_changelog_releases_are_newest_first(repo_root: Path) -> None:
    dates = [date for _, date in RELEASE_HEADING.findall(_changelog(repo_root))]
    assert dates == sorted(dates, reverse=True)


def test_changelog_keeps_an_unreleased_section(repo_root: Path) -> None:
    assert "## [Unreleased]" in _changelog(repo_root)


def test_changelog_restates_the_decision_support_boundary(repo_root: Path) -> None:
    """Every release preserves it, so the changelog states it once, before any entry."""
    preamble = _changelog(repo_root).split("## [Unreleased]", 1)[0]
    for phrase in (
        "never applies, messages, logs in, scrapes",
        "external action",
        "No release may invent a policy value",
    ):
        assert phrase in preamble, f"the changelog preamble is missing: {phrase!r}"


def test_changelog_states_the_remaining_gate(repo_root: Path) -> None:
    """A reader must be able to see readiness is still blocked without reading the code."""
    text = _changelog(repo_root)
    for key in (
        "seniority_band_selection_precedence",
        "compensation_range_selection_rule",
        "critical_unknown_detection_rule",
        "score_rounding_rule",
        "report_and_cli_score_display_scope",
    ):
        assert key in text


def test_architecture_document_names_the_current_record(repo_root: Path) -> None:
    """The architecture doc must cite the newest owner-decision record, not only the older one."""
    text = (repo_root / "docs" / "ARCHITECTURE.md").read_text(encoding="utf-8")
    assert "2026-09-26" in text
    assert "A-5 through A-7" in text


def test_no_document_still_calls_a_resolved_key_unresolved(repo_root: Path, src_dir: Path) -> None:
    """A-3 and A-4 were resolved by P-2 and P-1; nothing may still describe them as open."""
    targets = [repo_root / "docs" / "ARCHITECTURE.md", repo_root / "CHANGELOG.md"]
    targets += sorted(src_dir.rglob("*.py"))
    for path in targets:
        text = path.read_text(encoding="utf-8")
        for stale in ("UNRESOLVED (A-3)", "UNRESOLVED (A-4)"):
            assert stale not in text, f"{path} still describes {stale} as open"
