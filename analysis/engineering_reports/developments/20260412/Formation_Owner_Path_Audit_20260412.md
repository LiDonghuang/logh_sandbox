# Formation Owner/Path Audit 20260412

Status: Formation-only audit note  
Scope: initial carrier-opening audit for `eng/dev-v2.1-formation-only`  
Authority: engineering working note for Human/Governance review

## Purpose

This note records the first Formation-only owner/path audit after the cleanup and structural-tightening line was merged into `dev_v2.1`.

It is not a cleanup note.
It is not a doctrine-finalization note.
It is an execution-facing map of:

- what currently acts as active Formation owner
- what currently acts as carrier/support surface
- which Formation-side responsibilities look over-coupled
- which bounded next slices appear safest

## Governance Anchor

This audit follows the PR #8 governance instruction:

- `Governance instruction - Formation direction only`

Locked direction from that instruction:

- simplify Formation rather than expand it
- treat future Formation as coarse-body ownership
- move toward real locomotion ownership below Formation
- reject heavy O(n^2)-style Formation proposals as default language

## Current Active Owner Read

### Runtime active owners

The current maintained Formation-side state evolution is primarily runtime-owned in:

- `runtime/engine_skeleton.py::_resolve_v4a_reference_surface()`
- `runtime/engine_skeleton.py::_prepare_v4a_bridge_state()`
- `runtime/engine_skeleton.py::_evaluate_target_with_v4a_bridge()`

These functions currently own or update live bundle state such as:

- `morphology_axis_current_xy`
- `morphology_center_current_xy`
- `forward_extent_current`
- `lateral_extent_current`
- `current_material_*_phase_by_unit`
- `formation_terminal_active`
- `shape_error_current`
- `transition_advance_share`
- `battle_relation_gap_*`
- `battle_hold_weight_*`
- `effective_fire_axis_*`
- `front_reorientation_weight_*`

### Harness carriers

The harness currently prepares but does not own the maintained runtime evolution of Formation-side state:

- `test_run/test_run_scenario.py`
  - movement/reference settings normalization
  - initial spawned geometry
- `test_run/test_run_execution.py`
  - battle/fixture bundle construction
  - observer-facing readout packaging

The main carrier entry is:

- `test_run/test_run_execution.py::_FixtureExecutionSupport.build_fixture_expected_reference_bundle()`

That bundle seeds runtime state, but the maintained per-tick mutation is no longer harness-owned.

## Current Structural Problem

The governance read is confirmed by the active code path:

Formation currently owns too much.

In active runtime reality, the Formation carrier is not limited to coarse-body quantities.
It also carries:

- reference-slot style expected-position semantics
- unit-level material-phase tracking
- center/wing shaping
- transition advance budgeting
- heading realization relaxation
- hold/terminal state flags
- partial movement-realization compensation through speed shaping

That means the current Formation-side line is still a mixed carrier rather than a clean coarse-body owner.

## Responsibility Breakdown

### 1. Coarse-body ownership that still makes sense

These quantities are plausible long-term Formation-side owners:

- body center
- front/primary axis
- forward extent
- lateral extent

Current active runtime names closest to that read:

- `morphology_center_current_xy`
- `morphology_axis_current_xy`
- `forward_extent_current`
- `lateral_extent_current`

### 2. Shape-definition baggage that looks too heavy

The following active surfaces make the current line more slot-first and unit-ontology-heavy than the governance direction prefers:

- `expected_slot_offsets_local`
- `target_material_forward_phase_by_unit`
- `target_material_lateral_phase_by_unit`
- `current_material_forward_phase_by_unit`
- `current_material_lateral_phase_by_unit`
- `center_wing_differential_current`

These are currently used, so they are not dead.
But they are part of the over-coupling problem.

### 3. Transition-budget ownership that should likely move out

The following active surfaces are currently part of Formation-side bridging but read more like locomotion/realization budgeting than coarse-body ownership:

- `shape_vs_advance_strength`
- `heading_relaxation`
- `transition_advance_share`
- `transition_reference_max_speed_by_unit`
- hold-time speed suppression
- near-contact internal speed stabilization layered on top of shape transition

This is the strongest code-path evidence that locomotion responsibility is currently being simulated through a high-level Formation carrier.

### 4. Terminal/hold surfaces

Current terminal/hold state is mixed:

- neutral-terminal activation is active
- hold-state shell exists
- frozen-terminal shell exists

But the active-path read is uneven:

- `formation_terminal_active` is actively written/read
- `formation_hold_active` exists but no maintained true-writer was verified in this audit
- `frozen_terminal_*` fields are initialized and read, but no maintained path was verified that flips them live

So this area contains both active semantics and probable residual shell state.

## Cold or Weakly-Justified Residues

The following surfaces did not show a maintained active-reader case strong enough to justify confidence in their continued value:

- `band_identity_by_unit`
- `initial_material_forward_phase_by_unit`
- `initial_material_lateral_phase_by_unit`
- `formation_terminal_latched_tick`
- `formation_hold_latched_tick`
- `frozen_terminal_*` shell state as currently wired

This audit does not declare them formally dead.
It does mark them as priority candidates for bounded truth-audit and subtraction.

## Recommended Next Slices

### Slice 1. Cold-shell truth audit and subtraction shortlist

First review candidates:

- `frozen_terminal_*`
- `formation_hold_*`
- `*_latched_tick`
- `band_identity_by_unit`
- `initial_material_*`

Goal:

- remove or sharply narrow shells that are no longer truly maintained

### Slice 2. Define the future coarse-body boundary explicitly

Before deeper implementation, lock a bounded target read for what Formation should continue to own:

- center
- front axis
- forward extent
- lateral extent

This should be written as a short design note, not hidden inside code edits.

### Slice 3. Separate locomotion-realization budgeting from Formation

The likely main structural follow-up is to remove transition/speed-compensation logic from the current Formation-side bridge.

Most likely extraction targets:

- `shape_vs_advance_strength`
- `heading_relaxation`
- per-unit transition-speed budgeting
- hold-speed suppression logic that exists only to compensate for unrealistic realization

## Bottom Line

The current maintained Formation-side line is no longer mainly a harness problem.
It is a runtime-owned mixed carrier.

The main problem is not that Formation is too weak.
The main problem is that Formation still owns:

- too much shape ontology
- too much transition budgeting
- too much locomotion-compensation behavior

The safest next move is not broad redesign.
It is:

1. audit and subtract residual shells
2. lock the coarse-body owner boundary
3. only then start moving realization-budget logic out of the Formation carrier
