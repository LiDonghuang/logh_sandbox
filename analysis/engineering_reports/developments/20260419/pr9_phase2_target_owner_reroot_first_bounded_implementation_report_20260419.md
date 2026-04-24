# PR9 Phase II Target Owner Reroot First Bounded Implementation Report 20260419

Status: implemented first bounded slice
Date: 2026-04-19
Scope: runtime active-path owner reroot for same-tick unit target selection
Modified Layer: runtime active path only

## Purpose

Record the first bounded implementation after the accepted Phase II note set and bounded implementation proposal.

This report covers only:

- same-tick unit target-owner reroot
- runtime-local carrier placement
- combat-stage responsibility shrinkage

It does not claim:

- retreat activation
- locomotion rewrite
- combat-adaptation mechanism implementation
- mode introduction
- harness ownership changes

## Changed Files

- `runtime/engine_skeleton.py`

No code changes were made in:

- `runtime/runtime_v0_1.py`
- `test_run/test_run_execution.py`
- `test_run/test_run_scenario.py`

## Active Owner Before This Slice

Before this slice:

- `runtime/engine_skeleton.py::resolve_combat(...)` still selected the per-unit target
- `UnitState.engaged_target_id` remained the engagement-state carrier
- same-tick unit target choice and combat execution were still mixed in one stage owner

## Active Owner After This Slice

After this slice:

- `runtime/engine_skeleton.py::_select_targets_same_tick(...)` is the first explicit same-tick unit target-selection owner
- `runtime/engine_skeleton.py::step(...)` now computes `selected_target_by_unit` after movement / late clamp and before combat execution
- `runtime/engine_skeleton.py::resolve_combat(...)` now consumes `selected_target_by_unit`
- `resolve_combat(...)` no longer owns primary target selection and remains responsible for:
  - validity re-check
  - in-range / in-cone confirmation
  - fire / damage resolution
  - engagement writeback

## What Changed Concretely

### 1. Same-tick minimal carrier was introduced as stage-local runtime data

Implemented carrier:

- `selected_target_by_unit: dict[str, str | None]`

Carrier placement:

- runtime-local
- stage-local
- tick-local
- inside `runtime/engine_skeleton.py`

This slice does **not** store same-tick selection in `UnitState.engaged_target_id`.

### 2. Shared spatial service landed as runtime-local helper only

Implemented helper:

- `runtime/engine_skeleton.py::_select_targets_same_tick(...)`

Current read:

- it performs bounded local visible-enemy enumeration
- it applies forward fire-cone filtering
- it chooses the nearest valid enemy
- it returns only the same-tick target mapping

Important boundary note:

- this is first-slice runtime-local placement only
- it does **not** settle the long-term owner or final permanent placement of shared spatial service

### 3. `resolve_combat(...)` was reduced to combat execution work

The target-selection block formerly local to `resolve_combat(...)` was removed from that function as the primary owner.

`resolve_combat(...)` now:

- reads `selected_target_by_unit`
- re-checks target validity against current same-tick state
- computes fire quality / range quality
- applies contact hysteresis, damage, and engagement-state writeback

## What Did Not Change

This first slice intentionally did not change:

- fleet-level `evaluate_target()` coarse-direction ownership
- `last_target_direction`
- `coarse_body_heading_current`
- `movement_command_direction`
- locomotion formula family in `integrate_movement(...)`
- retreat policy
- Formation / FR semantics
- test harness ownership

## Required Governance Notes Carried Forward

### 1. `selected_target_id` remains distinct from `engaged_target_id`

The implementation preserves the intended semantic split:

- same-tick selection input: `selected_target_by_unit`
- post-resolution engagement writeback: `engaged_target_id`

This slice does not overload `engaged_target_id` as the unit-solving carrier.

### 2. Shared spatial helper placement is transitional

The current helper placement in `runtime/engine_skeleton.py` is accepted only as the first bounded slice.

It should not be misread as proof that the final long-term shared spatial service owner is permanently a combat helper.

### 3. Current locomotion / bridge reads of engagement-state remain explicit transition only

Verified unchanged downstream reads still exist in:

- `runtime/engine_skeleton.py::_apply_v4a_transition_speed_realization(...)`
- `runtime/engine_skeleton.py::_evaluate_target_with_v4a_bridge(...)`

Current read:

- these downstream reads remain transitional acceptance
- they are not the doctrinal long-term target owner

This slice did not strengthen those couplings.

### 4. No mode was introduced

This first slice did not introduce:

- a behavior tree
- a doctrine-scale mode system
- combat-adaptation owner flow-back into Formation / FR

The slice stays limited to "select who" owner reroot only.

## Validation

### 1. Static owner/path audit

Reviewed active code path:

- `runtime/engine_skeleton.py::step(...)`
- `runtime/engine_skeleton.py::_select_targets_same_tick(...)`
- `runtime/engine_skeleton.py::resolve_combat(...)`
- unchanged transitional reads in:
  - `_apply_v4a_transition_speed_realization(...)`
  - `_evaluate_target_with_v4a_bridge(...)`

### 2. Compile check

Command:

```powershell
python -m py_compile runtime/engine_skeleton.py runtime/runtime_v0_1.py
```

Result:

- passed

### 3. Narrow smoke check

Command:

```powershell
@'
from pathlib import Path
from test_run.test_run_entry import run_active_surface

result = run_active_surface(
    base_dir=Path('test_run'),
    execution_overrides={
        'steps': 120,
        'capture_positions': False,
        'print_tick_summary': False,
        'post_elimination_extra_ticks': 0,
    },
    emit_summary=False,
)
combat = result['combat_telemetry']
final_state = result['final_state']
engaged_count = sum(1 for unit in final_state.units.values() if bool(unit.engaged))
nonzero_contact_ticks = [idx + 1 for idx, value in enumerate(combat['in_contact_count']) if int(value) > 0]
nonzero_damage_ticks = [idx + 1 for idx, value in enumerate(combat['damage_events_count']) if int(value) > 0]
print(f"final_tick={int(final_state.tick)}")
print(f"engaged_count_final={engaged_count}")
print(f"contact_ticks_head={nonzero_contact_ticks[:5]}")
print(f"damage_ticks_head={nonzero_damage_ticks[:5]}")
print(f"in_contact_tail={combat['in_contact_count'][-5:]}")
print(f"damage_tail={combat['damage_events_count'][-5:]}")
'@ | python -
```

Result:

- `final_tick=120`
- `engaged_count_final=14`
- `contact_ticks_head=[61, 62, 63, 64, 65]`
- `damage_ticks_head=[61, 62, 63, 64, 65]`
- `in_contact_tail=[12, 12, 12, 16, 14]`
- `damage_tail=[12, 12, 12, 16, 14]`

## Bottom Line

The first bounded Phase II implementation slice is now in place.

What changed:

- same-tick unit target selection moved out of `resolve_combat(...)`
- `resolve_combat(...)` was reduced to combat execution responsibility
- `engaged_target_id` was not reused as the selection carrier

What remains explicitly transitional:

- runtime-local placement of the shared spatial helper
- downstream locomotion / bridge reads of `engaged` / `engaged_target_id`

What did not open:

- mode
- retreat
- broad locomotion rewrite
- harness-owned doctrine
