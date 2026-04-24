# PR9 Phase II Phase B/C Bridge Runtime Fallback Fail-Fast Cleanup Record 20260419

## Scope

This record captures the bounded continuation of fallback cleanup after the
Phase A scenario-builder hardening.

Scope classification:

- harness / bridge plus frozen runtime exception
- maintained active path only
- fail-fast cleanup, not mechanism redesign

Touched files:

- `test_run/test_run_execution.py`
- `runtime/engine_skeleton.py`

The runtime file edit was performed only after explicit Human file-level
approval for the named line of work:

- `bridge/runtime fallback cleanup`

## Why This Phase Was Needed

After Phase A, the maintained scenario-builder surface no longer silently
defaulted required active settings.

But two downstream fallback families still remained:

1. bridge-side re-defaulting in `test_run/test_run_execution.py`
2. runtime-side re-defaulting in `runtime/engine_skeleton.py`

Those remaining fallback points still allowed the maintained path to silently
continue if required bridge-injected values or mandatory same-tick desire
carrier fields disappeared downstream.

That remained inconsistent with:

- root `AGENTS.md` `R-08 - No Silent Fall Back Rule`
- `test_run/AGENTS.md` `T-03 - Validation and Failure Discipline`

## Active Owner / Path Read

### Bridge owner

The maintained bridge owner is:

- `test_run/test_run_execution.py`

Specifically:

- `_ExecutionWiringSupport._build_v4a_bundle_profile(...)`
- `_ExecutionWiringSupport.prepare_runtime_context(...)`

This bridge consumes prepared `movement_cfg` / `contact_cfg` / `observer_cfg`
from the scenario builder and injects active truth into engine surfaces.

### Runtime owner

The maintained runtime owner is:

- `runtime/engine_skeleton.py`

Specifically:

- `_movement_surface`
- `_combat_surface`
- `_prepare_v4a_bridge_state(...)`
- `_compute_unit_desire_by_unit(...)`
- `integrate_movement(...)`
- `resolve_combat(...)`

## What Changed

### 1. Bridge-side movement/contact reads no longer silently default

`test_run/test_run_execution.py` now uses direct required indexing for
maintained active bridge values.

This bridge layer now fails fast instead of silently defaulting for:

- `movement_cfg["v4a_reference_surface_mode"]`
- `movement_cfg["v4a_soft_morphology_relaxation"]`
- `movement_cfg["v4a_shape_vs_advance_strength"]`
- `movement_cfg["v4a_heading_relaxation"]`
- `movement_cfg["v4a_battle_standoff_hold_band_ratio"]`
- `movement_cfg["v4a_battle_hold_weight_strength"]`
- `movement_cfg["v4a_battle_hold_relaxation"]`
- `movement_cfg["v4a_battle_approach_drive_relaxation"]`
- `movement_cfg["v4a_battle_near_contact_internal_stability_blend"]`
- `movement_cfg["v4a_battle_near_contact_speed_relaxation"]`
- `movement_cfg["engaged_speed_scale"]`
- `movement_cfg["attack_speed_lateral_scale"]`
- `movement_cfg["attack_speed_backward_scale"]`
- `movement_cfg["v4a_battle_target_front_strip_gap_bias"]`
- `movement_cfg["v4a_battle_relation_lead_ticks"]`
- `movement_cfg["v4a_restore_strength"]`
- `movement_cfg["expected_reference_spacing"]`
- `movement_cfg["reference_layout_mode"]`
- `movement_cfg["symmetric_movement_sync_enabled"]`
- `movement_cfg["local_desire_turn_need_onset"]`
- `movement_cfg["local_desire_heading_bias_cap"]`
- `movement_cfg["local_desire_speed_brake_strength"]`
- `contact_cfg["hostile_contact_impedance_mode"]`
- `observer_cfg["tick_timing_enabled"]`
- `observer_cfg["runtime_diag_enabled"]`
- `execution_cfg["post_elimination_extra_ticks"]`

For `hybrid_v2` contact mode, bridge injection now also requires:

- `contact_cfg["hybrid_v2"]["radius_multiplier"]`
- `contact_cfg["hybrid_v2"]["repulsion_max_disp_ratio"]`
- `contact_cfg["hybrid_v2"]["forward_damping_strength"]`

If hostile contact impedance mode is `off`, the bridge now sets the engine
attributes from explicit inactive-mode constants instead of silently reading
missing `hybrid_v2` config.

### 2. Runtime local-desire public-surface fallback was removed

`runtime/engine_skeleton.py` no longer treats local-desire settings as
implicitly safe defaults once execution enters the maintained runtime path.

Constructor seeds were narrowed by removing these silent working defaults from
the maintained runtime surfaces:

- `_movement_surface["local_desire_turn_need_onset"]`
- `_movement_surface["local_desire_heading_bias_cap"]`
- `_movement_surface["local_desire_speed_brake_strength"]`
- `_movement_surface["v4a_restore_strength"]`
- `_combat_surface["fire_optimal_range_ratio"]`

Runtime now uses direct required reads on maintained bridge-injected values.

Applied in:

