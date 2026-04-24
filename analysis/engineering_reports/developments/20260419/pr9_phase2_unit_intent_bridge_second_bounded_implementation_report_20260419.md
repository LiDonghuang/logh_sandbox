# PR9 Phase II Unit Intent Bridge Second Bounded Implementation Report 20260419

Status: implemented
Date: 2026-04-19
Scope: second bounded Phase II implementation slice
Primary runtime file: `runtime/engine_skeleton.py`
Change class: runtime behavior owner/path cleanup with paired baseline review

## Purpose

This report records the second bounded Phase II slice that follows:

- the first target-owner reroot implementation
- the new Phase II primary baseline freeze
- the accepted second-slice proposal for a pre-movement unit-intent bridge

The purpose of this slice was narrow:

- stop using post-resolution `engaged` / `engaged_target_id` as the practical upstream owner in the v4a bridge path
- introduce a runtime-local same-tick unit-intent carrier for bridge and transition-speed shaping
- keep combat execution downstream as re-check / fire / damage / engagement writeback

## Governance-Carried Boundaries

This slice kept the already accepted boundaries:

- no `BattleState` schema expansion
- no persistent target memory
- no mode
- no retreat activation
- no `test_run/` ownership expansion
- no broad locomotion rewrite
- no Formation / FR combat-adaptation owner flow-back

Still explicitly true after this slice:

- `engaged_target_id` remains post-resolution engagement writeback
- shared spatial helper placement remains runtime-local and transitional

## Assumptions

1. The first target-owner reroot slice is the accepted starting state.
2. The smallest honest second slice remains local to `runtime/engine_skeleton.py`.
3. The same minimal selector contract may be reused at two sub-stage snapshots:
   - pre-movement for unit-intent bridge reads
   - post-movement for combat execution re-check
4. Reusing that contract does not by itself settle long-term shared spatial service ownership.

## Actual Code Changes

### 1. Added a runtime-local unit-intent carrier host

Inside `EngineTickSkeleton._debug_state`, this slice added:

- `unit_intent_target_by_unit`

This carrier is:

- runtime-local
- tick-local
- non-persistent
- not part of `BattleState`

`step(...)` now clears it at the start of each tick.

### 2. Added an explicit same-tick unit-intent selector helper

New helper:

- `_compute_unit_intent_target_by_unit(state)`

Contract:

- same minimal nearest-valid-enemy selector
- bounded by current snapshot
- still uses runtime fire-cone and in-range checks
- reused both for pre-movement bridge intent and post-movement combat target consumption

`_select_targets_same_tick(...)` now delegates to that helper instead of owning separate logic.

### 3. Rerooted `_evaluate_target_with_v4a_bridge(...)` away from `engaged*`

Before this slice, the bridge path built `engaged_attack_vectors` from:

- `unit.engaged`
- `unit.engaged_target_id`

After this slice, it builds that fire-axis read from:

- `unit_intent_target_by_unit`

So the bridge now reads same-tick pre-movement unit intent rather than last combat writeback.

### 4. Rerooted `_apply_v4a_transition_speed_realization(...)` away from `engaged*`

Before this slice, attack-facing speed shaping was gated by:

- `unit.engaged`
- `unit.engaged_target_id`

After this slice, the function takes:

- `unit_intent_target_by_unit`

and derives attack-direction speed shaping from the same-tick target chosen for the current unit-intent read.

### 5. Combat execution remained downstream

`resolve_combat(...)` still owns:

- validity re-check
- in-range / in-cone confirmation
- fire quality / damage
- engagement writeback

This slice did not merge bridge intent and combat writeback back together.

## Owner/Path Result

After this slice, the active path is:

1. `step(...)` resets runtime-local unit intent carrier
2. `evaluate_target(...)`
3. `_evaluate_target_with_v4a_bridge(...)` computes same-tick unit intent and stores `unit_intent_target_by_unit`
4. `integrate_movement(...)`
5. `_prepare_v4a_bridge_state(...)`
6. `_apply_v4a_transition_speed_realization(...)` consumes `unit_intent_target_by_unit`
7. post-movement `_select_targets_same_tick(...)` reuses the same selector contract on the moved snapshot
8. `resolve_combat(...)` consumes that moved-snapshot selection and performs combat execution

