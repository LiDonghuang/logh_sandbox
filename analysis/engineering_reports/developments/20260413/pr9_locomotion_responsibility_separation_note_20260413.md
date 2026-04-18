# PR9 Locomotion Responsibility Separation Note

Status: current review note
Date: 2026-04-13
Scope: formation-only responsibility split note after heading-owner relock
Authority: engineering review note only; not canonical semantics authority

## Purpose

This note locks the current separation read between:

- coarse-body Formation ownership
- transition-carried fleet-level direction/budgeting
- lower locomotion realization burden

It does not implement real locomotion.
It does not yet simplify unit targeting.
It does not retire expected-position dependence in this slice.

Its job is to make the current mixed bridge burden explicit so later implementation slices can shrink it in the right order.

## Governance anchor

This note follows:

- `Governance instruction — integrated Formation direction lock on PR #9`
  - `https://github.com/LiDonghuang/logh_sandbox/pull/9#issuecomment-4233754282`
- `pr9_heading_owner_boundary_relock_note_20260413.md`
- `pr9_formation_coarse_body_boundary_lock_note_20260412.md`

Locked directional read:

- Formation should stay coarse-body only
- fleet heading should stay upstream as runtime-owned coarse-body state
- locomotion below Formation should become more real
- unit targeting will be simplified later, but is out of scope for this note

## Active owner baseline

The maintained active mixed carrier still lives mainly in:

- `runtime/engine_skeleton.py::_prepare_v4a_bridge_state(...)`

Supporting upstream/downstream seams still involved:

- `runtime/engine_skeleton.py::_evaluate_target_with_v4a_bridge(...)`
- `runtime/engine_skeleton.py::_resolve_v4a_reference_surface(...)`
- `runtime/engine_skeleton.py::integrate_movement(...)`

Harness role remains limited to preparation and observer packaging in:

- `test_run/test_run_execution.py`

## Separation read

### A. Coarse-body state that may remain upstream

The acceptable upstream runtime-owned coarse-body family remains:

- `morphology_center_current_xy`
- `morphology_axis_current_xy`
- `coarse_body_heading_current_xy`
- `forward_extent_current`
- `lateral_extent_current`

These remain acceptable because they describe fleet-body pose and body size rather than per-unit realization policy.

### B. Transitional fleet-level budgeting that is not coarse-body core

The following surfaces are still active, but should not be normalized as long-term coarse-body ownership:

- `shape_vs_advance_strength`
- `transition_advance_share`
- `last_target_direction` as a mixed target/motion carrier

Current read:

- these are transitional fleet-level budgeting / carrier surfaces
- they may remain temporarily active while the bridge is being narrowed
- but they are not the positive coarse-body core

### C. Lower locomotion burden currently still embedded in the bridge

The following active burden is more properly read as locomotion realization responsibility than Formation ownership:

- `transition_reference_max_speed_by_unit`
- `formation_hold_reference_max_speed_by_unit`
- `battle_near_contact_internal_stability_blend`
- `battle_near_contact_speed_relaxation`
- `engaged_speed_scale`
- `attack_speed_lateral_scale`
- `attack_speed_backward_scale`
- forward-transport brake / boost scaling

Concrete realization branches in `_prepare_v4a_bridge_state(...)` that belong to this lower burden:

- `heading_alignment -> turn_speed_scale`
- `shape_need / advance_share -> shape_speed_scale`
- `forward_transport_delta -> forward_transport_speed_scale`
- engagement-direction-based `attack_speed_scale`
- `transition_speed_target` and relaxed per-unit `max_speed` rewrite
- hold-time per-unit speed suppression through `formation_hold_reference_max_speed_by_unit`

These branches are not merely “helping Formation.”
They are performing locomotion realization compensation inside a Formation-adjacent bridge.

## Immediate interpretation rule

Later slices should judge these families differently:

- keep upstream:
  - runtime-owned coarse-body heading / axis / body extents
- treat as transitional:
  - fleet-level transition budgeting carriers
- plan to move below Formation:
  - per-unit turn/speed realization burden

Active dependence does not make a branch boundary-correct.

## Specific read on `heading_relaxation`

`heading_relaxation` should currently be read as:

- acceptable only as a bounded coarse-body heading smoothing knob
- not proof that low-level locomotion already exists
- not a reason to keep per-unit realized heading control inside Formation

So:

- fleet-level heading smoothing may remain temporarily upstream
- unit-level realized turning should later belong below that layer

## Specific read on `transition_advance_share`

Current acceptable read:

- observer/debug export ownership is acceptable
- fleet-level budgeting carrier is acceptable as transitional state

Current not-acceptable read:

- treating it as settled Formation core
- using it to justify continued growth of Formation-side speed-compensation logic

## Preferred next implementation direction

After this note, bounded implementation slices should prefer:

1. keep coarse-body heading / axis upstream
2. avoid adding new Formation-side speed patches
3. shrink per-unit `max_speed` rewriting logic as a separate locomotion line later

This note does not require doing all of that now.
It only locks the responsibility split so the next slices do not drift back into “Formation compensates for locomotion” logic.

## Boundary of this note

This note does not yet define:

- the final low-level locomotion state schema
- acceleration / deceleration / turn-rate implementation details
- the exact staging for removing expected-position dependence
- the unit-targeting simplification implementation order
