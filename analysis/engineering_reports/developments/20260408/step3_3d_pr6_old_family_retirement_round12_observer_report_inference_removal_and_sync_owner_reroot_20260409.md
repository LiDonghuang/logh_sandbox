# Step3 3D PR6 - Old Family Retirement Round 12 - Observer Report-Inference Removal and Sync Owner Reroot - 2026-04-09

Scope: maintained `test_run` settings / harness cleanup

## Why this round existed

After the maintained mainline moved away from the old 2D / BRF path, two residual surfaces still needed cleanup:

1. `runtime.observer.report_inference`
   - still present in active settings/comments/accessor
   - but no longer had any active reader after BRF retirement

2. `symmetric_movement_sync_enabled`
   - still lived under legacy-named `runtime.movement.v3a.*`
   - even though its real role is a run-level harness execution control for maintained `v4a`

This round removes the dead observer branch and reroots the sync switch to an honest maintained owner.

## What changed

### 1. Removed dead observer report-inference surface

Deleted from the maintained active surface:

- `runtime.observer.report_inference`

Removed from:

- `test_run/test_run_v1_0.runtime.settings.json`
- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/settings_accessor.py`

Static owner audit confirmed there was no remaining active reader for this subtree.

### 2. Moved symmetric movement sync to run_control

Rerooted:

- from `runtime.movement.v3a.symmetric_movement_sync_enabled`
- to `run_control.symmetric_movement_sync_enabled`

Updated:

- `test_run/test_run_v1_0.runtime.settings.json`
- `test_run/test_run_v1_0.testonly.settings.json`
- `test_run/settings_accessor.py`
- `test_run/test_run_scenario.py`
- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`

Maintained truth is now:

- the switch is not a `v3a` movement parameter
- it is a run-level harness control that affects cross-fleet update ordering behavior

## What this round did not do

This round did **not**:

- delete `runtime.observer.event_bridge`
- delete `runtime.observer.collapse_shadow`
- redesign observer meaning
- change maintained movement or combat semantics

Those observer subtrees still have active readers in the maintained harness / telemetry path.

## Result

This round further shrank the maintained active surface:

- one dead observer subtree removed
- one live switch rerooted to its honest maintained owner
- fewer mixed-era names left in the active default configuration
