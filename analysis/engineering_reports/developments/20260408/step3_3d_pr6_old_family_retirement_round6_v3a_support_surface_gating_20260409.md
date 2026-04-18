# Step3 3D PR6 - Old Family Retirement Round 6 - v3a Support-Surface Gating - 2026-04-09

## Scope

- baseline/runtime: local cleanup branch only
- target line: active `v4a` movement path
- intent: subtraction-first narrowing of old-family support surface

## Problem

After the restore / neutral-battle cleanup slices, active `v4a` no longer depended on the old `movement.v3a.*` mechanism family for movement semantics.

However, the active path still:

- read `movement.v3a.experiment`
- read `movement.v3a.centroid_probe_scale`
- read `movement.v3a.odw_posture_bias.*`
- wrote these values into the runtime movement surface even when `movement_model == v4a`

So the old family remained artificially present on the active `v4a` path, even though it no longer owned live `v4a` behavior.

## Decision

Retire this support surface from the active `v4a` path without deleting the legacy/non-`v4a` path itself.

This round does **not** retire:

- `symmetric_movement_sync_enabled`
- `collapse_signal` / `cohesion_decision_source`
- anchor-regression `v3a` support

Those remain separate cleanup topics.

## Implementation

### `test_run/test_run_scenario.py`

- `_build_movement_cfg()` no longer reads or validates `movement.v3a.*` when `movement_model_effective != "v3a"`
- the active `v4a` movement config no longer carries:
  - `experiment_effective`
  - `centroid_probe_scale`
  - `centroid_probe_scale_effective`
  - `odw_posture_bias`

### `test_run/test_run_execution.py`

- when `movement_model == "v4a"`, the runtime movement surface no longer carries:
  - `v3a_experiment`
  - `centroid_probe_scale`
  - `odw_posture_bias_enabled`
  - `odw_posture_bias_k`
  - `odw_posture_bias_clip_delta`

### `runtime/engine_skeleton.py`

- active `v4a` no longer reads:
  - `v3a_experiment`
  - `centroid_probe_scale`
  - `odw_posture_bias_*`
- those reads are now confined to the non-`v4a` path only
- the default `_movement_surface` seed no longer carries these legacy keys by default

## Truth surface update

- `test_run_v1_0.settings.comments.json`
- `test_run_v1_0.settings.reference.md`

Both now say more plainly that the `movement.v3a.*` subtree is legacy/non-`v4a` only and is no longer read by active `v4a`.

## Current read

This is a true old-family support-surface reduction:

- the active `v4a` path is smaller
- one mixed-era bridge family no longer rides along by default
- no new wrapper, helper, or fallback was added

## Out of scope

- deleting the `v3a` subtree itself
- removing `baseline` selector aliases
- retiring `cohesion_decision_source`
- retiring `symmetric_movement_sync_enabled`
- broader `v3a` / `v3_test` runtime-family removal
