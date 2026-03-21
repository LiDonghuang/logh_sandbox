# Engine Skeleton Movement `v1` Retirement 20260321

Status: runtime cleanup record  
Scope: runtime / engine_skeleton only  
Classification: retired mechanism removal  

## Summary

This round retires the legacy `MOVEMENT_MODEL == "v1"` family from `runtime/engine_skeleton.py`.

The maintained runtime path now keeps only:

- `MOVEMENT_MODEL == "v3a"`

## Removed

- the legacy `v1` movement branch inside `integrate_movement(...)`
- the exact-legacy maneuver composition path kept for old regression-style behavior

## Active Surface Boundary

`test_run` maintained scenario resolution already remaps standard launcher requests onto `v3a`.

To avoid silent fallback, `runtime/engine_skeleton.py` now fails fast for any non-`v3a` movement model value.

This round does not rewrite movement semantics for the maintained path.

## Not Changed

- `diag4` family remains active diagnostic surface
- `diag4_rpg` remains unchanged in this round
- `v3a` movement path remains the maintained runtime path
