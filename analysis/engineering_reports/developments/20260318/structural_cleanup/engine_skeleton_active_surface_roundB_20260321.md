# Engine Skeleton Active Surface Round B - 20260321

Status: runtime structural cleanup  
Scope: `runtime/engine_skeleton.py` + minimal maintained-path sync in `test_run/test_run_execution.py`  
Classification: Partial Cleanup

## Summary

This round narrowed the active engine surface without changing runtime semantics.

The main change was to stop treating retired or single-option selectors as base-engine active surface:

- `MOVEMENT_MODEL` no longer participates in maintained `EngineTickSkeleton` runtime behavior
- `COHESION_DECISION_SOURCE` no longer participates in base `EngineTickSkeleton` runtime behavior

Instead:

- base runtime movement tuning now lives under `_movement_surface`
- base maintained diagnostic tuning now lives under `_diag_surface`
- test-run-specific cohesion selection remains in the maintained `test_run` layer via `runtime_cohesion_decision_source`

## What Was Removed From Base Active Surface

- top-level `MOVEMENT_MODEL`
- top-level `COHESION_DECISION_SOURCE`
- top-level movement tuning sprawl:
  - `alpha_sep`
  - `MOVEMENT_V3A_EXPERIMENT`
  - `CENTROID_PROBE_SCALE`
  - `ODW_POSTURE_BIAS_*`
- top-level diagnostic tuning sprawl:
  - `debug_fsr_diag_enabled`
  - `debug_outlier_eta`
  - `debug_outlier_persistence_ticks`
  - `debug_diag4_*`
  - `debug_cohesion_v3_shadow_enabled`

## New Canonical Hosts

- movement hot-path tuning: `EngineTickSkeleton._movement_surface`
- maintained diagnostic tuning: `EngineTickSkeleton._diag_surface`
- test-run-only cohesion selector: `TestModeEngineTickSkeleton.runtime_cohesion_decision_source`

## Intent

This is not a semantics rewrite.

It is a surface-normalization step aligned with the test-run reset pattern:

- keep one maintained source of truth
- delete retired selector surface instead of keeping compatibility knobs alive
- reduce flat parameter burden in the maintained hot path

## Validation

- `python -m py_compile runtime/engine_skeleton.py test_run/test_run_execution.py`
- `python test_run/test_run_anchor_regression.py`
- maintained animate smoke via `python test_run/test_run_entry.py` with `MPLBACKEND=Agg`

No runtime semantics changed in this turn.
