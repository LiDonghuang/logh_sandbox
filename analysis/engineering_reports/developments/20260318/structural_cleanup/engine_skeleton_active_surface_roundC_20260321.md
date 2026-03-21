# Engine Skeleton Active Surface Round C - 20260321

Status: runtime structural cleanup  
Scope: `runtime/engine_skeleton.py` + minimal maintained-path sync in `test_run/test_run_execution.py` and `runtime/engine_driver_dummy.py`  
Classification: Partial Cleanup

## Summary

This round continued active-surface normalization after Round B.

The goal was not to add more helpers or files.
The goal was to reduce top-level active knob sprawl in `EngineTickSkeleton`.

## What Changed

Top-level runtime/debug fields were reduced further by moving three active families behind single canonical hosts:

- combat tuning -> `_combat_surface`
- boundary tuning -> `_boundary_surface`
- FSR tuning -> `_fsr_surface`

This removed the following top-level active sprawl from base engine initialization:

- `CH_ENABLED`
- `contact_hysteresis_h`
- `fire_quality_alpha`
- `FSR_ENABLED`
- `boundary_soft_strength`
- `BOUNDARY_SOFT_ENABLED`
- `BOUNDARY_HARD_ENABLED`
- `fsr_strength`
- `fsr_lambda_delta`

## Canonical Hosts

- combat hot-path tuning: `EngineTickSkeleton._combat_surface`
- boundary hot-path tuning: `EngineTickSkeleton._boundary_surface`
- FSR hot-path tuning: `EngineTickSkeleton._fsr_surface`

## Maintained Path Sync

Minimal maintained-path sync was applied:

- `test_run/test_run_execution.py` now writes combat/boundary/FSR values into the new surface hosts
- `runtime/engine_driver_dummy.py` was updated so its local runtime exercise path still targets the maintained engine surface

## Intent

This is active-surface narrowing, not semantics rewrite.

It follows the same cleanup discipline used in `test_run`:

- delete flat selector burden
- keep one host per active family
- do not create a helper forest

## Validation

- `python -m py_compile test_run/test_run_v1_0_viz.py runtime/engine_skeleton.py test_run/test_run_execution.py runtime/engine_driver_dummy.py`
- `python test_run/test_run_anchor_regression.py`
- maintained animate smoke via `python test_run/test_run_entry.py` with `MPLBACKEND=Agg`

No runtime semantics changed in this turn.
