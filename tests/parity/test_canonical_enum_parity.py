"""Canonical parity.

Line numbers are never parsed. These tests read stable labelled Markdown sections, and
compare them against code-owned expected lists documented as derived from their source
document. Any drift in RiskFlag, Recommendation, or ValidationStatus fails the build.
"""

import re
from pathlib import Path

from careerops.config.loader import load_assessment_config
from careerops.config.schema import (
    APPROVED_ALIAS_FAMILIES,
    APPROVED_ALIAS_FAMILY_COUNT,
    APPROVED_ALIAS_VARIANT_COUNT,
    APPROVED_CANONICAL_TECHNOLOGIES,
    DEFERRED_ALIAS_VARIANTS,
    REQUIRED_UNRESOLVED_POLICY_KEYS,
)
from careerops.enums import (
    BlockerCode,
    EvidenceTier,
    MatchClassification,
    PolicyStatus,
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


# ===================================================== policy parity (P-1..P-6, A-5..A-7)
#
# Each test below binds a config/*.yaml value to a labelled section of an approved
# owner-decision record. Line numbers are never parsed. There are exactly eleven
# parity-parsed policy data sections: the original six P-1..P-6 sections, the reduced
# "Unresolved policy keys" section, "Remaining unresolved policy keys after A-5 through
# A-7", "Approved canonical identifiers and display names", "Approved alias registry",
# and "Explicitly deferred aliases". Requirements asserted as record text rather than as
# data sections - the P-3/P-5 non-equivalence, the A-5 formula, the A-6 unknown-term rule,
# the deferred candidate-side parsing, and the JS/TS compound-slot policy - are checked by
# the text tests and are not counted here.

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
    """The live gate section is renamed each time the gate changes; old labels are annotated."""
    section = _section(
        _record(repo_root), "Gate keys after the dimension-allocation decision"
    )
    documented = tuple(NUMBERED.findall(section))
    assert documented == REQUIRED_UNRESOLVED_POLICY_KEYS
    assert documented == load_assessment_config(config_dir).unresolved_keys()


def test_every_superseded_gate_section_is_annotated(repo_root: Path) -> None:
    """A stale gate list may stand only with a blockquote pointing at the live one.

    Two earlier sections list fewer keys than the active gate. Neither may read as current.
    """
    markdown = _record(repo_root)
    for heading in (
        "Unresolved policy keys",
        "Remaining unresolved policy keys after A-5 through A-7",
    ):
        section = _section(markdown, heading)
        assert "Superseded" in section or "superseded" in section, (
            f"{heading!r} lists a stale gate without saying so"
        )
        assert "Gate keys after the dimension-allocation decision" in section


def test_the_allocation_gate_record_states_its_standing(repo_root: Path) -> None:
    markdown = _record(repo_root)
    title = "# Owner-Decision Record — Dimension Allocation Gate"
    assert markdown.count(title) == 1
    record = markdown[markdown.index(title) :]
    for required in (
        "**Status:** approved",
        "**Date:** 2026-09-26",
        "**Owner:** Anthony Grant",
        "does not supersede or modify any canonical Markdown file",
        "It resolves nothing. It makes already-missing work visible.",
        "55 of the 100 points",
        "82 of 100",
        "no `MatchClassification` is produced or displayed",
    ):
        assert required in record, f"the allocation-gate record is missing: {required!r}"


def test_the_record_accounts_for_every_unruled_dimension(
    repo_root: Path, config_dir: Path
) -> None:
    """The 55-point claim must equal the actual weights, not a remembered number."""
    from careerops.config.schema import ALLOCATION_RULE_DIMENSIONS

    weights = load_assessment_config(config_dir).scoring.weights
    assert sum(weights[d] for d in ALLOCATION_RULE_DIMENSIONS.values()) == 55
    markdown = _record(repo_root)
    for dimension in ALLOCATION_RULE_DIMENSIONS.values():
        assert dimension in markdown


# ===================================================== technology policy parity (A-5..A-7)

A5_A7_TITLE = "# Owner-Decision Record — Technology Matching Policy A-5 through A-7"

ID_ROW = re.compile(r"^\| `([A-Z][A-Z0-9_]*)` \| (.+?) \|$", re.MULTILINE)
BACKTICKED_CONSTANT = re.compile(r"`([A-Z][A-Z0-9_]+)`")
PLAIN_BULLET = re.compile(r"^- (.+?)\s*$", re.MULTILINE)


def _a5_a7_record(repo_root: Path) -> str:
    """Return only the A-5..A-7 record.

    The earlier records repeat many of the same standing sentences, so a whole-file
    substring test would pass vacuously. `HEADING` matches `#{2,6}` and cannot see an H1,
    so the slice is taken from the H1 title, which must occur exactly once.
    """
    markdown = _record(repo_root)
    assert markdown.count(A5_A7_TITLE) == 1, "the A-5..A-7 record title must occur once"
    body = markdown[markdown.index(A5_A7_TITLE) :]
    # Stop at the next top-level record. HEADING matches #{2,6} only, so _section cannot
    # see an H1 and a slice must bound itself.
    nxt = body.find("\n# ", len(A5_A7_TITLE))
    return body if nxt == -1 else body[:nxt]


def test_canonical_display_names_match_the_decision_record(
    repo_root: Path, config_dir: Path
) -> None:
    section = _section(
        _a5_a7_record(repo_root), "Approved canonical identifiers and display names"
    )
    documented = tuple(ID_ROW.findall(section))
    assert documented == APPROVED_CANONICAL_TECHNOLOGIES
    policy = load_assessment_config(config_dir).scoring.technology_matching_normalization
    assert documented == tuple((e.id, e.display_name) for e in policy.canonical_technologies)
    assert "CRON" not in {identifier for identifier, _ in documented}


def test_alias_registry_matches_the_decision_record(
    repo_root: Path, config_dir: Path
) -> None:
    section = _section(_a5_a7_record(repo_root), "Approved alias registry")
    assert "Every alias family requires an approval date and a short owner-approved" in section
    documented = tuple(
        (identifier, tuple(v.strip().strip("`") for v in variants.split(", ")))
        for identifier, variants in ID_ROW.findall(section)
    )
    assert documented == APPROVED_ALIAS_FAMILIES
    assert len(documented) == APPROVED_ALIAS_FAMILY_COUNT
    assert sum(len(v) for _, v in documented) == APPROVED_ALIAS_VARIANT_COUNT
    policy = load_assessment_config(config_dir).scoring.technology_matching_normalization
    assert documented == tuple((f.canonical_id, f.variants) for f in policy.alias_families)


def test_deferred_aliases_match_the_decision_record(repo_root: Path) -> None:
    """The bullet list is prose, so each deferred variant is checked by presence."""
    section = _section(_a5_a7_record(repo_root), "Explicitly deferred aliases")
    bullets = PLAIN_BULLET.findall(section)
    assert len(bullets) >= len(DEFERRED_ALIAS_VARIANTS)
    joined = " ".join(section.replace("`", "").split())
    for variant in DEFERRED_ALIAS_VARIANTS:
        assert variant in joined.casefold(), f"deferred variant is missing: {variant!r}"
    for fragment in (
        "crontab -> CRON",
        "openssh -> SSH",
        "JS/TS",
        "javascript/typescript",
        "bare js",
        "bare ts",
        "react native -> React",
        "ubuntu -> Linux",
        "vector database -> ChromaDB",
        "RAG -> LangChain",
        "MCP -> Azure OpenAI",
        "fuzzy match",
        "semantic match",
        "embedding match",
        "LLM match",
        "external taxonomy or API lookup",
    ):
        assert fragment in joined, f"deferred alias list is missing: {fragment!r}"


def test_allocation_formula_is_documented(repo_root: Path) -> None:
    section = _section(_a5_a7_record(repo_root), "Approved allocation formula")
    for required in (
        "points = 20 × ( sum of required-slot best-tier multipliers ) / n",
        "points = 0",
        "any-of grouping",
        "deduplication",
        "never enter the numerator or the denominator",
        "exact and unrounded",
        "score_rounding_rule",
    ):
        assert required in section, f"allocation formula is missing: {required!r}"


def test_unknown_required_term_rule_is_documented(repo_root: Path) -> None:
    section = _section(_a5_a7_record(repo_root), "Approved unknown required-term rule")
    for required in (
        "remains a required slot",
        "receives zero credit",
        "stays in the denominator",
        "REQUIRED_SKILL_GAP",
        "never silently",
        "20 × (0.00 + 1.00) / 2 = 10.00",
        "never retroactively rewrites a completed assessment",
    ):
        assert required in section, f"unknown-term rule is missing: {required!r}"


def test_candidate_side_parsing_is_documented_as_deferred(
    repo_root: Path, config_dir: Path
) -> None:
    """The owner's required correction: deferred, and never claimed as normalized."""
    section = _section(_a5_a7_record(repo_root), "Approved scope of alias application")
    assert "does not claim to normalize" in section
    assert "explicitly deferred and must not be implemented" in section
    for case in (
        "Model Context Protocol (MCP)",
        "JavaScript/TypeScript",
        "Ubuntu/Linux",
        "Windows 10/11",
        "course titles",
    ):
        assert case in section, f"deferred parsing case is missing: {case!r}"
    policy = load_assessment_config(config_dir).scoring.technology_matching_normalization
    assert policy.candidate_side_compound_parsing == "deferred"


def test_compound_slot_policy_is_documented(repo_root: Path, config_dir: Path) -> None:
    section = _section(_a5_a7_record(repo_root), "Approved compound-slot policy for JS/TS")
    for required in (
        "`JS/TS` is an ALL-OF compound requirement",
        "JavaScript AND TypeScript",
        "not an alias-registry row",
        "minimum multiplier",
        "REQUIRED_SKILL_GAP",
        "must not be implemented",
    ):
        assert required in section, f"compound-slot policy is missing: {required!r}"
    policy = load_assessment_config(
        config_dir
    ).scoring.required_vs_preferred_technology_handling
    assert policy.compound_all_of_slot == "deferred"


def test_new_record_states_its_standing(repo_root: Path) -> None:
    """Asserted inside the A-5..A-7 slice: the earlier records repeat these sentences."""
    record = _a5_a7_record(repo_root)
    for required in (
        "**Status:** approved",
        "**Date:** 2026-09-26",
        "**Owner:** Anthony Grant",
        "does not supersede or modify any canonical Markdown file",
        "No canonical Markdown source is changed or superseded by this record",
        "active implementation authority",
        "Five policy keys",
        "does not unblock assessment implementation",
        "No assessment behaviour is authorized by this record",
        "rounding remains `score_rounding_rule`",
        "`critical_unknown_detection_rule`",
    ):
        assert required in record, f"the A-5..A-7 record is missing: {required!r}"


def test_superseded_eight_key_section_is_annotated(repo_root: Path) -> None:
    """The prior live gate section must name this record rather than stand stale."""
    section = _section(_record(repo_root), "Unresolved policy keys")
    assert "Reduced on 2026-09-26 by the owner-decision record below" in section
    assert "Remaining unresolved policy keys after A-5 through A-7" in section
    assert "These five keys gate assessment readiness" in section
    assert "These eight keys gate assessment readiness" not in section


def test_record_introduces_no_new_risk_flag_or_blocker_code(repo_root: Path) -> None:
    """A-5..A-7 create no enum member. Guards against PREFERRED_SKILL_GAP or UNKNOWN_TERM."""
    allowed = (
        {flag.value for flag in RiskFlag}
        | {code.value for code in BlockerCode}
        | {tier.value for tier in EvidenceTier}
        | {band.value for band in SalaryCompatibility}
        | {label.value for label in MatchClassification}
        | {label.value for label in Recommendation}
        | {status.value for status in ValidationStatus}
        | {identifier for identifier, _ in APPROVED_CANONICAL_TECHNOLOGIES}
        | {"CRON", "SSH"}
        | {member.value for member in PolicyStatus}
        | {"REQUIRED_UNRESOLVED_POLICY_KEYS"}
    )
    found = set(BACKTICKED_CONSTANT.findall(_a5_a7_record(repo_root)))
    assert found <= allowed, f"undeclared uppercase constants: {sorted(found - allowed)}"
    assert "PREFERRED_SKILL_GAP" not in found
    assert "UNKNOWN_TERM" not in found


def test_record_does_not_claim_readiness(repo_root: Path) -> None:
    record = _a5_a7_record(repo_root)
    for forbidden in (
        "readiness validation now succeeds",
        "assessment may proceed",
        "assessment behaviour may now be implemented",
        "no keys remain",
    ):
        assert forbidden not in record
