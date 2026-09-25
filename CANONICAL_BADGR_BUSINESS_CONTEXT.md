---
document_id: canonical-badgr-business-context
title: Canonical BADGRTechnologies LLC Context — Sanitized
version: 1.0.0
status: approved_for_nonsecret_project_context
last_reviewed: 2026-09-25
owner: Anthony Grant
change_policy: human_approval_required
sensitivity: confidential-business
allowed_use:
  - local_project_context
  - visual_branding
  - future_contract_opportunity_mode
  - local_development_environment_planning
prohibited_use:
  - credential_storage
  - financial_identity_storage
  - public_disclosure_without_review
  - automatic_social_media_actions
---

# BADGRTechnologies LLC Context

## Canonical business identity

| Field | Canonical value | Status |
|---|---|---|
| Display name | BADGR Technologies LLC | VERIFIED from supplied business context |
| Legal name | BADGRTechnologies LLC | VERIFIED from supplied business context |
| Entity type | LLC | VERIFIED from supplied business context |
| Industry | Custom Computer Programming Services | VERIFIED from supplied business context |
| Business start / founding reference | February 2025; exact date requires a single confirmed legal-record value | CONCERN: conflicting dates appeared in supplied materials |
| Business website | https://www.badgrtech.com/ | VERIFIED from supplied business context |
| Public portfolio | https://badgrtech.com/portfolio | VERIFIED from supplied resume/context |
| Tagline | CTRL+ALT+DELIVER | VERIFIED from supplied brand file |
| Primary geography | Atlanta / Lawrenceville, Georgia | VERIFIED at high level |

## Purpose in CareerOps Local

CareerOps Local version 1 serves Anthony Grant’s personal job search first.

A later, separate **BADGR business-opportunity mode** may assess potential contract, implementation, technical automation, AI-integration, or software opportunities for BADGRTechnologies LLC. This must remain logically separated from Anthony’s personal candidate dossier:

- Personal career matching uses `CANONICAL_CANDIDATE_DOSSIER.md`.
- Business-contract matching uses this document plus a future approved `CANONICAL_BADGR_CAPABILITIES.md`.
- Never merge personal résumé claims and business claims automatically.
- Never expose business financial, identifier, address, social-login, or account-recovery information.

## Defensible business capability framing

Use only this high-level framing until a dedicated capability dossier is created and approved:

> BADGRTechnologies LLC develops applied AI software, workflow automation, API-connected tools, technical systems, and product-oriented software. Its current visible engineering evidence includes RAG and hybrid retrieval experimentation, agent orchestration, local LLM workflows, Android product work, Linux-based tooling, API integration, evaluation, regression validation, failure analysis, and systems troubleshooting.

This describes technical direction and demonstrated work. It must not be converted into claims about clients, revenue, scale, certifications, regulated compliance, or production enterprise deployments without evidence.

## Brand identity

### Color system

| Token | Hex |
|---|---|
| `badgr_blue` | `#02068D` |
| `logo_primary` | `#0E305F` |
| `logo_primary_dark` | `#0A2345` |
| `logo_mid` | `#1C4A86` |
| `logo_light` | `#3E6FB0` |
| `logo_lightest` | `#7FA1D3` |
| `white` | `#F2F0E6` |
| `grey` | `#A9A9A9` |
| `black` | `#050505` |

### Usage rules

| UI purpose | Value |
|---|---|
| Header color | `#0E305F` |
| Body text | `#050505` |
| Background | `#F2F0E6` |
| Primary accent | `#02068D` |
| Style direction | Minimal, high-contrast, blue/black system aesthetic |

### Typography

Available/design-intent fonts reported in supplied material:

- Goldman Bold
- Inter family
- Satoshi family

**Rule:** Confirm licensing, installed availability, and intended usage before embedding fonts in a distributed application. Use system sans-serif fallback in the MVP.

## Public links — unverified operational status

These are public links supplied by the owner. They may be used only as optional references; an agent must not log in, post, message, alter accounts, or assume ownership/validity.

