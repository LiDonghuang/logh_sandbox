# Engine Skeleton `diag4` Outlier Family Retirement 20260321

Scope: runtime/debug-reference only  
Identity: major item record under `R-11`  
Non-scope: runtime semantics, movement doctrine, combat semantics, baseline replacement

## Summary

This round retires the remaining outlier-classification sub-family that was still embedded inside runtime `diag4`.

`diag4` itself remains available as a maintained diagnostic surface, but it is now narrowed to candidate/contact readout only.

## Deleted

- `diag4` internal state caches:
  - `_debug_diag4_prev_unit_state`
  - `_debug_diag4_prev_unit_radius`
  - `_debug_diag4_transition_counts`
  - `_debug_diag4_first_outlier_tick`
  - `_debug_diag4_return_attempt_count`
  - `_debug_diag4_outlier_return_count`
  - `_debug_diag4_outlier_duration`
  - `_debug_diag4_max_outlier_duration`
  - `_debug_diag4_disp_history`
  - `_debug_diag4_persistent_records`
  - `_debug_diag4_outlier_streaks`
- retired `diag4` config knobs:
  - `diag4_return_sector_deg`
  - `diag4_neighbor_k`
- retired `diag4` payload branches:
  - `module_b`
  - `module_c`
  - `module_d`

## Retained

- `diag4` gate itself: `diag4_enabled`
- `diag4_topk`
- `diag4_contact_window`
- `module_a.topk_candidates`
- combat-side rolling contact augmentation for `module_a`

## Rationale

Earlier rounds already retired:

- movement outlier stats as maintained harness/runtime telemetry
- `diag4_rpg`

What remained here was not an active maintained mechanism, but an embedded outlier-classification/debug family still occupying runtime hot-path-adjacent code and `_debug_state`.

This round removes that leftover family instead of continuing to keep it alive behind `diag4`.

## Effect

- runtime active diagnostic surface is narrower
- `_debug_state` no longer hosts the retired outlier-classification caches
- `diag4` no longer emits state-transition / persistent-outlier / reentry payloads

## Validation

- `python -m py_compile runtime/engine_skeleton.py`
- maintained runtime validation to be run in the normal post-edit round
