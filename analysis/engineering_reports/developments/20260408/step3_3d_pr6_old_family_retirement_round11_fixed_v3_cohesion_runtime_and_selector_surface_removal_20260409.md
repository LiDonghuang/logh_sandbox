# Step3 3D PR6 - Old Family Retirement Round 11 - Fixed v3 Cohesion Runtime and Selector Surface Removal - 2026-04-09

Scope: baseline/runtime + maintained `test_run` mainline cleanup

## Why this round existed

After Round 10 moved the maintained movement baseline to `v4a`, the active mainline still carried a stale mixed-era cohesion story:

- `runtime.selectors.cohesion_decision_source` still existed in public settings
- `runtime.semantics.collapse_signal.v3_*` still existed in public settings
- `test_run` scenario/runtime wiring still passed decision-source and collapse multipliers
- runtime cohesion code still retained a maintained `v2 | v3_test` selector branch even though the active mainline had already converged on fixed `v3_test`

This round removes that selector surface and makes the maintained runtime cohesion line explicit.

## What changed

### 1. Maintained public settings surface no longer exposes cohesion-source selection

Removed from the maintained settings/accessor surface:

- `runtime.selectors.cohesion_decision_source`
- `runtime.semantics.collapse_signal.v3_connect_radius_multiplier`
- `runtime.semantics.collapse_signal.v3_r_ref_radius_multiplier`

Updated:

- `test_run/settings_accessor.py`
- `test_run/test_run_v1_0.runtime.settings.json`
- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`
- `README.md`

### 2. Maintained scenario/execution wiring no longer carries the removed selector path

In the maintained `test_run` mainline:

- `_build_run_cfg()` no longer resolves or returns runtime decision-source fields
- `_build_movement_cfg()` no longer carries collapse-signal multipliers
- `prepare_active_scenario()` / `prepare_neutral_transit_fixture()` no longer pass decision-source through `runtime_cfg`
- `run_simulation()` no longer writes:
  - `engine.runtime_cohesion_decision_source`
  - `V2_CONNECT_RADIUS_MULTIPLIER`
  - `V3_CONNECT_RADIUS_MULTIPLIER`
  - `V3_R_REF_RADIUS_MULTIPLIER`

### 3. Maintained runtime cohesion now uses a single fixed geometry

In `runtime/engine_skeleton.py`:

- `_compute_cohesion_v2_geometry()` was removed from the maintained runtime path
- `_compute_cohesion_v3_geometry()` now uses fixed maintained values:
  - `v3_connect_multiplier = 1.1`
  - `v3_r_ref_multiplier = 1.0`
- `evaluate_cohesion()` no longer branches on runtime decision source
- maintained runtime cohesion now always computes the same `v3_test` geometry on the active mainline

## What this round did not do

This round did **not**:

- delete `runtime.observer`
- delete hostile contact-model experiment paths such as `hybrid_v2` or `intent_unified_spacing_v1`
- move or retire `runtime.movement.v3a.symmetric_movement_sync_enabled`
- remove the remaining legacy variable names inside non-`v4a` runtime movement code

Those are separate owner groups.

## Result

The maintained mainline now tells a more truthful story:

- movement baseline is `v4a`
- maintained runtime cohesion geometry is fixed `v3_test`
- old selector/collapse settings for `v2 | v3_test` switching are no longer part of the maintained public surface

This is a real subtraction step, not just a comment cleanup:

- less active settings surface
- less scenario/execution plumbing
- less maintained runtime branching