| Channel | URL | Status |
|---|---|---|
| Website | https://www.badgrtech.com/ | Provided; not independently revalidated here |
| Portfolio | https://badgrtech.com/portfolio | Provided; not independently revalidated here |
| GitHub | https://github.com/Ch405-L9 | Provided; not independently revalidated here |
| Instagram | https://www.instagram.com/badgrtech/ | Provided; account linkage needs owner confirmation |
| YouTube | https://www.youtube.com/@badgrtech25 | Provided; account linkage needs owner confirmation |
| TikTok | https://www.tiktok.com/@badgr.25 | Provided; account linkage needs owner confirmation |
| X | https://x.com/40n33Ba6R | Provided; account linkage needs owner confirmation |
| Facebook | https://www.facebook.com/profile.php?id=61581099610296 | Provided; business-vs-personal status needs owner confirmation |
| Personal LinkedIn | https://www.linkedin.com/in/anthonygrant-app-ai-engineer | Provided; career profile |
| Company LinkedIn | UNKNOWN | A company-admin URL appeared in sensitive source material but public company URL/status requires owner confirmation |

## Asset and local-path policy

The owner reported local directories for branding, business documents, projects, and certifications. These paths may be referenced in a local configuration document **only after Anthony confirms the path and grants access**.

Do not hard-code personal/home directory paths into public documentation or source code. Use environment variables or a local ignored config file, for example:

```text
CAREEROPS_BADGR_BRAND_DIR=
CAREEROPS_BADGR_DOCS_DIR=
CAREEROPS_PROJECTS_DIR=
CAREEROPS_CERTS_DIR=
```

Never commit paths that reveal sensitive storage layouts if the repository could become public.

## Local lab profile

**Reported on August 29, 2026; verify dynamically before relying on it.**

| Component | Reported value |
|---|---|
| Computer | CyberPowerPC GamingPC |
| Memory | 32 GiB |
| CPU | AMD Ryzen 5 5500, 12 logical processors reported |
| GPU | AMD Radeon RX 6500 XT |
| Disk capacity | 1.0 TB |
| OS | Ubuntu 24.04.4 LTS, 64-bit |
| Desktop | GNOME 46 / X11 |
| Kernel | Linux 7.0.0-30-generic |

### Reported local Ollama inventory

This inventory is operationally time-sensitive. Treat as `UNVERIFIED_AT_RUNTIME`; use `ollama list` locally before selecting a model.

- `phi4-mini:latest`
- `qwen3:8b`
- `deepseek-r1:14b`
- `qwen3:14b`
- `nomic-embed-text:latest`
- `kimi-k2.5:cloud`
- `mistral:7b`
- `qwen2.5-coder:7b`
- `qwen2.5:14b`
- `badgr-analyst:latest`
- `llama3.2:latest`
- `dmape-qwen:latest`
- `rockn/qwen2.5-omni-7b-q4_k_m:latest`
- `llama3.1:8b`
- `phi3:mini`
- `gemma2:2b`
- `llama3.2:3b`

### MVP local-model policy

- CareerOps must work completely without an LLM.
- Deterministic parsing, scoring, blockers, risk flags, and reporting are mandatory baseline behavior.
- Ollama is an optional local explanation/extraction provider, disabled by default.
- Default initial local provider candidate: `qwen3:8b` or `qwen2.5:14b`, only after a runtime health check and structured-output test.
- Use `nomic-embed-text` only if semantic similarity is introduced after deterministic duplicate detection is working.
- Do not make `kimi-k2.5:cloud` the default because it is not local-only.

## Sensitive data exclusion

The original submitted business file contained credentials, account identifiers, personal addresses, tax/business identifiers, phone numbers, dates of birth, and other sensitive information.

Those items are deliberately excluded from this canonical context. Store them only in a password manager, appropriately protected legal/financial systems, or encrypted local storage outside the source repository. If an exposed credential appeared in an AI prompt or uploaded file, rotate it before any further project work.
