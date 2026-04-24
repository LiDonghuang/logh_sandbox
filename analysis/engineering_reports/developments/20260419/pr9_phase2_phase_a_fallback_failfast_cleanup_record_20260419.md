# PR9 Phase II Phase A Fallback Fail-Fast Cleanup Record 20260419

## Scope

This record captures a bounded fallback-cleanup step on the maintained
`test_run` scenario-building surface.

Scope classification:

- harness / launcher only
- active public settings interface hardening
- no runtime behavior-formula change

This is intentionally Phase A only.

It does **not** remove bridge-side fallback re-injection in
`test_run/test_run_execution.py`, and it does **not** remove runtime-side
re-defaulting in `runtime/engine_skeleton.py`.

## Why This Cleanup Was Needed

The maintained active path still contained silent settings fallback on the
scenario-builder surface. That violates:

- root `AGENTS.md` `R-08 - No Silent Fall Back Rule`
- `test_run/AGENTS.md` `T-03 - Validation and Failure Discipline for Launcher Settings`

It also created ownership-truth risk. During fifth-slice local-desire analysis,
`attack_range = 3.0` was briefly misread from fallback/helper defaults even
though the maintained active battle setting is `20.0`.

So the immediate cleanup goal was:

- remove silent maintained-path fallback at the launcher/scenario-builder entry
- prefer explicit failure for required active settings
- keep scope smaller than a bridge/runtime cleanup wave

## Active Owner Read

For this cleanup, the active owner is the maintained scenario-builder settings
read in:

- `test_run/test_run_scenario.py`

Specifically, the cleaned surface is where layered settings are converted into:

- `unit_cfg`
- `movement_cfg`
- `boundary_cfg`
- `contact_cfg`

This is the highest-value fail-fast point because it is the maintained public
entry into the active test-run path.

## What Changed

### 1. Added explicit presence enforcement

`test_run/test_run_scenario.py` now contains `_require_present(raw_value, name)`.

Behavior:

- if a required maintained-path setting is missing, it raises
  `ValueError("{path} must be provided in maintained active settings")`
- it no longer silently substitutes a local default

### 2. Required settings now fail fast on the maintained active path

The following maintained-path settings no longer silently fall back inside
`test_run/test_run_scenario.py`.

`unit`:

- `unit_speed`
- `unit_max_hit_points`
- `attack_range`
- `damage_per_tick`

`runtime.movement.v4a`:

- `restore.strength`
- `reference.surface_mode`
- `reference.soft_morphology_relaxation`
- `transition.shape_vs_advance_strength`
- `transition.heading_relaxation`
- `battle.standoff_hold_band_ratio`
- `battle.target_front_strip_gap_bias`
- `battle.hold_weight_strength`
- `battle.relation_lead_ticks`
- `battle.hold_relaxation`
- `battle.approach_drive_relaxation`
- `battle.near_contact_internal_stability_blend`
- `battle.near_contact_speed_relaxation`
- `engagement.engaged_speed_scale`
- `engagement.attack_speed_lateral_scale`
- `engagement.attack_speed_backward_scale`

`runtime.selectors` / `run_control`:

- `movement_model`
- `symmetric_movement_sync_enabled`

`runtime.physical`:

- `boundary.enabled`
- `boundary.hard_enabled`
- `boundary.soft_strength`
- `movement_low_level.min_unit_spacing`
- `movement_low_level.alpha_sep`
- `fire_control.fire_quality_alpha`
- `fire_control.fire_optimal_range_ratio`
- `fire_control.fire_cone_half_angle_deg`
- `contact.contact_hysteresis_h`
- `contact.hostile_contact_impedance.active_mode`
- `local_desire.turn_need_onset`
- `local_desire.heading_bias_cap`
- `local_desire.speed_brake_strength`

Conditional active-mode requirement:

- if `hostile_contact_impedance.active_mode == hybrid_v2`, then
  `radius_multiplier`, `repulsion_max_disp_ratio`, and
  `forward_damping_strength` must now all be present

### 3. Active comments mismatch was corrected

`test_run/test_run_v1_0.settings.comments.json` previously described
`unit.attack_range` as if the active default were `5.0`.

This no longer matched the maintained active runtime settings, which currently
set:

- `unit.attack_range = 20.0`

The comment was updated to reflect current maintained active reality and the new
fail-fast read.

## What Did Not Change

This cleanup did **not**:

- change target-selection ownership
- change `resolve_combat(...)` ownership
- change locomotion formulas
- change fifth-slice local-desire regime math
- change `BattleState` schema
- change baseline files
- change governance files

This cleanup also did **not** yet remove fallback from:

- `test_run/test_run_execution.py`
- `runtime/engine_skeleton.py`

Those remaining surfaces were already identified in:

- `analysis/engineering_reports/developments/20260419/pr9_phase2_local_desire_signal_domain_and_silent_fallback_cleanup_note_20260419.md`

and remain pending for a later, separately approved cleanup slice.

## Validation

### Compile check

Command:

```powershell
python -m py_compile test_run/test_run_scenario.py
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
combat = result["combat_telemetry"]
final_state = result["final_state"]
print({
    "final_tick": int(final_state.tick),
    "engaged_count_final": sum(1 for unit in final_state.units.values() if bool(unit.engaged)),
    "contact_ticks_head": [i for i, v in enumerate(combat["in_contact_count"]) if v > 0][:5],
    "damage_ticks_head": [i for i, v in enumerate(combat["damage_events_count"]) if v > 0][:5],
})
'@ | python -
```

Result:

- `final_tick = 120`
- `engaged_count_final = 14`
- first contact / damage ticks remained `60..64`

So the Phase A fail-fast hardening did not change maintained active behavior.

### Negative missing-setting check

Command:

```powershell
@'
from pathlib import Path
from test_run import test_run_scenario as scenario

base_dir = Path('test_run')
settings = scenario.settings_api.load_layered_test_run_settings(base_dir)
del settings["unit"]["attack_range"]
try:
    scenario.prepare_active_scenario(base_dir, settings_override=settings)
except Exception as exc:
    print(type(exc).__name__)
    print(str(exc))
'@ | python -
```

Result:

- exception type: `ValueError`
- message: `unit.attack_range must be provided in maintained active settings`

This is the intended Phase A outcome.

## Read of Remaining Work

The remaining fallback-cleanup path should still be read in phases:

1. scenario-builder fail-fast hardening
2. bridge-side default re-injection cleanup
3. runtime-side re-defaulting cleanup

This record covers only phase 1.

## Conclusion

Phase A fallback cleanup is now complete on the maintained scenario-builder
surface.

The public active launcher path is narrower and more honest:

- missing required maintained settings now fail fast
- `attack_range` comment text now matches active maintained reality
- bridge/runtime fallback removal remains a separate next step rather than being
  silently bundled into this cleanup
