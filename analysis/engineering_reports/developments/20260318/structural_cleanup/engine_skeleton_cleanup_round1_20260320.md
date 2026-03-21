# Engine Skeleton Cleanup Round 1

Date: 2026-03-20  
Scope: bounded structural cleanup of `runtime/engine_skeleton.py`  
Primary target: `EngineTickSkeleton.integrate_movement(...)`

## What Changed

This round did not alter movement/combat formulas. It reduced the maintained reading burden of `integrate_movement(...)` by extracting diagnostic assembly and bookkeeping out of the hot execution path into same-file private helpers.

Added same-file helpers:

- `_dist_summary(...)`
- `_ensure_debug_dict(...)`
- `_collect_movement_outlier_stats(...)`
- `_build_movement_diag4_payload(...)`
- `_build_movement_diag_pending(...)`

## Direct Subtraction

`integrate_movement(...)` was reduced from `1731` lines at `HEAD` to `772` lines after this round.

The moved burden was primarily:

- projection-displacement diagnostic aggregation
- per-fleet outlier persistence bookkeeping
- diag4 legacy payload assembly
- RPG diagnostic payload assembly
- pending diagnostic package assembly

## What Was Not Changed

- movement vector construction
- pursuit / cohesion / ODW movement semantics
- FSR execution order
- collision projection order
- boundary clamp behavior
- combat logic

## Honest Classification

This is best classified as `Partial Cleanup`.

Reason:

- the maintained hot path is materially lighter
- `integrate_movement(...)` is visibly shorter and easier to review
- but total file size did not decrease; diagnostic weight was concentrated into private helper hosts inside the same file

## Remaining Burden Centers

Remaining high-burden areas after Round 1:

- `_build_movement_diag4_payload(...)` diagnostic payload host
- `resolve_combat(...)`
- repeated numeric-rank / projection-local utilities still in method scope

