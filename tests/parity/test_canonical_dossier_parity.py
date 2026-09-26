"""Canonical dossier parity.

`CANONICAL_CANDIDATE_DOSSIER.md` is the sole authority for candidate qualifications.
`careerops.dossier.approved_dossier` is a machine-readable transcription of it. These tests
re-read the document by labelled section and fail if the transcription drifts, which is what
makes the Transcribe route safe: a canonical edit that is not mirrored breaks the build
instead of silently producing a wrong score.

Line numbers are never parsed (standing ruling A-1). Contact values are never asserted by
content: the tests below assert their absence (D-9).
"""

import re
from pathlib import Path

from careerops.dossier.approved_dossier import (
    APPLIED_AI_SKILLS,
    AVOID_ROLE_FAMILIES,
    BASE_LOCATION,
    CANONICAL_VERSION,
    EMPLOYMENT_EVIDENCE,
    EXPLICIT_SKILL_TERMS,
    NAME,
    POSITIONING_STATEMENT,
    PROHIBITED_INFERENCES,
    PROJECT_EVIDENCE,
    SOFTWARE_AND_AUTOMATION_SKILLS,
    SYSTEMS_AND_DELIVERY_SKILLS,
    TARGET_ROLE_FAMILIES,
    TRAINING_EVIDENCE,
    VERIFIED_SKILLS,
    approved_dossier,
)
from careerops.enums import EvidenceTier

HEADING = re.compile(r"^(#{2,6}) (.+?)\s*$")
BULLET = re.compile(r"^- (.+?)\s*$", re.MULTILINE)
TABLE_ROW = re.compile(r"^\| (.+?) \| (.+?) \|", re.MULTILINE)
VERIFIED_TECHNOLOGIES = re.compile(
    r"^\*\*Verified technologies:\*\* (.+?)\.?\s*$", re.MULTILINE
)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?<!\d)(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}(?!\d)")
URL = re.compile(r"https?://")

SKILL_SUBSECTIONS = ("Applied AI", "Software and automation", "Systems and delivery")
AVOID_MARKER = "Avoid by default"


def _dossier(repo_root: Path) -> str:
    return (repo_root / "CANONICAL_CANDIDATE_DOSSIER.md").read_text(encoding="utf-8")


def _section(markdown: str, heading: str) -> str:
    """Return a section body, located by its exact title at any heading level.

    Capture stops at the next heading of the same level or shallower, so a subsection is
    scoped correctly and a parent section yields its subsections' content with the subsection
    headings removed. Line numbers are never used.
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


def _subsection_titles(markdown: str, parent: str, depth: int) -> list[str]:
    """Every heading of `depth` between `parent` and the next heading of parent's level."""
    titles: list[str] = []
    inside = False
    parent_depth: int | None = None
    for line in markdown.splitlines():
        match = HEADING.match(line)
        if match is None:
            continue
        found_depth = len(match.group(1))
        title = match.group(2).strip()
        if title == parent:
            inside = True
            parent_depth = found_depth
            continue
        if inside and parent_depth is not None:
            if found_depth <= parent_depth:
                break
            if found_depth == depth:
                titles.append(title)
    return titles


# ------------------------------------------------------------------- provenance


def test_transcription_records_the_canonical_version(repo_root: Path) -> None:
    """A canonical version bump must be acknowledged here, not absorbed silently."""
    markdown = _dossier(repo_root)
    assert f"version: {CANONICAL_VERSION}" in markdown


def test_identity_name_and_location_match(repo_root: Path) -> None:
    rows = dict(TABLE_ROW.findall(_section(_dossier(repo_root), "Identity and public professional links")))
    assert rows["Name"].strip() == NAME
    assert rows["Base location"].strip() == BASE_LOCATION


# ------------------------------------------------------------- D-9 contact absence


def test_transcription_contains_no_contact_value(src_dir: Path) -> None:
    """D-9: email, phone, and profile URLs exist in the canonical document, never here."""
    text = (src_dir / "careerops" / "dossier" / "approved_dossier.py").read_text(
        encoding="utf-8"
    )
    assert not EMAIL.search(text), "the transcription contains an email address"
    assert not PHONE.search(text), "the transcription contains a phone number"
    assert not URL.search(text), "the transcription contains a URL"


def test_canonical_document_does_carry_those_values(repo_root: Path) -> None:
    """Proves the absence test above is meaningful rather than vacuous."""
    identity = _section(_dossier(repo_root), "Identity and public professional links")
    assert EMAIL.search(identity)
    assert PHONE.search(identity)
    assert URL.search(identity)


# --------------------------------------------------------------- work preferences


def test_work_preferences_match_the_canonical_table(repo_root: Path) -> None:
    rows = dict(TABLE_ROW.findall(_section(_dossier(repo_root), "Work preferences")))
    preferences = approved_dossier().preferences
    assert rows["Target country"].strip() == preferences.target_country
    assert rows["Remote"].strip() == preferences.remote_preference
    assert "Willing to relocate" in rows["Relocation"]
    assert preferences.relocation_willing is True
    assert "Preferred" in rows["Relocation assistance"]
    assert preferences.relocation_assistance_preferred is True
    assert "$90,000" in rows["Preferred base salary minimum"]
    assert preferences.preferred_base_salary_min_usd == 90_000
    assert "$80,000" in rows["General exclusion"]
    assert preferences.exclusion_floor_base_salary_usd == 80_000
    assert "UNKNOWN" in rows["Work authorization"]
    assert preferences.work_authorization == "UNKNOWN"


