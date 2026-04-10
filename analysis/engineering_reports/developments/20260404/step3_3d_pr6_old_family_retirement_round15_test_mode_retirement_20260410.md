# step3_3d_pr6_old_family_retirement_round15_test_mode_retirement_20260410

## Scope

- baseline/runtime: harness-only cleanup
- test-only or harness-only: harness-only
- protocol or policy only: no

## Summary

Retired the maintained `test_mode` surface from `test_run`.

The old `test_mode` selector no longer owned maintained mode selection, movement
selection, or legacy permission gates. Its remaining active effect was only
indirect observer enablement and stale summary labeling.

This round removed that obsolete public surface and rerooted the honest
remaining behavior to `run_control.observer_enabled`.

## Files

- `test_run/test_run_scenario.py`
- `test_run/test_run_v1_0.runtime.settings.json`
- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`

## Active owner after change

- `run_control.observer_enabled`
  - maintained run-level observer/diagnostic toggle
- `run_control.symmetric_movement_sync_enabled`
  - maintained run-level execution-control seam

## Removed surface

- `run_control.test_mode`
- stale `test_mode` call-path plumbing in `prepare_active_scenario()`
- stale `test_mode` call-path plumbing in `prepare_neutral_transit_fixture()`

## Validation

- `python -m py_compile test_run/test_run_scenario.py test_run/test_run_entry.py test_run/test_run_execution.py`
- JSON load:
  - `test_run/test_run_v1_0.runtime.settings.json`
  - `test_run/test_run_v1_0.settings.comments.json`

