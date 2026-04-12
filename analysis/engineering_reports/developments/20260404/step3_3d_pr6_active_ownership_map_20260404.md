# PR6 / dev_v2.1 Active Ownership Map

Status: current-state ownership map  
Date: 2026-04-04  
Scope: active targeting owner, active restore owner, and still-live transitional dependencies  
Authority: working map only; not doctrine, not merge approval

## 1. Active targeting owner

Current active unit-level targeting behavior is owned in:

- `runtime/engine_skeleton.py::resolve_combat()`

Current read:

- candidate enemies are still filtered by max `attack_range`
- target choice now uses a fixed expected-damage-guided merit:
  - `normalized_hp / expected_damage_ratio`
- expected damage currently reads as:
  - `angle_quality * range_quality`

Current live parameter surfaces:

- `runtime.physical.fire_control.fire_quality_alpha`
  - directional fire-quality coefficient
- `runtime.physical.fire_control.fire_optimal_range_ratio`
  - inner full-quality range band as a ratio of `attack_range`

## 2. Where `restore_strength` is truly active

Current active `restore_strength` ownership is transitional, not native:

- harness surface:
  - `runtime.movement.v4a.restore_strength`
- harness bridge:
  - `test_run/test_run_execution.py`
  - writes `movement_surface["centroid_probe_scale"]`
- runtime carrier:
  - `runtime/engine_skeleton.py`
  - under `runtime_decision_source = v3_test`
  - through the `exp_precontact_centroid_probe` path

Current honest read:

- `v4a.restore_strength` is active
- but it is currently active by reusing an older runtime carrier
- this is a real transitional dependency, not a final clean owner

## 3. Still-live transitional `v3a` / `v3_test` dependencies

Current live transitional dependencies include:

- `runtime_decision_source = v3_test`
- runtime centroid-probe carrier used by `v4a.restore_strength`
- `movement_v3a_experiment = exp_precontact_centroid_probe`

Current read:

- these are still structurally live
- they should not be described as retired yet
- they are cleanup targets only after:
  - targeting stabilizes
  - `restore_strength` is reconnected to a true `v4a` owner

## 4. Legacy local-enemy carriers no longer active as Layer-A owners

Current active Layer-A far-field read is no longer owned by the older local-enemy substrate family.

The following are no longer active Layer-A owners on the current line:

- `nearest5_centroid`
- `weighted_local`
- `local_cluster`
- `soft_local_weighted`
- `soft_local_weighted_tight`

Current read:

- these remain historical harness material
- they should not be treated as the active Layer-A battle owner
- current Layer-A ownership is the newer bounded battle relation / standoff line in `test_run/test_run_execution.py`

## Bottom Line

Current ownership should be read as:

- targeting owner: runtime hot path
- `restore_strength` owner: `v4a` harness surface reusing old `v3_test` runtime carrier
- old `v3a` / `v3_test` family: still live as transitional support
- old local-enemy Layer-A substrate family: no longer active owner
