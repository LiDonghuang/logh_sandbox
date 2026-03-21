# Engine Skeleton `v1_debug` Retirement 20260321

Status: runtime cleanup record  
Scope: runtime / engine_skeleton only  
Classification: retired mechanism removal  

## Summary

This round retires the `COHESION_DECISION_SOURCE == "v1_debug"` family from the maintained runtime path.

The maintained runtime path keeps:

- canonical active cohesion `v2`
- maintained shadow path `v3_test`

The retired family is no longer kept alive inside `runtime/engine_skeleton.py`.

## Removed

- `debug_cohesion_v1_enabled`
- `_debug_prev_cohesion_v1`
- internal `debug_last_cohesion_v1` cache assembly
- `evaluate_cohesion(...)` v1 debug cohesion update path
- `integrate_movement(...)` branch that read `debug_last_cohesion_v1`

## Runtime Behavior Boundary

No maintained launcher/config path currently exposes `v1_debug` as a supported scenario label.

To avoid silent fallback, `runtime/engine_skeleton.py` now fails fast if `COHESION_DECISION_SOURCE` is manually forced to `v1_debug`.

This is a retirement of a debug/reference family, not a canonical runtime semantics rewrite.

## Notes

- `v2` remains the canonical active cohesion source.
- `v3_test` remains the maintained shadow/override path.
- `diag4`, `RPG`, and `MOVEMENT_MODEL == "v1"` were not changed in this round.
