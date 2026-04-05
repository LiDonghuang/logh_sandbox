# PR6 Restore Strength Decoupling Implementation Record

Status: implementation record  
Date: 2026-04-05  
Scope: bounded `restore_strength` ownership re-rooting for active `v4a`  
Authority: engineering implementation record; not retirement approval, not merge approval

## 1. Intent

This turn implements the first bounded `restore_strength` decoupling step.

The goal was:

- keep `runtime.movement.v4a.restore_strength`
- remove its active dependence on the old `v3a` / `v3_test` centroid-probe carrier
- establish one native `v4a` runtime host instead

This turn did **not**:

- move the parameter out of `test_run_v1_0.testonly.settings.json`
- retire `v3a`
- retire `v3_test`
- reopen targeting
- perform broad settings taxonomy cleanup

## 2. What changed

### Runtime native host

`runtime/engine_skeleton.py`

- added `movement_surface["v4a_restore_strength"]` as an explicit native runtime movement-surface scalar
- in `integrate_movement(...)`, active `v4a` now scales its cohesion contribution directly by:
  - `v4a_restore_strength`

### Harness bridge removal for active `v4a`

`test_run/test_run_execution.py`

For `movement_model == "v4a"`:

- now writes:
  - `movement_surface["v4a_restore_strength"] = v4a_restore_strength`
- now forces old `v3a` carrier fields to inactive/base values:
  - `movement_surface["v3a_experiment"] = base`
  - `movement_surface["centroid_probe_scale"] = 1.0`

For non-`v4a`:

- old `v3a` carrier behavior remains intact
- `movement_surface["v4a_restore_strength"]` is reset to `1.0`

### Effective-summary truth update

`test_run/test_run_scenario.py`

- `experiment_effective` now remains `v3a`-effective only
- `centroid_probe_scale_effective` now remains `v3a`-effective only
- active `v4a` no longer reports those old `v3a` carrier fields as if they were still effective

### Comments / reference sync

`test_run/test_run_v1_0.settings.comments.json`

- `runtime.movement.v4a.restore_strength` now describes a native `v4a` restore/cohesion-strength seam
- `runtime.movement.v3a.centroid_probe_scale` now states that active `v4a` no longer reuses it

`test_run/test_run_v1_0.settings.reference.md`

- updated to match the new native `v4a` ownership read
- updated to state that `v3a.experiment` / `v3a.centroid_probe_scale` are no longer active `v4a` knobs

## 3. Current ownership after this turn

Current active read is now:

- public surface:
  - `runtime.movement.v4a.restore_strength`
- settings container:
  - `test_run/test_run_v1_0.testonly.settings.json`
- settings path:
  - `test_run/settings_accessor.py`
- active harness transport:
  - `test_run/test_run_scenario.py`
  - `test_run/test_run_execution.py`
- native runtime owner:
  - `runtime/engine_skeleton.py`
  - active `v4a` cohesion contribution seam inside `integrate_movement(...)`

Current honest read:

- `restore_strength` is still a testonly-container parameter
- but it is no longer actively implemented through the old centroid-probe bridge for `v4a`

## 4. What remains unchanged

- `v3a.experiment`
- `v3a.centroid_probe_scale`
- `runtime_cohesion_decision_source = v3_test`
- broader old-family retirement status

So this turn should be read as:

- native `v4a` ownership re-rooting for `restore_strength`
- not full old-family retirement

## 5. Validation

Validation run in this turn:

- `python -m py_compile runtime/engine_skeleton.py test_run/test_run_execution.py test_run/test_run_scenario.py test_run/test_run_entry.py`

- direct `movement_cfg` truth check:
  - `movement_model_effective = v4a`
  - `experiment_effective = base`
  - `centroid_probe_scale_effective = 1.0`
  - `v4a_restore_strength_effective = 0.25`

- short active-surface smoke:
  - `final_tick = 3`
  - `movement_model_effective = v4a`
  - `v4a_restore_strength_effective = 0.25`
  - `runtime_decision_source_effective = v3_test`

- direct engine-surface capture after one-step simulation:
  - `movement_surface_v4a_restore_strength = 0.25`
  - `movement_surface_v3a_experiment = base`
  - `movement_surface_centroid_probe_scale = 1.0`

## 6. Settings/container governance read

This turn keeps Human's container rules intact:

- no silent parameter move between `testonly.settings` and `runtime.settings`
- comments updated in the same turn
- active value now truthfully links to native runtime behavior

If Human later decides `restore_strength` has become a formal runtime-owned parameter,
that should be handled explicitly in a later turn by:

- moving its container location
- updating settings paths if needed
- synchronizing comments/reference in the same turn

## Bottom Line

This turn makes `restore_strength` native for active `v4a` without broadening scope:

- keep the parameter
- keep the current settings container
- remove active dependence on old centroid-probe bridge for `v4a`
- leave `v3a` and old-family retirement for later turns
