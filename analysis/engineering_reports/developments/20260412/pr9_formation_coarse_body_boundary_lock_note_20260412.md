# PR9 Formation Coarse-Body Boundary Lock Note

Status: current review note
Date: 2026-04-12
Scope: formation-only boundary lock for `eng/dev-v2.1-formation-only` before any locomotion-separation proposal
Authority: engineering review note only; not canonical semantics authority

## Purpose

This note locks the current target read for what Formation should continue to own on `PR #9`.

It does not implement the boundary.
It does not delete active fields yet.
It does not propose the locomotion separation mechanics yet.

Its job is to make the acceptable Formation-owned coarse-body surface explicit in code terms so later edits can be judged against it.

## Active owner baseline

The maintained active Formation burden is still primarily runtime-owned in:

- `runtime/engine_skeleton.py::_resolve_v4a_reference_surface(...)`
- `runtime/engine_skeleton.py::_prepare_v4a_bridge_state(...)`
- `runtime/engine_skeleton.py::_evaluate_target_with_v4a_bridge(...)`

The harness prepares the opening carrier state in:

- `test_run/test_run_execution.py::_FixtureExecutionSupport.build_fixture_expected_reference_bundle(...)`

That harness path seeds the bundle, but the maintained per-tick owner remains runtime.

## Boundary lock

### A. Formation should continue to own only coarse-body state

The target acceptable Formation-owned surface is:

- body center
- front / primary axis
- forward extent
- lateral extent

Current runtime names closest to that boundary are:

- `morphology_center_current_xy`
- `morphology_axis_current_xy`
- `forward_extent_current`
- `lateral_extent_current`

These fields are the current coarse-body core because they describe fleet-body pose and body size without requiring strong unit-slot ontology.

### B. Formation may still temporarily carry immediate support state that directly serves that coarse-body core

The following fields are still direct support for the coarse-body read and are not the same kind of overreach as slot or speed-budget carriers:

- `forward_extent_target`
- `lateral_extent_target`
- `actual_forward_extent`
- `actual_lateral_extent`
- `shape_error_current`

Current read:

- these fields still describe body-size convergence rather than per-unit realization doctrine
- they are acceptable as transitional coarse-body support state while the boundary is being tightened

### C. The following surfaces are outside the desired long-term Formation boundary

#### 1. Slot / expected-position ontology

Fields:

- `expected_slot_offsets_local`

Reason:

- this field preserves explicit slot identity rather than coarse-body pose
- current runtime still uses it to synthesize per-unit expected positions, so it remains active
- active is not the same as boundary-correct

#### 2. Unit-level material-phase shaping

Fields:

- `target_material_forward_phase_by_unit`
- `target_material_lateral_phase_by_unit`
- `current_material_forward_phase_by_unit`
- `current_material_lateral_phase_by_unit`

Reason:

- these are unit-level morphology carriers
- they keep Formation coupled to per-unit shape realization instead of body-level ownership

#### 3. Center/wing shaping baggage

Fields:

- `center_wing_differential_current`
- `center_wing_differential_target`

Reason:

- these encode internal body-profile shaping rather than just body center / axis / extents
- they may remain temporarily active, but they are outside the locked coarse-body target

#### 4. Transition-budget and heading-realization control

Fields:

- `shape_vs_advance_strength`
- `heading_relaxation`
- `transition_advance_share`
- `transition_reference_max_speed_by_unit`

Reason:

- these govern how much movement advances versus how much shape recovery is enforced
- this is locomotion / realization budgeting, not coarse-body ownership

#### 5. Speed-compensation carriers layered on top of Formation transition

Concrete branches in `_evaluate_target_with_v4a_bridge(...)`:

- hold-time speed suppression through `formation_hold_reference_max_speed_by_unit`
- near-contact internal speed stabilization through `battle_hold_weight_current`
- forward transport brake / boost scaling applied during expected-position recovery

Reason:

- these branches modulate unit max speed in response to realization pressure
- they are strong evidence that movement compensation is currently living inside a Formation carrier
- this is outside the target Formation boundary

### D. Terminal / hold state is not part of the positive coarse-body core

Fields:

- `formation_terminal_active`
- `formation_terminal_axis_xy`
- `formation_terminal_center_xy`
- `formation_hold_*`
- `frozen_terminal_*`

Current read:

- these surfaces should not be treated as part of the positive coarse-body core
- they remain separate shell / state-family questions that must be handled explicitly
- this note does not retire or redesign them

## Decision rule for later PR #9 edits

Later Formation edits should be judged by this rule:

- keep or strengthen ownership when a field is directly about body center, body axis, forward extent, or lateral extent
- treat a field as boundary-external when it mainly encodes slot identity, per-unit morphology phase, internal profile shaping, transition budgeting, or speed compensation

Active dependence is not enough to justify long-term Formation ownership.
If a field is still active but boundary-external, it should be treated as transitional and handled in a later bounded slice rather than silently normalized as core Formation doctrine.

## Immediate consequence for next slices

This boundary lock supports the next governance step without broadening scope:

- the first bounded code deletion slice can stay limited to the already-shortlisted cold residues
- locomotion separation should later target the transition-budget and speed-compensation carriers identified above
- terminal / hold / frozen-terminal questions should remain separate from the first deletion slice

## Boundary of this note

This note locks only the desired coarse-body ownership boundary.

It does not yet define:

- the exact replacement owner for each boundary-external active field
- the implementation order for removing slot or material-phase dependence
- the future final status of `formation_hold_*` or `frozen_terminal_*`
