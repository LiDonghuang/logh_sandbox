Scope: runtime/test_run old-family retirement slice

Files:
- `runtime/engine_skeleton.py`
- `runtime/engine_driver_dummy.py`
- `test_run/test_run_execution.py`
- `test_run/test_run_telemetry.py`
- `test_run/test_run_entry.py`
- `test_run/test_run_scenario.py`
- `test_run/settings_accessor.py`
- `test_run/test_run_v1_0.runtime.settings.json`
- `test_run/test_run_v1_0.settings.comments.json`
- `README.md`

Summary:
- Removed the maintained-mainline non-`v4a` movement branch body from `runtime/engine_skeleton.py`.
- Runtime movement now explicitly fails fast if the maintained mainline tries to enter a non-`v4a` model.
- Deleted `runtime/engine_driver_dummy.py` because it no longer has any active reader in the maintained tree.
- Retired the legacy observer/debug surfaces:
  - `runtime.observer.event_bridge`
  - `runtime.observer.collapse_shadow`
  - `bridge_telemetry`
  - `collapse_shadow_telemetry`
  - `observer_telemetry["cohesion_v3" / "c_conn" / "c_scale" / "rho"]`
- Narrowed `test_run_telemetry.py` down to the still-active telemetry helpers only:
  - hostile intermix metrics
  - runtime debug payload extraction

What was intentionally not removed:
- `last_fleet_cohesion`
- `_compute_cohesion_v3_geometry(...)`
- `symmetric_movement_sync_enabled`

Reason:
- Those remain part of the current maintained state/runtime seam and were not treated as dead just because the surrounding old-family debug surfaces were removed.

Validation:
- `python -m py_compile runtime/engine_skeleton.py test_run/settings_accessor.py test_run/test_run_scenario.py test_run/test_run_execution.py test_run/test_run_entry.py test_run/test_run_telemetry.py`
- minimal headless `battle` and `neutral` 1-tick smoke through `test_run_entry.run_active_surface(...)`
