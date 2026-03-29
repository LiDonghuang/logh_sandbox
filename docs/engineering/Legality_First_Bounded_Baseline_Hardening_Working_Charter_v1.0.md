# Legality First-Bounded Baseline Hardening Working Charter v1.0

Status: Active
Authority: Engineering / Governance working charter
Scope: Step 3 legality line bounded baseline hardening only
Mode: Repo-side working charter; APP local-file sync required

## 1. Phase Identity

This phase is:

* `legality first-bounded baseline hardening phase`

It exists to harden the already-merged first bounded legality baseline without silently widening into deeper redesign.

## 2. Current Accepted Baseline Identity

Current merged legality bounded baseline commit:

* `4e6a9163125e13cf62b9ca706c15d72114d3ec5a`

Supporting evidence commits already in repo include:

* `86df7f2` for the human-trackable validation sample policy/example
* `aefeea1` for the first bounded baseline validation pack

## 3. Working Method

Within this phase:

* Engineering performs multiple bounded hardening iterations
* Human observes, judges, corrects, and redirects
* Governance intervenes only at real gates, disputes, or explicit escalation triggers

This charter reduces per-iteration governance micromanagement without removing boundary discipline.

## 4. Per-Iteration Minimum Evidence

Each substantive iteration should leave:

* machine-checkable metrics
* at least one minimal human-readable artifact
* one short bounded interpretation of:
  * what improved
  * what worsened
  * what remains unclear

## 5. Preferred Human-Readable Artifact Forms

Preferred forms are the lightest useful ones first:

* direct animation sample or short frame sequence when practical
* plot / chart
* tick-level CSV
* short targeted long-form trace
* before / after comparison when useful

Default preference is minimal size.

Do not expand into heavier artifacts unless the human asks for them or the lighter option is insufficient.

## 6. Hardening Focus

Hardening work in this phase should focus on:

* seam stability
* data-surface cleanliness
* traceability quality
* bounded validation breadth
* semantic cleanliness

## 7. Still Explicitly Closed

The following remain closed during this phase:

* personality reintegration
* deeper movement-layer recoupling
* broad architecture rewrite
* viewer semantic ownership redesign
* algorithm-finalization by stealth

## 8. Return-to-Governance Triggers

Engineering must return to Governance when:

* the seam no longer looks valid
* baseline replacement is being considered
* deeper legality algorithm redesign is being proposed
* cross-layer ownership starts to drift

## 9. Suggested Remote-Mode Defaults

Under this charter, the default remote modes for later iterations should be:

* docs / analysis only: `[DIRECT PUSH]`
* code-changing bounded candidate needing review: `[BRANCH + PR]`

## 10. Standing Authorization

Once this charter is committed:

* Engineering may run several bounded hardening iterations under it without waiting for new Governance prompts
* each substantive iteration must leave minimal human-readable evidence
* Human may redirect at any time
* Governance is called back only at the triggers above
