"""Transcription of CANONICAL_CANDIDATE_DOSSIER.md, version 1.0.0, reviewed 2026-09-25.

This module is a machine-readable copy. `CANONICAL_CANDIDATE_DOSSIER.md` remains the sole
authority: tests/parity/test_canonical_dossier_parity.py re-reads that document by labelled
section and fails if this copy drifts from it. Never edit this module to resolve a parity
failure without an approved canonical patch under CONTEXT_UPDATE_PROTOCOL.md.

Deliberately omitted, and asserted absent by the parity suite:

* professional email, phone, LinkedIn, portfolio, and GitHub values (D-9). The canonical
  Identity table carries them; only Name and Base location are transcribed;
* any business-ownership, revenue, client-count, or scale value (D-2);
* any total-years-of-experience figure (D-4). Employment dates stay opaque strings.

Two representational limits are recorded here rather than worked around, because filling
either would mean inventing a value:

1. `EmploymentEvidence.technologies` is empty for every entry. Unlike the project entries,
   the canonical employment entries carry no explicit "Verified technologies" line, so any
   list would come from interpreting responsibility prose. Tier 3 technology evidence
   therefore remains unavailable until an owner-approved explicit list exists. Practical
   effect is small for the target role families: Python, FastAPI, React, REST APIs, GitHub,
   Linux, Bash, SQLite, webhooks, VLANs, firewall rules, SSH, and TCP/IP are all Tier 1
   verified skills already, and best tier wins (E-3).
2. Compound and parenthetical skill names are transcribed verbatim, exactly as written. This
   module performs no splitting of any skill name: candidate-side compound parsing is
   deferred (A-6). Where a compound skill must nonetheless be reachable, the owner declares
   its terms explicitly in `EXPLICIT_SKILL_TERMS`, which A-6 permits as "explicitly
   represented candidate evidence terms". That table is a declaration, not a parser: nothing
   derives it at runtime, and every entry is owner-approved. "JavaScript/TypeScript" and
   course titles have no entry, so they stay unreachable.

No filesystem read, no network call, and no environment read occurs in this package.
"""

from typing import NamedTuple

from careerops.domain.candidate import (
    CandidateDossier,
    EmploymentEvidence,
    ProjectEvidence,
    SkillEvidence,
    TrainingEvidence,
    WorkPreferences,
)
from careerops.enums import EvidenceTier

__all__ = [
    "APPLIED_AI_SKILLS",
    "AVOID_ROLE_FAMILIES",
    "CandidateTerm",
    "CANONICAL_DOCUMENT",
    "CANONICAL_VERSION",
    "EMPLOYMENT_EVIDENCE",
    "EXPLICIT_SKILL_TERMS",
    "POSITIONING_STATEMENT",
    "PROHIBITED_INFERENCES",
    "PROJECT_EVIDENCE",
    "SOFTWARE_AND_AUTOMATION_SKILLS",
    "SYSTEMS_AND_DELIVERY_SKILLS",
    "TARGET_ROLE_FAMILIES",
    "TRAINING_EVIDENCE",
    "VERIFIED_SKILLS",
    "WORK_PREFERENCES",
    "approved_dossier",
    "candidate_terms",
]

CANONICAL_DOCUMENT = "CANONICAL_CANDIDATE_DOSSIER.md"
CANONICAL_VERSION = "1.0.0"

NAME = "Anthony Grant"
BASE_LOCATION = "Lawrenceville, Georgia, United States"

# Source: "Defensible positioning", the blockquote, verbatim.
POSITIONING_STATEMENT = (
    "Applied AI Engineer building reliable AI-enabled applications, retrieval-augmented "
    "systems, automation workflows, and MCP-connected tools. Hands-on with Python, FastAPI, "
    "JavaScript/TypeScript, REST APIs, Linux, local LLM workflows, hybrid retrieval, "
    "evaluation, regression testing, and failure analysis. Brings a systems and delivery "
    "mindset from technical implementation, Tier II/III troubleshooting, customer-facing "
    "technical environments, and product iteration."
)

# Source: "Work preferences" table. Work authorization stays UNKNOWN by type (D-5).
WORK_PREFERENCES = WorkPreferences(
    target_country="United States",
    remote_preference="Preferred",
    relocation_willing=True,
    relocation_assistance_preferred=True,
    preferred_base_salary_min_usd=90_000,
    exclusion_floor_base_salary_usd=80_000,
)

