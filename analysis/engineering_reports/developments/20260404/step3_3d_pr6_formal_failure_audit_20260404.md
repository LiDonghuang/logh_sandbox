# PR6 Formal Failure Audit - 2026-04-04

## Scope

- Branch / line: `eng/two-layer-spacing-first-bounded-impl`, PR `#6` local continuation
- Surface under audit:
  - `test_run` / harness-side `v4a` battle and neutral mechanism work
  - especially the local work after the Human-confirmed good window and the later request to add:
    - hold oscillation smoothing
    - hold internal stabilization
- Non-scope:
  - `runtime/engine_skeleton.py`
  - canonical / governance files
  - merge-readiness
  - closure approval

This audit is a formal engineering failure audit for the current local thread.

It is not a continuation of mechanism debugging.

## Intended Scope

The intended scope of the failed round was narrow:

1. preserve the now-accepted core read that `hold` should be a reversible signed relation
2. improve:
   - hold oscillation smoothness
   - hold-time internal body stability
3. keep work inside `test_run` / harness-only implementation
4. avoid frozen runtime changes
5. avoid broad structure changes

The round was **not** intended to:

- redesign `v4a` ownership structure
- reopen broad formation doctrine
- broaden parameter surfaces repeatedly
- degrade battle or neutral formation realization

## Explicit Failure Statement

This round **failed**.

It failed in a **mixed** sense:

### 1. implementation failure

Local mechanism edits did not reliably improve the targeted problem set and repeatedly introduced or preserved visible errors, including:

- `battle 1->4` early center-ahead arc
- `neutral 1->4 / 2->4` single-front outlier
- post-contact disorder

### 2. workflow / control failure

Diagnosis drifted repeatedly.

Too many local battle-facing probes, smoothers, and temporary mechanisms were stacked in one dirty worktree without establishing one stable trustworthy anchor first.

This reduced confidence in causal attribution and damaged Human trust.

### 3. conceptual boundary failure

The round did not maintain a strict enough subtraction-first discipline after the line began to drift.

Even when some local changes were well-intentioned or partially useful, the total battle path became too coupled for reliable reasoning in-thread.

## Divergence Point

The highest-trust divergence point is the **Human-confirmed regression window**:

- the line was still judged reasonable immediately before the request to continue into:
  - `Hold` oscillation smoothing
  - `Hold` internal stabilization
- the line was later judged degraded after that stage and its follow-on local edits

This Human-confirmed window is the authoritative regression window for future isolation.

This audit does **not** claim that every mechanism introduced after that point is equally guilty.

It does claim that this is the correct operational divergence window.

## Damage Classification

### A. Docs-only damage

Status: **moderate**

Observed damage:

- chronology documents and local records accumulated quickly
- some records correctly captured chronology but could be misread as proof of correctness if consumed carelessly
- one important documentation mismatch exists:
  - `test_run_v1_0.settings.comments.json` still describes `v4a` as reusing `centroid_probe_scale` unchanged
  - current code does not behave that way in active `v4a`

Impact:

- misleading record interpretation
- extra reading burden
- higher risk of trusting stale comments over code

### B. `test_run` / harness damage

Status: **severe**

Observed damage:

- `test_run/test_run_execution.py` accumulated overlapping local battle probes and subtractive reversals in one thread
- battle-facing local mechanisms were repeatedly modified without a stable isolation anchor
- the active harness path became too noisy for confident intuition-led diagnosis
- Human-visible bad results persisted:
  - battle early arc
  - neutral outlier
  - post-contact disorder

Impact:

- lowered causal confidence
- high misdiagnosis risk
- lower maintainability
- damaged Human trust

### C. Viewer-only damage

Status: **limited / secondary**

Observed damage:

- viewer HUD and direction/debug work changed repeatedly during the same period
- however, the current primary incident is not viewer-only
- visual confusion largely reflects unstable mechanism state rather than a pure viewer defect

Impact:

- extra reading burden
- some observer clutter
- but not the principal failure class for this incident

### D. Runtime / canonical / branch-structure damage

Status: **contained**

Observed damage:

- no frozen runtime core rewrite was applied
- no canonical or governance files were modified as part of the failed mechanism experimentation
- branch structure remains intact

Impact:

- limited
- this failure remains primarily a local harness / experiment-surface failure, not a canonical-layer corruption event

## What Remains Valid

The following should still be preserved as valid or provisionally valid:

1. the Human-confirmed regression window
2. the principle that `contact` is not a one-time event
3. the read that `hold` should be a reversible signed relation rather than a hard contact latch
4. the hard validation gates:
   - fleet-centroid trajectory
   - alive-unit body observation
   - fire-efficiency as a default battle observation surface
5. the warning that chronology records are not proof of correctness
6. the warning that the current dirty local `test_run` battle path is too noisy for intuition-led continued debugging
7. the fact that some recent local additions have already been retired and should remain retired:
   - hold smoothing public knobs
   - far-phase probe conditions

## What Must Be Frozen / Rolled Back / Quarantined

### Freeze

Freeze the current local worktree as an incident scene.

Do not continue broad mechanism debugging in this thread.

### Roll back

For future recovery work, treat the following recent battle-only local probes as already invalidated / non-authoritative:

- far-phase axis/bridge probe branches
- hold-smoothing public surface
- near-contact internal stabilization public surface

Do not reuse them as trusted foundations for the next diagnosis pass.

### Quarantine

Quarantine the following for the next thread:

- speculative causal theories from the failed thread
- intuition-led root-cause claims that were not backed by strict subtraction A/B
- stale v4a/cohesion comment claims that no longer match active code

## Recovery Recommendation

**Recovery recommendation: freeze-and-audit.**

Meaning:

1. freeze current local state as an incident scene
2. do not continue broad debugging in this thread
3. open a fresh thread
4. use the Human-confirmed regression window as the highest-trust anchor
5. perform subtraction-first isolation planning before any new mechanism edit

This audit does **not** recommend:

- immediate broad rollback by intuition
- immediate continued freeform debugging
- reopening wide theory expansion
- adding new parameters before isolation

## Operational Next Step

If a fresh thread is opened, its first task should be:

- establish one trustworthy local anchor from the Human-confirmed good/bad window
- plan subtraction-first isolation of the active `test_run/test_run_execution.py` battle path
- avoid new mechanism theory until one active bad path is isolated

## Bottom Line

This case remains open.

The correct read is:

- the round failed in a mixed implementation/workflow/control sense
- the main damage is in the local `test_run` / harness battle path
- frozen runtime and canonical layers remain contained
- the current thread should stop mechanism debugging
- recovery should proceed under a freeze-and-audit read, not under continued intuition-led iteration

