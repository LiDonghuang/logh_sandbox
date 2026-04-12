# Step3 3D PR6 - Old Family Retirement Round 10 - Baseline to v4a and Maintained v3a Retirement - 2026-04-09

Scope: baseline/runtime + active `test_run` mainline cleanup

## Why this round existed

Earlier cleanup rounds narrowed old-family `v3a` surfaces, but the maintained mainline still told an untrue story:

- `baseline` still resolved to `v3a`
- `run_simulation()` still accepted maintained `v3a`
- runtime movement default still fell back to `v3a`
- `test_run_anchor_regression.py` still forced a maintained `v3a` run

Human explicitly approved formal baseline replacement instead of partial retirement.

## What changed

### 1. Maintained baseline now resolves to `v4a`

In `test_run/test_run_scenario.py`:

- `resolve_movement_model()` now sets `baseline_model = "v4a"`
- explicit `movement_model = "v3a"` is rejected as retired from the maintained `test_run` mainline
- the old maintained `v3a` movement-config branch was removed

### 2. Maintained execution path now only accepts `v4a`

In `test_run/test_run_execution.py`:

- `run_simulation()` now accepts only maintained `runtime_cfg["movement_model"] == "v4a"`
- the maintained branch no longer writes legacy `v3a` movement-surface keys
- the maintained movement surface always writes:
  - `model = "v4a"`
  - `v4a_restore_strength`

### 3. Runtime default moved away from silent `v3a`

In `runtime/engine_skeleton.py`:

- `_movement_surface["model"]` default is now `v4a`
- runtime movement-model read defaults to `v4a`
- invalid runtime movement model now fails fast instead of silently remapping to `v3a`

This does **not** delete the remaining legacy runtime branch body yet.
It removes maintained default entry into that branch.

### 4. Old maintained anchor-regression script retired

`test_run/test_run_anchor_regression.py` was removed from the active tree.

That script forced maintained `v3a` execution and no longer matched current maintained baseline truth.

## Truth-surface updates

Updated:

- `README.md`
- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`

These now state:

- maintained movement baseline is `v4a`
- maintained mainline does not support explicit `v3a` execution
- `runtime.movement.v3a.symmetric_movement_sync_enabled` remains only as a legacy-named harness seam

## Explicit non-goals

This round did **not**:

- delete the remaining legacy runtime `v3a` branch body
- touch `runtime.selectors.cohesion_decision_source`
- retire `runtime.movement.v3a.symmetric_movement_sync_enabled`
- change active `v4a` battle/neutral behavior

## Result

This round is a real baseline replacement / retirement step:

- maintained baseline moved from `v3a` to `v4a`
- maintained `v3a` execution path was retired from active `test_run`
- old-family runtime code may still exist locally, but it is no longer the maintained entry path
