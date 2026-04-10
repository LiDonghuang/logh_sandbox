# Step3 / PR6 Old-Family Retirement Round 14

Status: implemented local cleanup record  
Scope: maintained-mainline FSR actuator retirement, `fsr_strength` surface removal, and `contact_model -> contact` runtime bundle reroot  
Authority: local engineering record, not canonical governance authority

## 1. Why this round exists

FSR had already been disabled for active `v4a`, but the project still carried:

- an actuator block inside `runtime/engine_skeleton.py`
- `fsr_strength` in maintained runtime settings
- `contact_model` as a stale bundle name even though the remaining active content was now just contact/hysteresis and hostile-contact impedance

This round removes the maintained-mainline actuator and shrinks the public surface accordingly.

## 2. Active owner before the change

### Runtime actuator

- `runtime/engine_skeleton.py`
  - `_fsr_surface`
  - per-tick FSR block inside `integrate_movement()`

### Harness/runtime bridge

- `test_run/test_run_execution.py`
  - wrote `fsr_surface["enabled"]`
  - wrote `fsr_surface["strength"]`

### Maintained settings surface

- `test_run/test_run_v1_0.runtime.settings.json`
  - `runtime.physical.contact_model.fsr_strength`
- `test_run/settings_accessor.py`
  - runtime path mapping for `fsr_strength`
- settings comments / reference / README

## 3. What changed

### A. FSR actuator removed from maintained runtime path

Removed from `runtime/engine_skeleton.py`:

- `_fsr_surface`
- `fsr_enabled`
- `fsr_strength`
- `lambda_delta`
- `kappa_f`
- `k_f`
- `lambda_raw`
- `lambda_f`
- per-unit isotropic position rewrite driven by the FSR lambda

### B. Passive fleet-radius diagnostics retained

The old FSR block was reduced to passive diagnostics only when runtime diagnostics are enabled:

- `centroid_x`
- `centroid_y`
- `r_cur`
- `r_eq`
- `s_f`
- `n_alive`
- `n0`

Runtime state names were rerooted from FSR naming to neutral naming:

- `_diag_surface["fsr_diag_enabled"]` -> `_diag_surface["runtime_diag_enabled"]`
- `_debug_state["fsr_reference"]` -> `_debug_state["fleet_radius_reference"]`
- `debug_last_fsr_stats` -> `debug_last_fleet_radius_stats`

### C. Public surface removal

Removed from maintained settings/runtime surface:

- `runtime.physical.contact_model.fsr_strength`

### D. Bundle rename

The maintained runtime physical bundle was rerooted:

- `runtime.physical.contact_model` -> `runtime.physical.contact`

This affected:

- runtime settings
- `settings_accessor.py`
- `test_run_scenario.py`
- test-only hostile-contact impedance nested path
- settings comments / reference
- README wording
- run summary wording in `test_run_entry.py`

## 4. What was intentionally kept

This round did **not** remove:

- `movement_low_level.min_unit_spacing`
- `movement_low_level.alpha_sep`
- `physical.contact.contact_hysteresis_h`
- hostile-contact impedance experiments

Reason:

- they still have active non-FSR readers on the maintained mainline

## 5. Truthful post-change read

After this round:

- active maintained movement baseline remains `v4a`
- active maintained runtime path no longer contains an FSR actuator
- `fsr_strength` is no longer part of the maintained public runtime surface
- fleet-radius style diagnostics may still be computed internally when runtime diagnostics are enabled
- the maintained contact bundle is now honestly named `contact`

## 6. Validation

Minimal checks intended for this round:

- `python -m py_compile runtime/engine_skeleton.py test_run/settings_accessor.py test_run/test_run_scenario.py test_run/test_run_execution.py test_run/test_run_entry.py`
- `git diff --check`

## 7. Cleanup significance

This round is a real subtraction-first cleanup because it:

- deletes a legacy actuator instead of hiding it behind a permanent off-switch
- removes a public parameter that no longer has an honest maintained owner
- narrows the maintained runtime surface
- reroots naming from stale `contact_model` wording to the smaller surviving contact bundle
