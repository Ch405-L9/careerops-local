"""Canonical parity.

Line numbers are never parsed. These tests read stable labelled Markdown sections, and
compare them against code-owned expected lists documented as derived from their source
document. Any drift in RiskFlag, Recommendation, or ValidationStatus fails the build.
"""

import re
from pathlib import Path

from careerops.config.loader import load_assessment_config
from careerops.config.schema import REQUIRED_UNRESOLVED_POLICY_KEYS
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


def test_approved_record_states_its_standing(repo_root: Path) -> None:
    """The 2026-09-25 owner-decision record must declare status, date, owner, and scope."""
    markdown = (repo_root / "docs" / "SCORING_DECISIONS.md").read_text(encoding="utf-8")
    for required in (
        "**Status:** approved",
        "**Date:** 2026-09-25",
        "**Owner:** Anthony Grant",
        "resolves the prior **A-3**",
        "adds **P-3 through P-6**",
        "does not supersede or modify any canonical Markdown file",
        "No canonical Markdown source is changed or superseded by this record",
        "active implementation authority",
    ):
        assert required in markdown, f"approved record is missing: {required!r}"


def test_approved_record_states_seniority_blocker_non_equivalence(repo_root: Path) -> None:
    """P-3's 0-point band and P-5's blocker must be declared non-equivalent."""
    markdown = (repo_root / "docs" / "SCORING_DECISIONS.md").read_text(encoding="utf-8")
    section = _section(markdown, "Cross-reference: P-3 and P-5 are not equivalent")
    assert "not equivalent" in section
    assert "without firing a blocker" in section
    assert "at least two" in section


def test_no_canonical_document_was_modified(repo_root: Path) -> None:
    """Phase 1A modifies no canonical Markdown file. Verified by content, not by git."""
    guardrails = (repo_root / "PROJECT_GUARDRAILS.md").read_text(encoding="utf-8")
    assert "FALLBACK_80K_TO_85K" not in guardrails
    prompt = (repo_root / "PROMPT_PHASE_0.md").read_text(encoding="utf-8")
    assert "FALLBACK_80K_TO_89K" in prompt, (
        "PROMPT_PHASE_0.md must retain its original wording; the decision record supersedes "
        "it without editing it"
    )


# ============================================================ policy parity (P-1..P-6)
#
# Each test below binds a config/*.yaml value to a labelled section of the approved
# owner-decision record. Line numbers are never parsed. There are exactly seven
# parity-parsed policy sections; the P-3/P-5 non-equivalence requirement is asserted as
# decision-record text above, not as an eighth data section.

NAMED_VALUE = re.compile(r"^- ([A-Z_0-9]+): ([0-9.]+)$", re.MULTILINE)
NAMED_RANGE = re.compile(r"^- ([A-Z_]+): (\d+)-(\d+)$", re.MULTILINE)
POINT_BAND = re.compile(r"^- (\d+): \S", re.MULTILINE)
CATEGORY = re.compile(r"^- category: ([a-z_]+)$", re.MULTILINE)
SETTING = re.compile(r"^- ([a-z_]+): (\S+)$", re.MULTILINE)
NUMBERED = re.compile(r"^\d+\. (.+?)\s*$", re.MULTILINE)


def _record(repo_root: Path) -> str:
    return (repo_root / "docs" / "SCORING_DECISIONS.md").read_text(encoding="utf-8")


def test_evidence_tier_multipliers_match_the_decision_record(
    repo_root: Path, config_dir: Path
) -> None:
    section = _section(_record(repo_root), "Approved evidence-tier multipliers")
    documented = {name: float(value) for name, value in NAMED_VALUE.findall(section)}
    weights = load_assessment_config(config_dir).scoring.evidence_tier_weighting
    assert documented == {tier.value: getattr(weights, tier.value) for tier in EvidenceTier}


def test_classification_thresholds_match_the_decision_record(
    repo_root: Path, config_dir: Path
) -> None:
    section = _section(_record(repo_root), "Approved classification thresholds")
    documented = {name: (int(lo), int(hi)) for name, lo, hi in NAMED_RANGE.findall(section)}
    bands = load_assessment_config(config_dir).scoring.match_classification_thresholds.bands
    assert documented == {
        band.classification.value: (band.min_score, band.max_score) for band in bands
    }


def test_seniority_bands_match_the_decision_record(repo_root: Path, config_dir: Path) -> None:
    section = _section(_record(repo_root), "Approved seniority point bands")
    documented = [int(points) for points in POINT_BAND.findall(section)]
    bands = load_assessment_config(config_dir).scoring.seniority_bands.bands
    assert documented == [band.points for band in bands]


def test_compensation_points_match_the_decision_record(
    repo_root: Path, config_dir: Path
) -> None:
    section = _section(_record(repo_root), "Approved compensation point mapping")
    documented = {name: int(float(value)) for name, value in NAMED_VALUE.findall(section)}
    config = load_assessment_config(config_dir)
    actual = {band.classification.value: band.points for band in config.compensation.bands}
    actual["CONTRACT_REQUIRES_REVIEW"] = config.compensation.contract_points
    actual["UNKNOWN"] = config.compensation.unknown_points
    assert documented == actual


def test_senior_scope_rule_matches_the_decision_record(
    repo_root: Path, config_dir: Path
) -> None:
    section = _section(_record(repo_root), "Approved senior-scope firing conditions")
    settings = dict(SETTING.findall(section))
    documented_categories = CATEGORY.findall(section)
    rule = load_assessment_config(config_dir).blockers.senior_scope
    assert settings["requires_explicit_senior_scope"] == "true"
    assert int(settings["minimum_unsupported_requirements"]) == (
        rule.minimum_unsupported_requirements
    )
    assert tuple(documented_categories) == rule.unsupported_requirement_categories


def test_report_order_matches_the_decision_record(repo_root: Path, config_dir: Path) -> None:
    section = _section(_record(repo_root), "Approved report display order")
    documented = tuple(NUMBERED.findall(section))
    assert documented == load_assessment_config(config_dir).scoring.report_display.order


def test_unresolved_policy_keys_match_the_decision_record(
    repo_root: Path, config_dir: Path
) -> None:
    section = _section(_record(repo_root), "Unresolved policy keys")
    documented = tuple(NUMBERED.findall(section))
    assert documented == REQUIRED_UNRESOLVED_POLICY_KEYS
    assert documented == load_assessment_config(config_dir).unresolved_keys()
