---
document_id: context-update-protocol
title: Canonical Context Update and Consistency Protocol
version: 1.0.0
status: required_for_ai_context_maintenance
last_reviewed: 2026-09-25
owner: Anthony Grant
change_policy: explicit_human_approval_required
sensitivity: confidential
---

# Canonical Context Update and Consistency Protocol

## Purpose

This protocol governs updates to CareerOps Local’s candidate, business, brand, project, hardware, and model context. It is designed to prevent silent drift, credential leakage, factual inflation, and accidental overwrites.

## Canonical-source hierarchy

Use sources in this order when resolving facts:

1. An explicit current instruction from Anthony Grant.
2. An approved canonical document in the repository.
3. A resume, portfolio artifact, Git repository, official company record, or owner-approved source artifact.
4. A local runtime check for operational facts such as installed models or hardware.
5. Anything else is `UNVERIFIED` or `INSUFFICIENT_EVIDENCE`.

A model’s prior output is never a source of truth.

## Non-negotiable rules

- Never update a canonical file automatically.
- Never write secrets into Markdown, source control, logs, test fixtures, tickets, prompts, or reports.
- Never paste a `.env`, password-manager export, account credential, personal address, government identifier, tax identifier, financial data, date of birth, recovery code, or API key into AI context.
- Never silently choose one value when sources conflict.
- Preserve history by proposing a patch, not overwriting raw inputs.
- Distinguish `VERIFIED`, `CONCERN`, `UNVERIFIED`, and `INSUFFICIENT_EVIDENCE`.
- Runtime/system facts must be timestamped and rechecked rather than treated as permanent.

## Files governed by this protocol

| File | Purpose | Edit authority |
|---|---|---|
| `CANONICAL_CANDIDATE_DOSSIER.md` | Candidate qualification truth source | Anthony approval required |
| `CANONICAL_BADGR_BUSINESS_CONTEXT.md` | Sanitized business/brand/local-lab context | Anthony approval required |
| `CANONICAL_CONFLICTS_AND_UNKNOWNS.md` | Contradictions and pending validations | Anthony approval required for resolution edits |
| `PROJECT_GUARDRAILS.md` | Privacy, safety, and compliance boundaries | Anthony approval required |
| `JOB_CAPTURE_TEMPLATE.md` | Job capture schema | Anthony approval required for breaking schema changes |

## Required AI workflow

### When an inconsistency is found

1. Do not edit any canonical file.
2. Identify the exact field/claim and source(s).
3. Assess impact and confidence.
4. Add or reference a validation queue ID.
5. Propose a minimal patch.
6. Wait for explicit approval.
7. After approval, make only the approved change and report the file, line/section, and new version/date.

### When the owner provides new information

1. Classify it as personal career, business context, brand asset, system inventory, or secret.
2. If it is a secret, do not store it; recommend a password manager, encrypted secret store, or local ignored `.env` file.
3. If it is a public/professional fact, propose a canonical location and patch.
4. If it conflicts with an existing value, create a validation item rather than replacing the value.
5. Wait for explicit approval.

### When facts are gathered from a job listing

Job-listing facts are not canonical candidate/business facts. Store them as source records with URL, capture date, exact excerpt, platform, and validation status. A listing cannot change the candidate dossier.

## Copy-ready AI prompt for context checks

```text
You are the Context Integrity Reviewer for CareerOps Local.

Read the canonical Markdown context files and the new information I provide. Your job is to identify contradictions, stale operational assumptions, missing evidence, unsafe secrets, and claims that would inflate qualifications or business capabilities.

Rules:
1. Do not edit files.
2. Do not repeat, store, or expose credentials, personal addresses, tax identifiers, financial data, identity documents, recovery codes, or API keys. If supplied, label them SENSITIVE and recommend secure handling.
3. Treat canonical files as authoritative only when marked approved.
4. Treat model output and unauthenticated web claims as non-authoritative.
5. For each issue, provide a Context Validation Notice with: document, field, current value, new/conflicting evidence, impact, confidence, recommended action, and a minimal proposed unified diff.
6. If nothing needs changing, explicitly state: NO CANONICAL UPDATE PROPOSED.
7. Require the exact approval phrase APPROVE PATCH <ID> before any file change.

New information follows:
<PASTE_NEW_INFORMATION_HERE>
```

## Copy-ready AI prompt after approval

```text
You are applying an approved canonical-context patch.

Approval received: <PASTE_EXACT_APPROVAL>

Rules:
1. Apply only the approved patch and no other cleanup or inferred edits.
2. Preserve all unrelated content.
3. Update the document version using semantic patch increment unless the approved change is materially breaking.
4. Update last_reviewed to today’s date.
5. If the patch cannot be applied exactly, stop and explain why; do not improvise.
6. Never add secrets, credentials, personal addresses, identifiers, financial information, or API keys.
7. Return: files changed, exact sections changed, validation-queue status, and verification performed.
```

## Versioning policy

- Patch (`1.0.1`): typo correction, link correction, non-breaking clarification, verified runtime refresh.
- Minor (`1.1.0`): new non-breaking project evidence, new approved field, changed capability scope.
- Major (`2.0.0`): schema/policy change that materially changes matching, safety, or document structure.

## Runtime-inventory refresh prompt

```text
Perform a local runtime inventory refresh only. Do not install, remove, download, authenticate, or modify anything.

Run read-only commands appropriate for Ubuntu and Ollama, such as:
- uname -a
- lsb_release -a or /etc/os-release
- free -h
- lscpu
- lspci
- df -h
- ollama list

Compare results with CANONICAL_BADGR_BUSINESS_CONTEXT.md.
Do not update the canonical file. Produce a Context Validation Notice and proposed patch for any difference. Wait for approval.
```
