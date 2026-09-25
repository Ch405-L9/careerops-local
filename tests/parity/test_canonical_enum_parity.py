"""Canonical parity.

Line numbers are never parsed. These tests read stable labelled Markdown sections, and
compare them against code-owned expected lists documented as derived from their source
document. Any drift in RiskFlag, Recommendation, or ValidationStatus fails the build.
"""

import re
from pathlib import Path

from careerops.enums import (
    EvidenceTier,
    Recommendation,
    RiskFlag,
    SalaryCompatibility,
    ValidationStatus,
)

BULLET_CODE = re.compile(r"^- `([A-Z_0-9]+)`\s*$", re.MULTILINE)
HEADING = re.compile(r"^(#{2,6}) (.+?)\s*$")
TABLE_FIRST_COLUMN = re.compile(r"^\| ([A-Z_]+) \|", re.MULTILINE)

# Derived from PROJECT_GUARDRAILS.md, section "Mandatory risk flags".
EXPECTED_RISK_FLAGS: tuple[str, ...] = tuple(flag.value for flag in RiskFlag)


def _section(markdown: str, heading: str) -> str:
    """Return the body of a section, located by its exact title at any heading level.

    Capture stops at the next heading of the same level or shallower, so a subsection is
    scoped correctly. Line numbers are never used.
    """
    body: list[str] = []
    capture_depth: int | None = None
    for line in markdown.splitlines():
        match = HEADING.match(line)
        if match is not None:
            depth = len(match.group(1))
            if match.group(2).strip() == heading:
                capture_depth = depth
                continue
            if capture_depth is not None and depth <= capture_depth:
                capture_depth = None
            continue
        if capture_depth is not None:
            body.append(line)
    if not body:
        raise AssertionError(f"section not found: {heading!r}")
    return "\n".join(body)


def test_risk_flags_match_guardrails(repo_root: Path) -> None:
    markdown = (repo_root / "PROJECT_GUARDRAILS.md").read_text(encoding="utf-8")
    documented = BULLET_CODE.findall(_section(markdown, "Mandatory risk flags"))
    assert len(documented) == 24
    assert [flag.value for flag in RiskFlag] == documented
    assert EXPECTED_RISK_FLAGS == tuple(documented)


def test_recommendations_match_guardrails(repo_root: Path) -> None:
    markdown = (repo_root / "PROJECT_GUARDRAILS.md").read_text(encoding="utf-8")
    documented = BULLET_CODE.findall(_section(markdown, "Human-in-the-loop rule"))
    assert [label.value for label in Recommendation] == documented


def test_validation_statuses_match_guardrails(repo_root: Path) -> None:
    markdown = (repo_root / "PROJECT_GUARDRAILS.md").read_text(encoding="utf-8")
    documented = TABLE_FIRST_COLUMN.findall(_section(markdown, "Evidence statuses"))
    assert [status.value for status in ValidationStatus] == documented


def test_salary_bands_match_the_decision_record(repo_root: Path) -> None:
    """A-1: SalaryCompatibility follows docs/SCORING_DECISIONS.md, not PROMPT_PHASE_0.md."""
    markdown = (repo_root / "docs" / "SCORING_DECISIONS.md").read_text(encoding="utf-8")
    section = _section(markdown, "Approved SalaryCompatibility enum members")
    documented = BULLET_CODE.findall(section)
    assert [band.value for band in SalaryCompatibility] == documented


def test_evidence_tiers_match_the_decision_record(repo_root: Path) -> None:
    markdown = (repo_root / "docs" / "SCORING_DECISIONS.md").read_text(encoding="utf-8")
    documented = BULLET_CODE.findall(_section(markdown, "Approved EvidenceTier enum members"))
    assert [tier.value for tier in EvidenceTier] == documented


def test_decision_record_states_its_standing(repo_root: Path) -> None:
    """The record must declare its date, its limited supersession, and its reconciliation path."""
    markdown = (repo_root / "docs" / "SCORING_DECISIONS.md").read_text(encoding="utf-8")
    for required in (
        "owner-approved implementation decision record dated 2026-09-25",
        "temporarily supersedes",
        "PROMPT_PHASE_0.md",
        "does **not** alter historical source content",
        "CONTEXT_UPDATE_PROTOCOL.md",
        "limited to Phase 1A",
    ):
        assert required in markdown, f"decision record is missing: {required!r}"


def test_no_canonical_document_was_modified(repo_root: Path) -> None:
    """Phase 1A modifies no canonical Markdown file. Verified by content, not by git."""
    guardrails = (repo_root / "PROJECT_GUARDRAILS.md").read_text(encoding="utf-8")
    assert "FALLBACK_80K_TO_85K" not in guardrails
    prompt = (repo_root / "PROMPT_PHASE_0.md").read_text(encoding="utf-8")
    assert "FALLBACK_80K_TO_89K" in prompt, (
        "PROMPT_PHASE_0.md must retain its original wording; the decision record supersedes "
        "it without editing it"
    )