# Source: "Target seniority", the list under "Prioritize:".
TARGET_ROLE_FAMILIES: tuple[str, ...] = (
    "Intermediate / mid-level",
    "Junior / associate only when genuinely appropriate",
    "Engineer I / Engineer II",
    "Applied AI Engineer",
    "AI Product Engineer",
    "AI Integration Engineer",
    "AI Automation Engineer",
    "AI Solutions / Implementation Engineer",
    "Developer Tools / DevEx Engineer",
    "AI-adjacent Software Engineer",
    "Technical Systems / Implementation Engineer with substantive AI, API, automation, "
    "or systems work",
)

# Source: "Target seniority", the list under "Avoid by default".
AVOID_ROLE_FAMILIES: tuple[str, ...] = (
    "Senior, Staff, Principal, Lead, Head of AI",
    "Research Scientist, Applied Scientist, ML Researcher",
    "Foundation Model Engineer",
    "Roles with required active clearance",
    "Roles with mandatory completed degrees and no equivalent-experience alternative",
    "Research-heavy model-training roles outside documented experience",
)

# Source: "Verified skills". Every entry is Tier 1 by decision D-7.
APPLIED_AI_SKILLS: tuple[str, ...] = (
    "LLM API integration",
    "RAG",
    "Hybrid retrieval",
    "BM25",
    "ChromaDB",
    "Model Context Protocol (MCP)",
    "Agent workflows",
    "Ollama",
    "Local LLM workflows",
    "Structured outputs",
    "Prompt evaluation",
    "Regression testing",
    "Failure analysis",
)

SOFTWARE_AND_AUTOMATION_SKILLS: tuple[str, ...] = (
    "Python",
    "FastAPI",
    "JavaScript",
    "TypeScript",
    "React",
    "REST APIs",
    "SQLite",
    "Webhooks",
    "Git",
    "GitHub",
    "Bash",
    "Linux",
    "Cron",
)

SYSTEMS_AND_DELIVERY_SKILLS: tuple[str, ...] = (
    "Tier II/III support",
    "Root-cause analysis",
    "Technical escalation",
    "SOPs and runbooks",
    "Release validation",
    "Windows 10/11",
    "Ubuntu/Linux",
    "TCP/IP",
    "VLANs",
    "Firewall rules",
    "SSH",
    "Remote support",
    "Customer-facing technical implementation",
)

VERIFIED_SKILLS: tuple[SkillEvidence, ...] = tuple(
    SkillEvidence(name=name, tier=EvidenceTier.TIER_1_VERIFIED_SKILL)
    for name in (
        *APPLIED_AI_SKILLS,
        *SOFTWARE_AND_AUTOMATION_SKILLS,
        *SYSTEMS_AND_DELIVERY_SKILLS,
    )
)

# Source: "Project evidence". Each entry's technologies come from its explicit
# "Verified technologies" line, and from nowhere else.
PROJECT_EVIDENCE: tuple[ProjectEvidence, ...] = (
    ProjectEvidence(
        name="C.Walts — Hybrid Retrieval and Evaluation System",
        technologies=("ChromaDB", "BM25", "MCP", "local LLM workflows"),
        summary=(
            "Designed and iterated a hybrid dense-retrieval plus BM25 workflow. "
            "Used corpus controls, evaluation isolation, preservation checks, and rollback "
            "verification. "
            "Diagnosed lexical-index persistence and restoration defects; implemented "
            "corrective changes and validation. "
            "In a controlled evaluation on August 12, 2026, achieved 17/17 useful top-5 "
            "retrieval cases and 10/10 preservation checks, with p50/p95 retrieval latency "
            "of 84/125 ms."
        ),
        qualifier=(
            "These results are controlled project-evaluation evidence. The methodology and "
            "limitations must be retained; do not represent them as universal production "
            "performance."
        ),
    ),
    ProjectEvidence(
        name="BADGR Harness — AI Agent Orchestration",
        technologies=("Python", "Ollama", "MCP", "Linux"),
        summary=(
            "Built and evaluated specialist-routing patterns for AI-agent workflows. "
            "Investigated and corrected a routing defect that could send general requests "
            "to a domain-specific specialist. "
            "Retained validation evidence for generic-versus-specialist separation. "
            "Used structured testing, failure analysis, and iteration to improve expected "
            "routing behavior and reliability."
        ),
    ),
    ProjectEvidence(
        name="BADGR Bolt — Android Reading Application",
        technologies=("Kotlin", "Android", "GitHub Pages"),
        summary=(
            "Developed an RSVP/ORP reading application with narration integration, Play "
            "Integrity handling, device troubleshooting, release validation, and "
            "security-hardening updates. "
            "Maintained deployment and release-validation evidence, including 24 completed "
            "GitHub Pages deployments through June 24, 2026."
        ),
    ),
)