- `_prepare_v4a_bridge_state(...)` for `movement_surface["model"]`
- `_compute_unit_desire_by_unit(...)` for:
  - `local_desire_turn_need_onset`
  - `local_desire_heading_bias_cap`
  - `local_desire_speed_brake_strength`
- `integrate_movement(...)` for:
  - `movement_surface["model"]`
  - `movement_surface["v4a_restore_strength"]`
- `resolve_combat(...)` for:
  - `combat_surface["fire_optimal_range_ratio"]`

### 3. Same-tick desire carrier fallback was removed

`integrate_movement(...)` no longer silently falls back from
`unit_desire_by_unit` to:

- `movement_direction`
- `1.0`

It now requires, per alive unit:

- `unit_desire_by_unit[unit_id]` mapping
- `desired_heading_xy`
- `desired_speed_scale`

So the accepted desire carrier is now treated as mandatory inside the
maintained v4a path.

## What Did Not Change

This cleanup did **not**:

- change target-selection ownership
- change `resolve_combat(...)` ownership
- change fifth-slice turn-need/local-desire formulas
- change same-tick target-selection logic
- change locomotion composition math beyond fail-fast behavior
- activate mode / retreat / persistent target memory
- change baseline files
- change governance files

This cleanup also intentionally did **not** harden optional reads that remain
legitimately optional, such as:

- fixture-specific `fixture_cfg.get(...)`
- diagnostic bundle reads
- debug/timeseries reads
- human-facing report helpers reading optional telemetry payloads
- optional `capture_hit_points`

Those are not the same as maintained active public-settings fallback.

## Validation

### Compile check

Command:

```powershell
python -m py_compile test_run/test_run_execution.py runtime/engine_skeleton.py test_run/test_run_scenario.py
```

Result:

- passed

### Positive maintained-path smoke

Command:

```powershell
@'
from pathlib import Path
from test_run.test_run_entry import run_active_surface

result = run_active_surface(
    base_dir=Path('test_run'),
    execution_overrides={'steps': 120},
    emit_summary=False,
)
combat = result['combat_telemetry']
final_state = result['final_state']
engaged_count_final = sum(1 for unit in final_state.units.values() if bool(unit.engaged))
print({
    'final_tick': int(final_state.tick),
    'engaged_count_final': int(engaged_count_final),
    'contact_ticks_head': [i for i, v in enumerate(combat['in_contact_count']) if v > 0][:5],
    'damage_ticks_head': [i for i, v in enumerate(combat['damage_events_count']) if v > 0][:5],
})
'@ | python -
```

Result:

- `final_tick = 120`
- `engaged_count_final = 14`
- first contact / damage ticks remained `60..64`

So the bridge/runtime fail-fast hardening did not change maintained active
behavior.

### Negative bridge-side missing-key check

Command:

```powershell
@'
from pathlib import Path
from test_run import test_run_scenario as scenario
from test_run import test_run_execution as execution

base_dir = Path('test_run')
prepared = scenario.prepare_active_scenario(base_dir)
del prepared['runtime_cfg']['movement']['local_desire_turn_need_onset']
try:
    execution.run_simulation(
        initial_state=prepared['initial_state'],
        execution_cfg=prepared['execution_cfg'],
        runtime_cfg=prepared['runtime_cfg'],
        observer_cfg=prepared['observer_cfg'],
    )
except Exception as exc:
    print(type(exc).__name__)
    print(str(exc))
'@ | python -
```

Result:

- exception type: `KeyError`
- message: `'local_desire_turn_need_onset'`

### Negative runtime carrier-hardening check

Command:

```powershell
@'
from pathlib import Path
from test_run import test_run_scenario as scenario
from test_run import test_run_execution as execution

base_dir = Path('test_run')
prepared = scenario.prepare_active_scenario(base_dir)
fixture_context = execution._resolve_fixture_execution_context(
    prepared['initial_state'],
    prepared['execution_cfg'].get('fixture', {}),
)
ctx = execution._ExecutionWiringSupport.prepare_runtime_context(
    execution_cfg=prepared['execution_cfg'],
    runtime_cfg=prepared['runtime_cfg'],
    observer_cfg=prepared['observer_cfg'],
    fixture_context=fixture_context,
)
engine = ctx['engine']
engine._compute_unit_desire_by_unit = lambda *args, **kwargs: {}
try:
    engine.integrate_movement(prepared['initial_state'])
except Exception as exc:
    print(type(exc).__name__)
    print(str(exc))
'@ | python -
```

Result:

- exception type: `KeyError`
- message: `'A1'`

This confirms `integrate_movement(...)` no longer silently falls back from a
missing maintained desire carrier.

## Conclusion

Phase B/C fallback cleanup is now complete for the maintained bridge/runtime
path under the approved scope.

The maintained active path is now narrower and more honest in three layers:

1. scenario-builder settings fail fast
2. bridge injection fails fast
3. runtime local-desire / fire-optimal-range and desire-carrier reads fail fast

Remaining optional `.get(...)` reads are now intentionally limited to fixture,
diagnostic, and other explicitly optional surfaces rather than maintained active
public-settings fallback.