# ------------------------------------------------------------------ role families


def test_role_families_match_the_canonical_lists(repo_root: Path) -> None:
    body = _section(_dossier(repo_root), "Target seniority")
    head, _, tail = body.partition(AVOID_MARKER)
    assert tail, f"the {AVOID_MARKER!r} marker is missing from Target seniority"
    assert tuple(BULLET.findall(head)) == TARGET_ROLE_FAMILIES
    assert tuple(BULLET.findall(tail)) == AVOID_ROLE_FAMILIES


# ------------------------------------------------------------ defensible positioning


def test_positioning_statement_matches_the_canonical_blockquote(repo_root: Path) -> None:
    body = _section(_dossier(repo_root), "Defensible positioning")
    quoted = " ".join(
        line.removeprefix("> ").strip() for line in body.splitlines() if line.startswith("> ")
    )
    assert quoted == POSITIONING_STATEMENT


# ---------------------------------------------------------------- verified skills


def test_verified_skill_subsections_are_all_transcribed(repo_root: Path) -> None:
    """A new skill subsection must fail here rather than be silently dropped."""
    found = _subsection_titles(_dossier(repo_root), "Verified skills", depth=3)
    assert tuple(found) == SKILL_SUBSECTIONS


def test_each_skill_subsection_matches_the_canonical_bullets(repo_root: Path) -> None:
    markdown = _dossier(repo_root)
    expected = {
        "Applied AI": APPLIED_AI_SKILLS,
        "Software and automation": SOFTWARE_AND_AUTOMATION_SKILLS,
        "Systems and delivery": SYSTEMS_AND_DELIVERY_SKILLS,
    }
    for title, transcribed in expected.items():
        documented = tuple(BULLET.findall(_section(markdown, title)))
        assert documented == transcribed, f"{title} drifted"


def test_every_verified_skill_is_tier_one_and_in_document_order(repo_root: Path) -> None:
    """D-7: the Verified skills section is Tier 1 evidence."""
    documented = tuple(BULLET.findall(_section(_dossier(repo_root), "Verified skills")))
    assert tuple(skill.name for skill in VERIFIED_SKILLS) == documented
    assert {skill.tier for skill in VERIFIED_SKILLS} == {
        EvidenceTier.TIER_1_VERIFIED_SKILL
    }


def test_compound_skill_names_are_transcribed_verbatim() -> None:
    """A-6: no skill name is split. Compounds stay exactly as the document writes them."""
    names = {skill.name for skill in VERIFIED_SKILLS}
    for compound in (
        "Model Context Protocol (MCP)",
        "Windows 10/11",
        "Ubuntu/Linux",
        "Tier II/III support",
    ):
        assert compound in names
    for split_form in ("MCP", "Windows", "Ubuntu", "Windows 10", "Windows 11"):
        assert split_form not in names, (
            f"{split_form!r} must not become a Verified skills entry; explicit terms live "
            "in EXPLICIT_SKILL_TERMS, not in the transcription"
        )


# --------------------------------------------------- owner-approved explicit terms


def test_every_explicit_term_key_is_a_verbatim_skill() -> None:
    """A key that is not a real skill name would attach evidence to nothing."""
    names = {skill.name for skill in VERIFIED_SKILLS}
    for key in EXPLICIT_SKILL_TERMS:
        assert key in names, f"{key!r} is not a transcribed Verified skills entry"


def test_no_explicit_term_invents_a_technology() -> None:
    """Every word of every term must already appear in its key. This is the anti-invention
    control: a declaration may only re-represent what the document already says."""
    for key, terms in EXPLICIT_SKILL_TERMS.items():
        haystack = key.casefold()
        for term in terms:
            assert term, f"{key!r} declares an empty term"
            for word in term.split():
                assert word.casefold() in haystack, (
                    f"{key!r} -> {term!r} introduces {word!r}, which the canonical skill "
                    "name does not contain"
                )


def test_no_explicit_term_is_a_bare_two_letter_acronym() -> None:
    """A-6: no bare two-letter acronym becomes a matchable term."""
    for key, terms in EXPLICIT_SKILL_TERMS.items():
        for term in terms:
            assert not (len(term) == 2 and term.isalpha()), f"{key!r} declares {term!r}"


def test_no_explicit_term_reaches_a_prohibited_inference() -> None:
    """A declaration may never manufacture evidence the dossier explicitly disclaims."""
    disclaimed = " ".join(PROHIBITED_INFERENCES).casefold()
    for key, terms in EXPLICIT_SKILL_TERMS.items():
        for term in terms:
            assert term.casefold() not in disclaimed, (
                f"{key!r} -> {term!r} names a prohibited inference"
            )