# Source: "Employment evidence". `technologies` is empty for every entry: the canonical
# document states no explicit technology list for employment, and inferring one from
# responsibility prose would invent a value. See the module docstring, limit 1.
EMPLOYMENT_EVIDENCE: tuple[EmploymentEvidence, ...] = (
    EmploymentEvidence(
        title="Founder & Applied AI Engineer",
        organization="BADGRTechnologies LLC",
        location="Lawrenceville, Georgia",
        start="January 2025",
        end="Present",
        technologies=(),
        responsibilities=(
            "Founded and operated a licensed technology business delivering applied AI "
            "software, workflow automation, and client-facing technical solutions.",
            "Scoped technical requirements, defined acceptance criteria, built AI-enabled "
            "and API-connected workflows, investigated failures, conducted regression "
            "validation, and documented limitations and next steps.",
            "Delivered solutions using Python, JavaScript/TypeScript, React, FastAPI, REST "
            "APIs, GitHub, Linux, Bash, SQLite, webhooks, and automation-oriented workflows.",
        ),
    ),
    EmploymentEvidence(
        title="Field Support Hardware Engineer II",
        organization="UVeye",
        location="Atlanta, Georgia",
        start="March 2024",
        end="April 2025",
        technologies=(),
        responsibilities=(
            "Delivered Tier II/III field and escalation support for AI-powered "
            "vehicle-inspection systems across Windows, Linux, cameras, networking, and "
            "customer-operational environments.",
            "Served as assistant lead field engineer on a high-priority airport "
            "rental-fleet deployment supporting three AI-powered vehicle-inspection systems.",
            "Diagnosed and resolved hardware, software, network, and deployment issues; "
            "coordinated with engineering teams and customer stakeholders.",
            "Configured MikroTik routers, VLAN segmentation, subnets, firewall rules, SSH "
            "access, and ACL controls for IP-camera and NVR environments.",
            "Used AWS operational tools within established access controls and documented "
            "workflows to locate, restore, and back up scanned-image assets.",
        ),
    ),
    EmploymentEvidence(
        title="Technical Support Engineer II",
        organization="Source Support Services",
        location="Lawrenceville, Georgia",
        start="September 2021",
        end="March 2023",
        technologies=(),
        responsibilities=(
            "Delivered remote and onsite Tier II/III troubleshooting for enterprise "
            "networking, desktops, servers, storage, and client environments.",
            "Achieved approximately 80% first-contact resolution across assigned support "
            "work.",
            "Authored technical documentation and repeatable troubleshooting workflows that "
            "contributed to a 15% reduction in mean time to resolution.",
            "Communicated findings, remediation steps, and status updates to clients and "
            "internal teams in high-urgency support situations.",
        ),
    ),
    EmploymentEvidence(
        title="Technical Support Analyst / Jr. Implementation Manager",
        organization="HotSauce Technologies",
        location="Norcross, Georgia",
        start="June 2019",
        end="July 2021",
        technologies=(),
        responsibilities=(
            "Supported enterprise point-of-sale systems, servers, peripherals, and "
            "client-side software through implementation and ongoing support workflows.",
            "Promoted to Junior Implementation Manager based on technical performance and "
            "customer service.",
            "Coordinated client onboarding, implementation activities, rollout support, "
            "escalation management, SOPs, and communication between customers and "
            "engineering teams.",
        ),
    ),
)

# Source: "Education and training" table, canonical wording column. `TrainingEvidence` has no
# technologies field, so Tier 4 technology evidence remains unrepresentable; course titles are
# never parsed for technology names (A-6).
TRAINING_EVIDENCE: tuple[TrainingEvidence, ...] = (
    TrainingEvidence(
        name=(
            "Coursework Toward AS in Information Technology — Systems Security Focus, "
            "Northeast State Technical College"
        ),
        provider="Northeast State Technical College",
    ),
    TrainingEvidence(
        name=(
            "Meta/Coursera coursework: Version Control; Kotlin Fundamentals; Android "
            "Mobile Development; UX/UI in Android Studio; Principles of UX/UI; Advanced "
            "Programming in Kotlin"
        ),
        provider="Meta/Coursera",
    ),
)

