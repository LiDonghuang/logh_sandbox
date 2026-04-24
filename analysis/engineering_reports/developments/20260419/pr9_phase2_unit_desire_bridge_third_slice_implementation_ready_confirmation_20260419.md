# PR9 Phase II Unit Desire Bridge Third Slice Implementation-Ready Confirmation 20260419

Status: confirmation only
Date: 2026-04-19
Scope: implementation-ready confirmation before any possible third bounded runtime slice
Authority: engineering-side confirmation only; not implementation

## Approved Document Baseline

Current approved proposal baseline:

- [pr9_phase2_unit_desire_bridge_bounded_implementation_slice_proposal_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_unit_desire_bridge_bounded_implementation_slice_proposal_20260419.md)

## Exact Owner/Path To Change

Exact owner/path to change:

- locomotion input ownership inside [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py)
- specifically the current path where fleet-level `movement_direction` still owns the unit maneuver input in `integrate_movement(...)`

Exact active path evidence:

- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1898) already computes same-tick upstream `unit_intent_target_by_unit`
- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:2612) still begins locomotion input from fleet-level `reference_direction` / `movement_direction`
- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:2869) still feeds `target_term_x` / `target_term_y` directly from `movement_direction`
- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:2916) still derives local `desired_speed_scale` only from turn alignment inside locomotion realization

Exact intended third-slice change:

- add one runtime-local, tick-local, non-persistent unified `unit_desire_by_unit` carrier in `runtime/engine_skeleton.py`
- compute it pre-movement after same-tick target intent and fleet/coarse context are already available
- make `integrate_movement(...)` consume:
  - `desired_heading_xy`
  - `desired_speed_scale`

The owner/path being changed is only:

- who supplies locomotion desire input

It is not:

- target selection ownership
- combat execution ownership
- engagement writeback ownership

## What Still Does Not Change

The future third slice would still not change:

- `BattleState` schema by default
- `resolve_combat(...)` ownership
- same-tick target selection ownership already established upstream
- `engaged_target_id` as post-resolution engagement writeback
- test harness ownership
- fleet front axis / unit facing / actual velocity separation

Still not authorized:

- mode introduction
- retreat activation
- persistent target memory
- broad locomotion redesign
- schema-heavy expansion by default
- harness-owned doctrine growth

## Why This Slice Is Still Smaller Than A Combat-Adaptation Or Locomotion-Rewrite Wave

This slice stays smaller because it only clarifies:

- one pre-movement desire carrier
- one locomotion input seam

It does not attempt to implement:

- a combat-adaptation doctrine family
- a behavior tree or heavy mode system
- retreat-policy behavior
- a redesign of the broader locomotion term family

## Minimal Human-Readable Read

Current accepted upstream target intent already exists.
Current locomotion still consumes a mixed fleet-owned input.
The third slice, if later opened, should only replace that locomotion input owner with an explicit same-tick unit desire carrier.
