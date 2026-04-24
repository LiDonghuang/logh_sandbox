# pr9_forward_fire_cone_targeting_establishment_record_20260413

## Scope

- runtime
- public `test_run` runtime settings interface
- first establishment record

## What changed

The current maintained combat target-assignment path now has an explicit forward
fire-cone gate:

- runtime owner:
  - `runtime/engine_skeleton.py::resolve_combat()`
- new public runtime setting:
  - `runtime.physical.fire_control.fire_cone_half_angle_deg`
- default established in active runtime settings:
  - `30.0`

The current maintained read is:

1. collect hostile units inside `attack_range`
2. exclude candidates outside the attacker's forward fire cone
3. choose the nearest remaining valid target
4. keep existing angle/range quality only for damage weighting after assignment

## Why this record exists

This is a major item because it changes both:

- maintained runtime target-assignment availability
- the public `test_run` runtime configuration interface

So it should be recorded independently rather than back-edited into older
analysis.

## Boundary

This record does **not** claim that fleet-level Formation direction ownership
changed here.

It applies only to unit-level combat target assignment inside the maintained
runtime combat stage.

## Files in scope

- `runtime/engine_skeleton.py`
- `test_run/settings_accessor.py`
- `test_run/test_run_scenario.py`
- `test_run/test_run_execution.py`
- `test_run/test_run_v1_0.runtime.settings.json`
- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`
