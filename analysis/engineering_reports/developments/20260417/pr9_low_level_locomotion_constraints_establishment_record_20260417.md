# pr9_low_level_locomotion_constraints_establishment_record_20260417

## Scope

- runtime
- public `test_run` runtime settings interface
- first establishment record

## What changed

The maintained runtime movement loop now establishes an explicit low-level
locomotion realization seam below Formation.

Active runtime owner:

- `runtime/engine_skeleton.py::integrate_movement()`

New public runtime settings:

- `runtime.physical.movement_low_level.max_accel_per_tick`
- `runtime.physical.movement_low_level.max_decel_per_tick`
- `runtime.physical.movement_low_level.max_turn_deg_per_tick`
- `runtime.physical.movement_low_level.turn_speed_min_scale`

Current maintained read:

1. upstream Formation / bridge still produces desired movement composition
2. low-level locomotion rotates unit heading toward that desired direction under
   a bounded per-tick turn-rate limit
3. low-level locomotion realizes speed under bounded acceleration /
   deceleration limits
4. desired speed is additionally reduced when realized heading is badly
   misaligned with desired movement direction

## Why this record exists

This is a major item because it changes both:

- maintained runtime movement behavior availability
- the public `test_run` runtime configuration interface

So it should be recorded independently rather than back-edited into older
analysis.

## Boundary

This record does **not** claim that Formation ownership moved again in this
slice.

It applies only to low-level unit locomotion realization below the existing
Formation / bridge command surface.

It also does **not** change the unit-level fire-cone targeting rule.

## Files in scope

- `runtime/engine_skeleton.py`
- `test_run/settings_accessor.py`
- `test_run/test_run_scenario.py`
- `test_run/test_run_execution.py`
- `test_run/test_run_v1_0.runtime.settings.json`
- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`
