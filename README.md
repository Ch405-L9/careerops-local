# CareerOps Local — Claude Code Starter Pack

This pack is a safe, local-first project brief for building **CareerOps Local**: an evidence-based job and contract intelligence assistant for Anthony Grant, with a future optional business-opportunity mode for BADGRTechnologies LLC.

## Start here

1. Create and enter a new repository:
   ```bash
   mkdir -p ~/projects/careerops-local
   cd ~/projects/careerops-local
   git init
   ```
2. Copy this pack into the repository root, preserving paths.
3. Confirm the secret business-info files are **not** copied into the repository. They contain credentials and personal information.
4. Start Claude Code and paste the contents of `PROMPT_PHASE_0.md`.
5. Claude Code must stop after its Phase 0 plan. Review it before allowing file changes.

## Pack contents

- `PROMPT_PHASE_0.md` — paste-first instruction for Claude Code.
- `CANONICAL_CANDIDATE_DOSSIER.md` — approved personal/career facts for matching.
- `CANONICAL_BADGR_BUSINESS_CONTEXT.md` — sanitized, non-secret BADGR context for the future business mode and visual identity.
- `CANONICAL_CONFLICTS_AND_UNKNOWNs.md` — known contradictions and facts requiring confirmation.
- `CONTEXT_UPDATE_PROTOCOL.md` — canonical, human-approved change process and prompt.
- `JOB_CAPTURE_TEMPLATE.md` — permitted manual Wellfound job-capture template.
- `PROJECT_GUARDRAILS.md` — scope, privacy, security, and platform-compliance boundaries.

## Critical security notice

The supplied business-information files contained passwords, account identifiers, personal addresses, sensitive personal data, and business identifiers. Those are intentionally excluded from this pack. Because credentials appeared in a submitted file, change or rotate every exposed password immediately, enable unique passwords and MFA, and move account credentials to a reputable password manager. Never place passwords, API keys, `.env` files, recovery codes, financial identifiers, or identity documents in this repository or an LLM prompt.

## Canonical-data rule

The canonical Markdown files in this pack are human-approved inputs. They are not self-updating. AI may **propose** a structured patch after identifying an inconsistency, but must not change canonical files without explicit approval.
