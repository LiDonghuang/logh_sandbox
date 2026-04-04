# PR6 Status / Restore / Cleanup Report for Governance

Status: governance update memo  
Date: 2026-04-04  
Scope: project status after `eng/two-layer-spacing-first-bounded-impl`, restore-strength explanation, and old-2D cleanup direction  
Authority: discussion/update only; not merge request, not default-switch request

## I. Current Project Status After `eng/two-layer-spacing-first-bounded-impl`

### 1. What remains structurally valid

Since `eng/two-layer-spacing-first-bounded-impl` / PR `#6`, the project has
opened and bounded several real lines rather than only discussion lines:

- two-layer spacing read
- soft morphology reference carrier
- transition-movement seam
- battle standoff / hold relation
- 3D viewer-side `movement` / `posture` direction split
- 3D debug / observation surface hardening

Those lines should still be read as the real opening package of the current
`v4a` effort.

### 2. What failed locally

After that branch, a local incident occurred during battle-line smoothing /
stabilization work. The main local failure pattern was:

- too many battle-facing local probes and smoothing edits accumulated in one
  dirty worktree
- diagnosis drifted
- one important active carrier (`v4a.restore_strength`) was incorrectly judged
  dead and retired

That local incident is already recorded separately in:

- [step3_3d_pr6_formal_failure_audit_20260404.md](/e:/logh_sandbox/analysis/engineering_reports/developments/20260404/step3_3d_pr6_formal_failure_audit_20260404.md)

### 3. Where the line currently stands

The current pushed recovery anchor is now on:

- branch: `dev_v2.1`

Pushed recovery commits:

- `cfd8ecc` `v2.1: reactivate v4a restore strength bridge`
- `787bf0d` `v2.1: restore v4a near-contact smoothing group`

Current engineering read:

- formation / hold behavior has been brought back to a state Human currently
  reads as broadly reasonable again
- this does **not** mean the architecture is now clean
- it means the line has recovered a usable anchor and can move forward again in
  bounded steps

### 4. Current targeting opening

This update turn also carries a first pushed targeting candidate on `dev_v2.1`:

- `runtime/engine_skeleton.py::resolve_combat()`
- expected-damage-guided target selection
- `fire_optimal_range_ratio`
- angle + range participating earlier in target choice

Human's preliminary 3D read is:

- better than the previous effectively unrestricted over-concentrated focus fire
- tuning and optimization still remain later work

So the current honest status is:

- pushed anchor recovered
- targeting opening now genuinely started on the active branch
- further cleanup should proceed from this recovered anchor, not from the failed
  local incident state

## II. Restore-Strength Panic Explanation

### 1. What the panic was

Engineering previously concluded that:

- `runtime.movement.v4a.restore_strength`

was no longer materially active and could be retired.

That conclusion was wrong.

### 2. What actually happened

High-trust comparison against the `0402` anchor showed that under:

- `runtime_decision_source_effective = v3_test`

the current `v4a` line was still reusing the runtime centroid-probe carrier.

In practice, the real active difference was:

- `v3a_experiment = exp_precontact_centroid_probe`
- `centroid_probe_scale = 0.25`

versus the mistaken local retirement state:

- `v3a_experiment = base`
- `centroid_probe_scale = 1.0`

Restoring that path reproduced the `0402` `tick = 1` movement decomposition
exactly.

### 3. Governance-level interpretation

Governance should not read this as:

- "old 2D magic fixed the project"

The sharper read is:

- the current `v4a` line was still structurally leaning on an old runtime
  carrier
- Engineering mistakenly believed that dependency had already ended
- the resulting retirement created a false local crisis and wasted time

### 4. Why this matters now

The restore-strength incident means two things at once:

1. short-term recovery was correct  
   - restoring the path was necessary to recover the previously acceptable line

2. medium-term structure is still wrong  
   - `v4a` should not permanently depend on old `v3_test` runtime carrier

So the governance-facing read should be:

- restoring `restore_strength` was the correct immediate repair
- but this also proved the architecture is still transitional and not yet clean

## III. Old 2D Mechanism Removal / Retirement Direction

### 1. Engineering read

Engineering now believes a serious subtraction-first cleanup line is necessary
after targeting stabilizes.

This is not only for elegance. It is now a maintainability and diagnosis issue.

The current codebase still carries too many mixed-era mechanisms across:

- `runtime/engine_skeleton.py`
- `test_run/test_run_execution.py`
- `test_run/test_run_scenario.py`
- layered settings surfaces
- comments / reference files

### 2. What should eventually be removed or retired

The main future cleanup target families are:

- old `v3a` movement-era carriers that remain only as transitional support
- old `v3_test` / centroid-probe dependence that `v4a` still leans on
- older `pre_tl_target_substrate` / local enemy-reference legacy carriers once
  the new targeting line stabilizes
- stale comments / interface claims that no longer match active mechanism
  reality

### 3. What should not happen

Engineering does **not** recommend:

- keeping the old 2D mechanism families indefinitely as silent fallback
- preserving ambiguous mixed ownership just because it is historically familiar
- trying to "clean up" by adding more wrappers or compatibility layers

### 4. Recommended retirement handling

For historically important but no-longer-active script lines, Engineering sees
two acceptable destinations:

1. move them into a clearly labeled local retired folder  
2. rely on existing frozen historical branches as the preservation carrier

The key point is:

- active default surfaces should become smaller
- historical preservation should not continue to pollute active mechanism
  ownership

### 5. Recommended next sequencing

Engineering recommends the following order:

1. finish bounded targeting logic stabilization  
2. move `restore_strength` off the old `v3_test` carrier and onto a true `v4a`
   owner  
3. then begin subtraction-first retirement of `v3a` / old 2D mechanism paths

This order matters because:

- targeting still needs the current recovered anchor
- `restore_strength` still proves a live transitional dependency
- only after those are resolved can `v3a` retirement be done honestly

## Bottom Line

Governance should currently read the project as:

- PR `#6` was a real opening branch and remains historically important
- a serious local failure happened afterward, but it has now produced one
  recovered anchor on `dev_v2.1`
- `restore_strength` was not a fake issue; it exposed a real transitional
  dependency that Engineering had misread
- the next important phase is not random further patching, but:
  - targeting stabilization
  - `restore_strength` decoupling from old runtime carrier
  - then subtraction-first retirement of old 2D mechanism families
