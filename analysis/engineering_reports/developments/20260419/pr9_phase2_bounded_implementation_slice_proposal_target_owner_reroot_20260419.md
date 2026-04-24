# PR9 Phase II Bounded Implementation Slice Proposal Target Owner Reroot 20260419

Status: proposal only
Date: 2026-04-19
Scope: first bounded implementation proposal for PR #9 Phase II target-owner reroot
Authority: engineering proposal for Human + governance review before any code implementation

## Purpose

This proposal defines the first bounded implementation slice after the accepted Phase II note set.

It does not implement the reroot.
It does not open retreat policy.
It does not open broad locomotion rewrite.
It does not open a combat-adaptation mechanism family.

Its job is to lock the smallest acceptable first code slice:

- move same-tick per-unit target selection out of `resolve_combat()`
- keep target ownership separate from `engaged_target_id`
- preserve all current Phase II governance guardrails

## Governance And Note Anchors

This proposal follows:

- [docs/governance/PR9_Phase2_Unit_Solving_Layer_Governance_Direction_20260419.md](E:/logh_sandbox/docs/governance/PR9_Phase2_Unit_Solving_Layer_Governance_Direction_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_unit_structure_contract_note_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_unit_structure_contract_note_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_simplified_unit_targeting_note_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_simplified_unit_targeting_note_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_locomotion_followup_note_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_locomotion_followup_note_20260419.md)

Most important governance read carried into this proposal:

- first implementation should touch one essential owner/path only
- target owner moves to the unit solving layer
- same-tick minimal `selected_target_id` seam is allowed
- `resolve_combat()` should become re-check / fire / damage / engagement writeback
- no heavy persistent target memory
- no retreat activation in this opening wave

## Assumptions

1. The first code slice should remain runtime-local and should not require `test_run` changes.
2. The safest first carrier is stage-local / tick-local rather than a new persistent schema field.
3. The first slice should avoid overloading `UnitState.engaged_target_id` with same-tick target-selection meaning.
4. Existing locomotion and bridge reads of `engaged` / `engaged_target_id` may remain temporarily, but only as explicit transitional acceptance.
5. `evaluate_target()` remains fleet-level coarse direction work in this slice and is not expanded into unit doctrine.

## Verified Active Owner Baseline

### 1. Current step order

Current active order in `runtime/engine_skeleton.py::step(...)` is:

- `evaluate_cohesion()`
- `evaluate_target()`
- `evaluate_utility()`
- `integrate_movement()` or symmetric movement merge
- contact impedance / fixture clamp
- `resolve_combat()`

So the first clean reroot insertion point is immediately before `resolve_combat()`.

### 2. Current per-unit target owner

Current active per-unit target owner is still `runtime/engine_skeleton.py::resolve_combat(...)`.

Current local variables there include:

- `assigned_target`
- `best_enemy_id`
- `best_dist_sq`
- `best_dx`
- `best_dy`
- angle/range quality values used to support later fire resolution

That local target-selection block is the main owner/path to reroot.

### 3. Current engagement-state carrier

Current active unit field is:

- `runtime/runtime_v0_1.py::UnitState.engaged_target_id`

Verified current read:

- it is written during combat resolution / engagement writeback
- it is read later by locomotion shaping and v4a bridge logic

Therefore `engaged_target_id` is a current engagement-state carrier, not an honest same-tick unit-solving selection carrier.

### 4. Current transitional downstream reads that should remain explicit

Current direct reads of `engaged` / `engaged_target_id` include:

- `runtime/engine_skeleton.py::_apply_v4a_transition_speed_realization(...)`
- `runtime/engine_skeleton.py::_evaluate_target_with_v4a_bridge(...)`

These are not the first owner/path being rerooted here.
If left unchanged in the first slice, they must remain explicitly transitional rather than silently normalized as final doctrine.

## Proposed First Slice

### A. Slice goal

The first bounded implementation slice should do exactly this:

1. introduce a same-tick minimal per-unit target-selection seam before combat execution
2. make `resolve_combat()` consume that seam instead of selecting targets itself
3. keep `resolve_combat()` responsible for re-check / fire / damage / engagement writeback only

### B. Preferred carrier shape

Preferred first-slice carrier:

- stage-local
- tick-local
- minimal

Recommended read:

- `selected_target_by_unit: dict[str, str | None]`