So the second slice changed upstream practical ownership without changing downstream combat-stage responsibility.

## Validation

### 1. Static owner/path audit

Reviewed active code path:

- `runtime/engine_skeleton.py::step(...)`
- `runtime/engine_skeleton.py::_evaluate_target_with_v4a_bridge(...)`
- `runtime/engine_skeleton.py::_prepare_v4a_bridge_state(...)`
- `runtime/engine_skeleton.py::_apply_v4a_transition_speed_realization(...)`
- `runtime/engine_skeleton.py::_compute_unit_intent_target_by_unit(...)`
- `runtime/engine_skeleton.py::_select_targets_same_tick(...)`
- `runtime/engine_skeleton.py::resolve_combat(...)`

Audit conclusion:

- upstream bridge and transition-speed shaping no longer depend on `engaged*`
- `engaged_target_id` remains downstream engagement writeback only

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
        'plot_diagnostics_enabled': False,
        'print_tick_summary': False,
        'post_elimination_extra_ticks': 0,
    },
    emit_summary=False,
)
combat = result['combat_telemetry']
contact_ticks = [i + 1 for i, value in enumerate(combat['in_contact_count']) if int(value) > 0]
damage_ticks = [i + 1 for i, value in enumerate(combat['damage_events_count']) if int(value) > 0]
print({
    'final_tick': int(result['final_state'].tick),
    'engaged_count_final': sum(1 for unit in result['final_state'].units.values() if bool(unit.engaged)),
    'contact_ticks_head': contact_ticks[:5],
    'damage_ticks_head': damage_ticks[:5],
    'in_contact_tail': combat['in_contact_count'][-5:],
    'damage_tail': combat['damage_events_count'][-5:],
})
'@ | python -
```

Result:

- `final_tick=120`
- `engaged_count_final=14`
- `contact_ticks_head=[61, 62, 63, 64, 65]`
- `damage_ticks_head=[61, 62, 63, 64, 65]`
- `in_contact_tail=[12, 12, 12, 16, 14]`
- `damage_tail=[12, 12, 12, 16, 14]`

### 4. Paired baseline review

Per `docs/governance/Baseline_Replacement_Protocol_v1.0.md`, this slice was reviewed against the current Phase II primary baselines by replaying the saved baseline inputs:

- `initial_state`
- `execution_cfg`
- `runtime_cfg`
- `observer_cfg`

Review order:

1. `battle_36v36`
2. `battle_100v100`
3. `neutral_36`
4. `neutral_100`

Compared metrics:

- frame count
- final tick
- first contact tick
- first damage tick
- peak contact / damage counts
- final alive counts / total HP by fleet
- neutral objective timing / distance metrics
- short human-readable trace windows

Result:

- all four paired comparisons matched exactly
- no metric drift was observed in the reviewed windows

Human-readable evidence:

- `battle_36v36` contact trace ticks `61-65`
  - baseline: `[6, 24, 42, 48, 72]`
  - current: `[6, 24, 42, 48, 72]`
- `neutral_36` distance tail
  - baseline: `[2.510964, 2.344499, 2.110347, 1.838309, 1.53779]`
  - current: `[2.510964, 2.344499, 2.110347, 1.838309, 1.53779]`

## Interpretation

This slice changed upstream owner/path semantics but did not change observed behavior on the current maintained Phase II primary baseline set.

The most reasonable read is:

- the new unit-intent bridge now matches the accepted branch behavior for the maintained battle and neutral scenarios
- the code path is cleaner because bridge and transition-speed shaping no longer depend on post-resolution engagement writeback
- further Phase II work can build on this seam without carrying the old `engaged*` upstream coupling

This is an inference from the paired baseline review, not proof of broader invariance outside the reviewed scenarios.

## Bottom Line

The second bounded Phase II slice is now in place.

What changed:

- runtime-local same-tick unit intent now exists as an explicit upstream carrier
- bridge fire-axis shaping now reads that carrier
- transition-speed attack shaping now reads that carrier
- combat execution remains downstream and still owns engagement writeback

What did not open:

- mode
- retreat
- persistent memory
- locomotion rewrite
- harness-owned doctrine

What is still transitional:

- runtime-local helper placement as the temporary shared spatial-service seam
