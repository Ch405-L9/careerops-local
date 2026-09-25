"""Tests against the shipped configuration in `config/`.

Structural validation must pass. Readiness validation must fail on exactly the two approved
unresolved keys, and on nothing else.
"""

from pathlib import Path

import pytest

from careerops.config.loader import load_assessment_config, load_ready_assessment_config
from careerops.config.schema import AssessmentPolicyUnresolvedError
from careerops.enums import BlockerCode, RiskFlag, SalaryCompatibility

APPROVED_PHRASES = (
    "or equivalent experience",
    "or equivalent practical experience",
    "or equivalent professional experience",
    "or equivalent work experience",
    "or related experience",
    "equivalent combination of education and experience",
    "education or equivalent experience",
    "degree preferred",
    "bachelor's preferred",
    "or demonstrable experience",
)


def test_shipped_configuration_parses_structurally(config_dir: Path) -> None:
    """Stage 1 must succeed so import, lint, type check, test, and CLI help all work."""
    config = load_assessment_config(config_dir)
    assert sum(config.scoring.weights.values()) == 100


def test_shipped_configuration_is_not_ready(config_dir: Path) -> None:
    """Stage 2 must fail while policy remains unapproved (A-3, A-4)."""
    with pytest.raises(AssessmentPolicyUnresolvedError) as excinfo:
        load_ready_assessment_config(config_dir)
    assert excinfo.value.unresolved_keys == (
        "match_classification_thresholds",
        "evidence_tier_weighting",
    )


def test_exactly_two_unresolved_keys(config_dir: Path) -> None:
    """No more, no fewer. A third unresolved key is a policy drift."""
    assert len(load_assessment_config(config_dir).unresolved_keys()) == 2


def test_seniority_dimension_uses_the_approved_name(config_dir: Path) -> None:
    """D-4."""
    weights = load_assessment_config(config_dir).scoring.weights
    assert weights["seniority_and_documented_evidence_compatibility"] == 15
    assert "seniority_years" not in weights


def test_bands_tile_the_range_without_gap_or_overlap(config_dir: Path) -> None:
    """D-3."""
    bands = load_assessment_config(config_dir).compensation.bands
    ordered = sorted(bands, key=lambda b: (b.min_usd is not None, b.min_usd or 0))
    assert ordered[0].min_usd is None
    assert ordered[-1].max_usd is None
    for lower, upper in zip(ordered, ordered[1:], strict=False):
        assert lower.max_usd == upper.min_usd


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        (79_999, SalaryCompatibility.BELOW_80K),
        (80_000, SalaryCompatibility.FALLBACK_80K_TO_85K),
        (85_999, SalaryCompatibility.FALLBACK_80K_TO_85K),
        (86_000, SalaryCompatibility.BELOW_PREFERRED_REVIEW),
        (89_999, SalaryCompatibility.BELOW_PREFERRED_REVIEW),
        (90_000, SalaryCompatibility.TARGET_90K_PLUS),
        (250_000, SalaryCompatibility.TARGET_90K_PLUS),
    ],
)
def test_every_boundary_amount_falls_in_exactly_one_band(
    config_dir: Path, amount: int, expected: SalaryCompatibility
) -> None:
    """Computed in the test, not in the package: Phase 1A implements no band lookup."""
    bands = load_assessment_config(config_dir).compensation.bands
    matched = [
        band
        for band in bands
        if (band.min_usd is None or amount >= band.min_usd)
        and (band.max_usd is None or amount < band.max_usd)
    ]
    assert len(matched) == 1
    assert matched[0].classification is expected


def test_only_below_80k_is_a_hard_blocker(config_dir: Path) -> None:
    """D-3, A-2: 86,000-89,999 is not a hard blocker."""
    bands = load_assessment_config(config_dir).compensation.bands
    blocking = {band.classification for band in bands if band.hard_blocker}
    assert blocking == {SalaryCompatibility.BELOW_80K}


def test_below_preferred_review_note_states_both_boundaries(config_dir: Path) -> None:
    """A-2 requires the report to state the position relative to both figures."""
    bands = load_assessment_config(config_dir).compensation.bands
    note = next(
        band.report_note
        for band in bands
        if band.classification is SalaryCompatibility.BELOW_PREFERRED_REVIEW
    )
    assert "90,000" in note
    assert "80,000" in note


def test_degree_equivalency_phrases_are_the_approved_list(config_dir: Path) -> None:
    """D-8."""
    phrases = load_assessment_config(config_dir).blockers.degree_equivalency_phrases
    assert phrases == APPROVED_PHRASES


def test_blocker_set_is_complete_and_expected(config_dir: Path) -> None:
    """D-5, D-6, D-10 shape this set."""
    codes = {rule.code for rule in load_assessment_config(config_dir).blockers.blockers}
    assert codes == set(BlockerCode)
    assert len(codes) == 7


def test_risk_flag_registry_is_complete(config_dir: Path) -> None:
    flags = {rule.flag for rule in load_assessment_config(config_dir).risk_flags.flags}
    assert flags == set(RiskFlag)
    assert len(flags) == 24


def test_blockers_config_declares_no_salary_override(repo_root: Path) -> None:
    """D-10: the override is deferred, so no key may hint at one."""
    text = (repo_root / "config" / "blockers.yaml").read_text(encoding="utf-8")
    keys = [
        line.split(":", 1)[0].strip().lstrip("- ")
        for line in text.splitlines()
        if ":" in line and not line.strip().startswith("#")
    ]
    assert not [key for key in keys if "override" in key.lower()]


def test_risk_flag_config_declares_no_detection_patterns(repo_root: Path) -> None:
    """Detection patterns are Phase 3 work and must be absent."""
    text = (repo_root / "config" / "risk_flags.yaml").read_text(encoding="utf-8")
    directives = "\n".join(
        line for line in text.splitlines() if not line.strip().startswith("#")
    )
    assert "pattern" not in directives.lower()


def test_missing_config_file_is_reported_clearly(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_assessment_config(tmp_path)