def test_deferred_compounds_have_no_explicit_terms() -> None:
    """The owner deferred these, so no declaration may quietly enable them."""
    for deferred in ("JavaScript/TypeScript", "Tier II/III support"):
        assert deferred not in EXPLICIT_SKILL_TERMS
    for entry in TRAINING_EVIDENCE:
        assert entry.name not in EXPLICIT_SKILL_TERMS


def test_explicit_terms_cover_exactly_the_approved_compounds() -> None:
    """The approved table, named exactly. A fourth entry is an owner decision, not a patch."""
    assert EXPLICIT_SKILL_TERMS == {
        "Model Context Protocol (MCP)": ("Model Context Protocol", "MCP"),
        "Ubuntu/Linux": ("Ubuntu", "Linux"),
        "Windows 10/11": ("Windows 10", "Windows 11"),
    }


# ---------------------------------------------------------------- project evidence


def test_project_names_match_the_canonical_subsections(repo_root: Path) -> None:
    found = _subsection_titles(_dossier(repo_root), "Project evidence", depth=3)
    assert tuple(found) == tuple(project.name for project in PROJECT_EVIDENCE)


def test_project_technologies_come_only_from_the_explicit_lines(repo_root: Path) -> None:
    """Each project's technologies are its "Verified technologies" line, and nothing else."""
    markdown = _dossier(repo_root)
    for project in PROJECT_EVIDENCE:
        section = _section(markdown, project.name)
        declared = VERIFIED_TECHNOLOGIES.findall(section)
        assert len(declared) == 1, f"{project.name} must declare technologies exactly once"
        assert tuple(declared[0].split(", ")) == project.technologies


def test_only_the_first_project_carries_a_qualifier(repo_root: Path) -> None:
    """The C.Walts qualifier is mandatory wording and must survive transcription."""
    markdown = _dossier(repo_root)
    qualified = [p for p in PROJECT_EVIDENCE if p.qualifier != "UNKNOWN"]
    assert len(qualified) == 1
    section = _section(markdown, qualified[0].name)
    assert "**Required qualifier:**" in section
    assert "do not represent them as universal production performance" in qualified[0].qualifier


# ------------------------------------------------------------- employment evidence


def test_employment_headings_match_title_and_organization(repo_root: Path) -> None:
    found = _subsection_titles(_dossier(repo_root), "Employment evidence", depth=3)
    expected = tuple(f"{job.title} — {job.organization}" for job in EMPLOYMENT_EVIDENCE)
    assert tuple(found) == expected


def test_employment_locations_and_dates_match(repo_root: Path) -> None:
    markdown = _dossier(repo_root)
    for job in EMPLOYMENT_EVIDENCE:
        section = _section(markdown, f"{job.title} — {job.organization}")
        assert f"**Location:** {job.location}" in section
        assert f"**Dates:** {job.start}–{job.end}" in section


def test_employment_responsibilities_match_the_canonical_bullets(repo_root: Path) -> None:
    markdown = _dossier(repo_root)
    for job in EMPLOYMENT_EVIDENCE:
        section = _section(markdown, f"{job.title} — {job.organization}")
        assert tuple(BULLET.findall(section)) == job.responsibilities


def test_no_employment_entry_claims_a_technology_list(repo_root: Path) -> None:
    """The canonical employment entries state no technology list, so none is transcribed.

    Inferring one from responsibility prose would invent a value. Tier 3 technology evidence
    stays unavailable until an owner-approved explicit list exists. In particular AWS appears
    only in UVeye responsibility prose and must never become a Tier 3 technology match (E-6,
    and cloud architecture ownership is a prohibited inference).
    """
    markdown = _dossier(repo_root)
    for job in EMPLOYMENT_EVIDENCE:
        section = _section(markdown, f"{job.title} — {job.organization}")
        assert not VERIFIED_TECHNOLOGIES.findall(section), (
            f"{job.organization} now declares technologies; transcribe them explicitly"
        )
        assert job.technologies == ()


# ------------------------------------------------------------------ education


def test_training_entries_match_the_canonical_table(repo_root: Path) -> None:
    rows = dict(TABLE_ROW.findall(_section(_dossier(repo_root), "Education and training")))
    documented = (rows["Education"].strip(), rows["Additional training"].strip())
    assert tuple(entry.name for entry in TRAINING_EVIDENCE) == documented


def test_training_carries_no_technology_field() -> None:
    """Tier 4 technology evidence is unrepresentable, and course titles are never parsed."""
    from careerops.domain.candidate import TrainingEvidence

    assert "technologies" not in TrainingEvidence.model_fields


# ------------------------------------------------------ prohibited inferences


def test_prohibited_inferences_match_the_canonical_list(repo_root: Path) -> None:
    body = _section(_dossier(repo_root), "Known evidence gaps and prohibited inferences")
    assert tuple(BULLET.findall(body)) == PROHIBITED_INFERENCES


def test_prohibited_inferences_still_name_the_adjacent_stacks() -> None:
    """These are the targets A-6 forbids reaching by alias."""
    joined = " ".join(PROHIBITED_INFERENCES)
    for token in ("Kubernetes", "Terraform", "LangChain", "Azure OpenAI", "Docker"):
        assert token in joined
