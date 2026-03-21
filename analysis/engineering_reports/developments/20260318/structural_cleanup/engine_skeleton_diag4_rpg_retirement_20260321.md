# Engine Skeleton `diag4_rpg` Retirement 20260321

Status: runtime cleanup record  
Scope: runtime / engine_skeleton + test_run_execution  
Classification: retired mechanism removal  

## Summary

This round removes the `diag4_rpg` sub-family from the maintained runtime path.

The maintained diagnostic surface keeps:

- `diag4` legacy modules `A/B/C/D`

The removed sub-family is:

- `module_rpg`
- `debug_diag4_rpg_enabled`
- `debug_diag4_rpg_window`
- associated `_debug_diag4_rpg_*` payload/state bookkeeping

## Removed

- engine-side `diag4_rpg` toggles from `EngineTickSkeleton.__init__`
- `diag4_rpg` branching and payload assembly from `_build_movement_diag4_payload(...)`
- `diag4_rpg` gating in `_build_movement_diag_pending(...)`
- `diag4_rpg` hot-path conditionals in `integrate_movement(...)`
- execution-side `engine.debug_diag4_rpg_enabled = False` vestige

## Boundary

`diag4` itself remains active maintained diagnostic surface.

This round removes only the dormant RPG add-on branch that was no longer enabled by the maintained launcher path.

## Validation Intent

The maintained launcher path should continue to expose current `diag4` behavior without any RPG-specific payload branch.