This is preferred over:

- reusing `engaged_target_id`
- adding heavy persistent target memory
- adding a new long-lived mode/state machine surface

### C. Preferred placement

The smallest honest placement is:

- create the target-selection mapping inside `runtime/engine_skeleton.py`
- pass it from `step(...)` into `resolve_combat(...)`

This keeps the first slice inside one active runtime file and avoids premature schema expansion in `BattleState` or `UnitState`.

## Exact Target Files And Seams

Primary future implementation file:

- `runtime/engine_skeleton.py`

Primary future implementation seams:

- `step(...)`
- a new unit target-selection helper local to runtime stage ownership
- `resolve_combat(...)`

Not preferred for the first slice:

- `runtime/runtime_v0_1.py`
- `test_run/test_run_execution.py`
- `test_run/test_run_scenario.py`

### Concrete path change proposal

#### 1. `step(...)`

Proposed change:

- after movement and late clamp, compute same-tick selected targets on the moved state
- pass the resulting stage-local mapping into `resolve_combat(...)`

Target read:

- `resolve_combat(moved_state, selected_target_by_unit)`

#### 2. New target-selection helper

Proposed helper responsibility:

- bounded local visible enemy enumeration
- forward fire-cone filtering
- nearest valid enemy choice
- write no HP
- write no engagement state
- return only the minimal selected target id mapping

This helper is the first explicit unit-target owner.

#### 3. `resolve_combat(...)`

Proposed change:

- remove ownership of primary target selection
- keep validity re-check against same-tick selected target
- keep in-range / in-cone confirmation
- keep fire permission
- keep damage / HP resolution
- keep `engaged` / `engaged_target_id` writeback

This means current local selection-owner logic should leave `resolve_combat(...)`, while combat execution logic should remain there.

## What Must Not Change In The First Slice

The first slice should not change:

- fleet-level `evaluate_target()` coarse-direction ownership
- `last_target_direction`
- `coarse_body_heading_current`
- `movement_command_direction`
- locomotion formula family in `integrate_movement(...)`
- retreat-policy behavior
- Formation / FR semantics
- `test_run` ownership boundary

## Explicit Guardrails From Governance Notes

### 1. `selected_target_id` must not collapse into `engaged_target_id`

The first slice must preserve the semantic distinction:

- `selected_target_id` means same-tick unit-solving selection input to combat execution
- `engaged_target_id` remains post-resolution engagement-state writeback

Carrier convenience is not an excuse to collapse those two meanings.

### 2. Combat adaptation seam stays guarded

This slice must not introduce:

- a heavy behavior tree
- a doctrine-scale mode system
- owner flow-back into Formation or FR

If any mode language appears at all, it must remain solving-assist semantics only.
The cleaner first slice is to avoid adding mode behavior entirely.

### 3. Locomotion coupling is accepted only as transitional

If `_apply_v4a_transition_speed_realization(...)` and `_evaluate_target_with_v4a_bridge(...)` continue reading `engaged` / `engaged_target_id` after the first slice, that must be read as explicit transition, not final doctrine.

The first slice does not need to remove those reads yet.
But it must not strengthen them or silently treat them as the true target owner.

## Recommended Rejection Rules

The first implementation should be rejected if it does any of the following:

1. stores same-tick selection by reusing `engaged_target_id`
2. leaves target choice inside `resolve_combat()` and only renames local variables
3. introduces persistent target memory or lock-on behavior
4. widens into locomotion rewrite or combat adaptation implementation
5. pushes combat-time de-formation meaning back into Formation / FR
6. expands into harness-owned doctrine

## Validation Posture For The Future Implementation Turn

If this proposal is approved for code work, the first implementation turn should validate minimally:

- static owner/path audit after edit
- `python -m py_compile runtime/engine_skeleton.py runtime/runtime_v0_1.py`
- one narrow smoke check only if needed after the owner reroot compiles

This first slice does not need broad DOE or broad baseline-comparison work.

## Bottom Line

The narrowest honest first Phase II code slice is:

- one runtime-file owner reroot in `runtime/engine_skeleton.py`
- stage-local / same-tick `selected_target_by_unit` carrier
- `resolve_combat()` reduced to combat execution responsibilities
- no schema-heavy state addition
- no locomotion rewrite
- no retreat activation
- no Formation owner regression