# Source: "Known evidence gaps and prohibited inferences", verbatim.
PROHIBITED_INFERENCES: tuple[str, ...] = (
    "Completed bachelor’s degree or completed associate degree",
    "Active security clearance",
    "Docker, Kubernetes, Terraform",
    "CI/CD ownership",
    "Cloud architecture ownership",
    "MLOps ownership",
    "SOC 2, HIPAA, or regulated-industry compliance ownership",
    "LangChain, OpenAI API, Azure OpenAI, GCP Vertex AI",
    "Five or more years of conventional software-engineering employment",
    "Research publications, advanced ML research, or foundation-model training",
    "Client count, customer count, revenue, funding, employee count, or business scale",
    "People management or formal engineering leadership",
    "Relocation assistance eligibility",
    "Work authorization status",
)


# Owner-approved explicit terms for compound skill names, declared 2026-09-26.
#
# A-6 permits aliases against "explicitly represented candidate evidence terms". These are
# that representation. Each key is a verbatim Verified skills entry; each value lists the
# terms the owner approved as naming the same technology. Nothing here is derived at runtime:
# adding an entry is an owner decision, and the parity suite asserts that every term's words
# all appear in its key, so no term can be invented.
#
# Deliberately absent: "JavaScript/TypeScript" (a compound requirement, not a single
# technology - the owner deferred it), "Tier II/III support" (not a technology), and every
# course title (Tier 4 technology evidence stays unrepresentable).
EXPLICIT_SKILL_TERMS: dict[str, tuple[str, ...]] = {
    "Model Context Protocol (MCP)": ("Model Context Protocol", "MCP"),
    "Ubuntu/Linux": ("Ubuntu", "Linux"),
    "Windows 10/11": ("Windows 10", "Windows 11"),
}

_SKILL_SUBSECTIONS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Applied AI", APPLIED_AI_SKILLS),
    ("Software and automation", SOFTWARE_AND_AUTOMATION_SKILLS),
    ("Systems and delivery", SYSTEMS_AND_DELIVERY_SKILLS),
)


class CandidateTerm(NamedTuple):
    """One candidate evidence term, its tier, and the section a report must cite.

    `term` is the raw candidate phrase exactly as the dossier represents it, or an
    owner-approved explicit term from `EXPLICIT_SKILL_TERMS`. Nothing here is normalized:
    normalization belongs to the matcher, which applies only the four approved A-6 steps.
    """

    term: str
    tier: EvidenceTier
    evidence_reference: str


def candidate_terms() -> tuple[CandidateTerm, ...]:
    """Every candidate technology term available for matching, with tier and citation.

    Pure data assembly: no normalization, no job phrase, no alias, and no score. Verified
    skills yield Tier 1, project technologies Tier 2, and employment technologies Tier 3 -
    the last of which is empty today, by the limit recorded above. Training yields nothing,
    because `TrainingEvidence` carries no technologies field.

    A term may appear more than once at different tiers. Best tier wins is the matcher's
    responsibility (E-3), not this function's.
    """
    terms: list[CandidateTerm] = []
    for subsection, skills in _SKILL_SUBSECTIONS:
        reference = f"Verified skills — {subsection}"
        for skill in skills:
            terms.append(
                CandidateTerm(skill, EvidenceTier.TIER_1_VERIFIED_SKILL, reference)
            )
            for explicit in EXPLICIT_SKILL_TERMS.get(skill, ()):
                terms.append(
                    CandidateTerm(
                        explicit, EvidenceTier.TIER_1_VERIFIED_SKILL, reference
                    )
                )
    for project in PROJECT_EVIDENCE:
        reference = f"Project evidence — {project.name}"
        for technology in project.technologies:
            terms.append(
                CandidateTerm(technology, EvidenceTier.TIER_2_PROJECT_EVIDENCE, reference)
            )
    for job in EMPLOYMENT_EVIDENCE:
        reference = f"Employment evidence — {job.title} — {job.organization}"
        for technology in job.technologies:
            terms.append(
                CandidateTerm(
                    technology, EvidenceTier.TIER_3_EMPLOYMENT_EVIDENCE, reference
                )
            )
    return tuple(terms)


def approved_dossier() -> CandidateDossier:
    """Return the transcribed canonical dossier. Pure: no I/O, no clock, no randomness."""
    return CandidateDossier(
        name=NAME,
        base_location=BASE_LOCATION,
        preferences=WORK_PREFERENCES,
        positioning_statement=POSITIONING_STATEMENT,
        target_role_families=TARGET_ROLE_FAMILIES,
        avoid_role_families=AVOID_ROLE_FAMILIES,
        verified_skills=VERIFIED_SKILLS,
        project_evidence=PROJECT_EVIDENCE,
        employment_evidence=EMPLOYMENT_EVIDENCE,
        training_evidence=TRAINING_EVIDENCE,
        prohibited_inferences=PROHIBITED_INFERENCES,
    )
