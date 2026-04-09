# step3_3d_pr6_old_family_retirement_round8_v3a_default_surface_removal_20260409

## Scope
- active `test_run` default settings / generic accessor surface
- legacy `v3a` experiment support narrowing
- no change to active `v4a` movement behavior

## What changed
- removed pure legacy `v3a` experiment keys from the active default `test_run` settings surface:
  - `runtime.movement.v3a.experiment`
  - `runtime.movement.v3a.centroid_probe_scale`
  - `runtime.movement.v3a.odw_posture_bias.*`
- removed those keys from generic `settings_accessor.RUNTIME_SETTING_PATHS`
- localized maintained legacy `v3a` reads inside `test_run_scenario._build_movement_cfg(...)`
- kept `runtime.movement.v3a.symmetric_movement_sync_enabled` in place because it still owns an active harness-side sync seam

## Why this counts as subtraction
- active default settings file is smaller
- generic accessor surface is smaller
- active truth surface no longer pretends those legacy keys belong to the maintained default `test_run` path
- no wrapper/helper layer was added

## Explicit boundary
- this round does **not** delete the maintained legacy `v3a` path itself
- this round does **not** remove `symmetric_movement_sync_enabled`
- this round does **not** delete `test_run_v1_0_viz.py`

## Follow-up implication
- `test_run_v1_0_viz.py` is still imported by `test_run_entry.py`; delete it only after the active entrypoint is rerooted away from that module
