# PR9 Formation Runtime Behavior Change - State And Concerns - 2026-04-12

Status: Working review note for governance

Scope:
- runtime behavior change observed after bounded Formation owner-reroot slices
- branch-local execution slice only
- not a repair note

## What Changed

Two bounded execution slices landed on the `eng/dev-v2.1-formation-only` branch:

1. Cold-shell subtraction in `test_run/test_run_execution.py`
   - removed:
     - `band_identity_by_unit`
     - `initial_material_forward_phase_by_unit`
     - `initial_material_lateral_phase_by_unit`
   - this slice was expected to be behavior-neutral

2. Active owner-reroot in `runtime/engine_skeleton.py`
   - `movement_heading_current_xy` was removed as a Formation-bundle-carried runtime state
   - current heading is now derived runtime-side from live unit orientations
   - `transition_advance_share` was removed from Formation bundle state storage and is now exported through runtime debug / observer plumbing

## Current Observed Outcome

Human Launcher review reports a visible behavior shift:

- Formation appears less rigid and more fluid than before
- after neutral arrival at the objective, the shape appears more prone to rotating/collapsing toward the centroid
- after battle contact, the same rotational-collapse tendency also appears stronger

These observations are treated as real regression signals for governance review.

## Active Owner Truth

The active mechanism path involved in the visible change is:

- `runtime/engine_skeleton.py`
  - `_prepare_v4a_bridge_state(...)`
  - `_resolve_v4a_reference_surface(...)`
  - `integrate_movement(...)`
  - `resolve_combat(...)`
- `test_run/test_run_execution.py`
  - observer/readout path only for `transition_advance_share`

The current change should not be read as a harness-side redesign. The active owner remains runtime.

## Working Concern

The visible change appears to come from the heading-owner reroot rather than the `transition_advance_share` export reroot.

Current working concern:

- fleet-level heading memory became weaker after `movement_heading_current_xy` was removed from the Formation carrier
- heading is now derived from already-realized unit orientation state
- that creates a tighter feedback path between local unit realization and fleet-level heading
- under late neutral arrival and battle contact, this may allow local turn/contact effects to steer the fleet heading more than before

This is a concern statement, not a final causality claim.

## Important Uncertainty

The current explanatory model is still under review.

Specifically:

- Human review has already flagged that the phrase
  - "Locomotion reality begins to define fleet heading"
  may be directionally suspicious or at least incomplete
- governance review is requested before any corrective patch is attempted

Accordingly, this note records:

- observed outcome
- active owner path
- current concern surface

It does **not** claim that root cause is fully settled.

## Validation Done

Static / bounded validation completed:

- `python -m py_compile runtime/engine_skeleton.py test_run/test_run_execution.py test_run/test_run_scenario.py test_run/test_run_entry.py`
- maintained battle smoke:
  - 1 tick
  - 3 tick
- maintained neutral smoke:
  - 1 tick
  - 3 tick

Observed limits:

- no paired baseline-replacement protocol was run in this slice
- no repair is included in this note
- the note exists so governance can inspect the current branch state before further mechanism changes

## Requested Governance Read

Governance review is requested on two questions:

1. Is the current direction still the correct owner-reroot direction despite the visible rigidity loss?
2. Is the present concern model about heading ownership and collapse tendency sufficiently correct to guide the next slice, or should it be reframed before repair work starts?
