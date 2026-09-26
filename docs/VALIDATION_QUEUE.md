# Validation Queue

Owner-supplied information that conflicts with, or is absent from, an approved canonical
document. Recorded here rather than applied, per `CONTEXT_UPDATE_PROTOCOL.md`: "If it conflicts
with an existing value, create a validation item rather than replacing the value. Wait for
explicit approval."

This file is **not canonical**. It records pending decisions. Nothing here affects matching,
scoring, or any report until the owner approves a canonical patch and that patch is applied.

Each item states what would change, what it would change, and what approval it needs. Items are
answered by an `APPROVE PATCH <ID>` reply, which is when the canonical document is edited and
the transcription re-mirrored.

---

## VQ-001 — Kubernetes during UVeye employment

**Raised:** 2026-09-26, by the owner, during Phase 4 planning.
**Status:** OPEN — awaiting owner decision.
**Confidence:** UNVERIFIED. Owner-stated, no approved source artifact yet.

### What was stated

Kubernetes was used during employment at UVeye (Field Support Hardware Engineer II, March
2024–April 2025).

### What it conflicts with

`CANONICAL_CANDIDATE_DOSSIER.md`, section "Known evidence gaps and prohibited inferences", lists
`Docker, Kubernetes, Terraform` among items that are **UNKNOWN or UNVERIFIED** and "must not be
claimed without direct approved evidence".

The UVeye employment entry also states no technology list at all, so there is no field this
would go into today. That limit is recorded in `src/careerops/dossier/approved_dossier.py` and
in `docs/ARCHITECTURE.md`.

### Current behaviour, unchanged

A listing requiring Kubernetes scores **0** for that slot and raises `REQUIRED_SKILL_GAP`. That
is correct against the dossier as approved. Nothing is claimed, and nothing is inferred.

### Why it is not applied

Three separate approvals are involved, and none exists yet:

1. A canonical patch removing Kubernetes from the prohibited-inference list, under
   `CONTEXT_UPDATE_PROTOCOL.md`. Removing an item from that list is a material change to
   matching, so it is a major change under the protocol's versioning policy, not a patch bump.
2. A canonical decision on what evidence tier applies. Employment use would be Tier 3
   (multiplier 0.90), which is stronger than Tier 2 project evidence. The dossier's own rule is
   that a tier may never create an unverified skill.
3. A decision on the employment-technology limit. `EmploymentEvidence.technologies` is empty for
   every entry because the canonical employment entries declare no technology list. Adding one
   technology to one entry means deciding whether to declare explicit lists for all four.

### What the owner should consider before approving

Nothing is blocked by leaving this open, and there is a real reason not to rush it. The
dossier's prohibited-inference list is what protects against overstating qualifications, and
"Kubernetes" spans a wide range of claims — from operating inside a cluster someone else ran, to
deploying and maintaining workloads, to owning cluster architecture. The same list separately
prohibits `CI/CD ownership`, `Cloud architecture ownership`, and `MLOps ownership`, and those
remain prohibited regardless of this item.

A narrow, defensible form would name the actual scope rather than the bare product, and would
say which tier it sits at. The scope wording is the owner's to supply; this file will not
propose one.

### Approval needed

`APPROVE PATCH VQ-001` plus the scope wording and the intended evidence tier. The patch would
then touch `CANONICAL_CANDIDATE_DOSSIER.md`, the transcription, and the dossier parity suite
together, so the three cannot drift.

---

## VQ-002 — Distinguishing an unevidenced known technology from an unrecognized term

**Raised:** 2026-09-26, during Phase 4 review.
**Status:** DEFERRED by assistant decision, recorded for owner override.
**Confidence:** VERIFIED as a description of current behaviour.

### The observation

Every required technology that finds no candidate evidence reports
`TechnologyGapReason.UNRECOGNIZED_TERM`. That includes widely known technologies such as
Kubernetes, Terraform, and LangChain. The label reads as though the tool does not know what
Kubernetes is, when the accurate statement is that no candidate evidence supports it.

`TechnologyGapReason.NO_EVIDENCE` exists for the other case — a phrase that resolves to an
approved canonical identifier but has no supporting evidence — and is currently **unreachable by
construction**, because all nine approved identifiers were chosen from the dossier and therefore
all have evidence. It is not dead code; it becomes reachable the moment a canonical identifier is
approved for a technology the candidate does not have.

### Decision, and why

No new enum member is added, for three reasons.

1. **A new member would require inventing a value.** Distinguishing "known technology" from an
   arbitrary string needs a registry of known technologies. The only registry that exists is the
   nine approved identifiers, and a phrase resolving to one of those would not be unmatched. Any
   other list would be invented.
2. **The one legitimate basis is a larger decision.** The dossier's "Known evidence gaps and
   prohibited inferences" section explicitly names Docker, Kubernetes, Terraform, LangChain,
   OpenAI API, Azure OpenAI, and GCP Vertex AI. That is owner-approved canonical content and a
   valid source. Reaching it requires those terms declared explicitly, as `EXPLICIT_SKILL_TERMS`
   does for compound skills, because matching "Kubernetes" against the prose string
   "Docker, Kubernetes, Terraform" is substring matching on prose, which A-6 forbids. Declaring
   a prohibited-term table is an owner decision.
3. **Order matters.** Adding the member before the table would create a member nothing can
   legitimately produce. The table comes first.

`UNRECOGNIZED_TERM` is also accurate for what it describes: the normalization layer recognizes
no canonical identifier for the phrase. It is a statement about normalization, not a claim about
whether the technology exists. A-6 routes exactly this case to the owner-review report section
so the owner can decide whether an identifier should be approved.

### Current behaviour, and why nothing is misleading

Scoring is unaffected either way: an unmatched required slot receives zero, stays in the
denominator, and raises `REQUIRED_SKILL_GAP`. The runner prints the evidence fact beside the
reason, so the output cannot be misread:

    'Weaviate' — UNRECOGNIZED_TERM — no candidate evidence at any tier — raises REQUIRED_SKILL_GAP

### If the owner wants the distinction

The sequence is a prohibited-term declaration first, then an enum member, in one patch:

1. Declare `PROHIBITED_TERMS` in the dossier transcription, each term's words verified present
   in its canonical bullet — the same anti-invention control already proven for
   `EXPLICIT_SKILL_TERMS`.
2. Add a `TechnologyGapReason` member, or relax `PROHIBITED_INFERENCE` to permit
   `best_tier_found=None`, meaning "the listing requires something the dossier explicitly
   disclaims".
3. Extend the dossier parity suite so the declaration cannot drift from the canonical list.

Approval phrase would be `APPROVE PATCH VQ-002`. Nothing is blocked while this stays deferred.
