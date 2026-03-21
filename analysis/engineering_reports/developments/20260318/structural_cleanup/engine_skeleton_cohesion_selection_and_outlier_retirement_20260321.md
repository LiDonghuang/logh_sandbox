# Engine Skeleton Cohesion Selection And Outlier Retirement 20260321

Status: major item record  
Scope: runtime / maintained harness cleanup  
Authority: bounded cleanup turn, non-semantic structural simplification

## Summary

This turn made two explicit runtime-side cleanup changes:

1. `EngineTickSkeleton.evaluate_cohesion(...)` no longer computes both `v2` and `v3_test` in the maintained `v3_test` path.
2. movement outlier statistics were retired from the maintained runtime debug payload and maintained harness telemetry surface.

## Change 1 - Single-Path Cohesion Selection

Previous state:

- base runtime always computed `v2`
- maintained `v3_test` path then additionally computed `v3`
- harness override replaced the runtime cohesion result after the fact

Current state:

- `EngineTickSkeleton.evaluate_cohesion(...)` selects exactly one maintained runtime path based on `runtime_cohesion_decision_source`
- supported values remain:
  - `v2`
  - `v3_test`
- unsupported values now fail fast
- no per-tick dual computation remains in the maintained path

## Change 2 - Movement Outlier Stats Retirement

Previous state:

- movement outlier statistics were assembled inside runtime diagnostic payload
- maintained harness extracted them into:
  - `outlier_total`
  - `persistent_outlier_total`
  - `max_outlier_persistence`

Review result:

- these values did not participate in runtime movement/combat semantics
- they were not used by current maintained BRF or maintained VIZ plot surface
- they therefore no longer justified continued hot-path/debug-payload cost

Current state:

- `_collect_movement_outlier_stats(...)` removed from `runtime/engine_skeleton.py`
- movement outlier payload fields removed from runtime diagnostic payload
- maintained harness telemetry extraction no longer exports those fields

## Non-Changes

- `_compute_cohesion_v2_geometry(...)` retained
- `_compute_cohesion_v3_shadow_geometry(...)` retained
- `diag4` active diagnostic surface retained
- runtime movement/combat semantics not changed in this turn

## Validation Scope

- `python -m py_compile`
- `python test_run/test_run_anchor_regression.py`
- maintained animate smoke

## Classification

Partial Cleanup

Reason:

- maintained hot path became lighter
- retired diagnostic baggage was removed
- runtime file and maintained surface are cleaner
- but broader runtime burden centers still remain
