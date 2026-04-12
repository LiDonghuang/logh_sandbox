# PR6 / dev_v2.1 Active Ownership Map - Post Decoupling

Status: current-state ownership map  
Date: 2026-04-05  
Scope: active targeting owner, active restore owner, and remaining still-live old-family surfaces after bounded `restore_strength` decoupling  
Authority: working map only; not doctrine, not merge approval

## 1. Active targeting owner

Current active unit-level targeting behavior remains owned in:

- `runtime/engine_skeleton.py::resolve_combat()`

Current read:

- candidate enemies are still filtered by max `attack_range`
- target choice uses fixed expected-damage-guided merit:
  - `normalized_hp / expected_damage_ratio`
- expected damage reads as:
  - `angle_quality * range_quality`

Current live parameter surfaces:

- `runtime.physical.fire_control.fire_quality_alpha`
- `runtime.physical.fire_control.fire_optimal_range_ratio`

## 2. Where `restore_strength` is truly active now

Current active `restore_strength` ownership is now:

- public surface:
  - `runtime.movement.v4a.restore_strength`
- settings container:
  - `test_run/test_run_v1_0.testonly.settings.json`
- harness transport:
  - `test_run/test_run_scenario.py`
  - `test_run/test_run_execution.py`
- native runtime owner:
  - `runtime/engine_skeleton.py`
  - active `v4a` cohesion contribution seam in `integrate_movement(...)`

Current honest read:

- `v4a.restore_strength` is active
- it is still stored in the testonly settings container
- but it is no longer active by reusing the old centroid-probe bridge

## 3. What old-family surfaces are still live

The following old-family surfaces are still structurally live:

- `runtime_decision_source = v3_test`
- `runtime.movement.v3a.experiment`
- `runtime.movement.v3a.centroid_probe_scale`

Current honest read:

- they remain live for old-family support, especially `v3a`
- they should not yet be described as broadly retired
- they are no longer active `v4a.restore_strength` owner surfaces

## 4. What has already been removed from the active v4a path

The following old bridge read is no longer active for `v4a.restore_strength`:

- `movement_surface["v3a_experiment"] = exp_precontact_centroid_probe`
- `movement_surface["centroid_probe_scale"] = restore_strength`

The following human-facing residues were also removed from the default active
`v4a` launcher/report surface:

- `battle_restore_bridge_active`
- default export of:
  - `movement_v3a_experiment_effective`
  - `centroid_probe_scale_effective`

Those two `v3a` fields are now exported only when:

- `movement_model_effective == "v3a"`

## 5. Legacy local-enemy carriers

Current active Layer-A far-field read is still not owned by the older
local-enemy substrate family.

The following remain historical / non-active Layer-A owners:

- `nearest5_centroid`
- `weighted_local`
- `local_cluster`
- `soft_local_weighted`
- `soft_local_weighted_tight`

## Bottom Line

Current ownership should now be read as:

- targeting owner: runtime hot path
- `restore_strength` owner: active `v4a` public surface feeding a native `v4a` runtime seam
- old `v3a` / `v3_test` family: still live only as old-family support, not as active `restore_strength` owner
- active launcher/report surface: narrower than before, with bridge-era residue removed from default `v4a` output
