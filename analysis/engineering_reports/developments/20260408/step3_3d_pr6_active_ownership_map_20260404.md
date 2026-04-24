# PR6 / dev_v2.1 Active Ownership Map

Status: current-state ownership map  
Date: 2026-04-05
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

Current active `restore_strength` ownership is now native on the `v4a`
movement line:

- harness surface:
  - `runtime.movement.v4a.restore_strength`
- runtime owner:
  - `runtime/engine_skeleton.py`
  - `v4a_active` movement path
  - direct scaling of the `v4a` runtime restore vector

Current honest read:

- `v4a.restore_strength` is active
- current runtime read is direct:
  - `restore_term = restore_strength * normalize(restore_vector)`
- this read no longer multiplies by:
  - `formation_rigidity`
  - `pursuit_drive`
  - `mobility_bias`
  - any hidden native restore carrier scale
- `v4a` movement no longer changes when
  - `runtime.selectors.cohesion_decision_source = v2`
  - vs `runtime.selectors.cohesion_decision_source = v3_test`
- old `runtime_cohesion_decision_source -> enemy_cohesion -> deep_pursuit`
  movement influence is no longer an active owner on the `v4a` line

## 3. Still-live transitional `v3a` / `v3_test` dependencies

Current live transitional dependencies still include:

- `runtime_decision_source = v3_test` as the current baseline selector
- old `v3a` experiment surface:
  - `movement_v3a_experiment = exp_precontact_centroid_probe`
- legacy cohesion / collapse observer family still reading the old
  `v2 | v3_test` selector

Current read:

- these are still structurally live
- they should not be described as retired yet
- but they are no longer the active movement owner for
  `v4a.restore_strength`
- they remain cleanup targets after:
  - targeting stabilizes
  - old-family retirement is formally opened

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
- `restore_strength` owner: native `v4a` runtime movement restore scalar
- old `v3a` / `v3_test` family: still live as transitional support, but no longer the active movement owner for `restore_strength`
- old local-enemy Layer-A substrate family: no longer active owner
