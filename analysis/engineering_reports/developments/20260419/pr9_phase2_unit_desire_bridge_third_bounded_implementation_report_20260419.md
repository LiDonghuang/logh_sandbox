# PR9 Phase II Third Bounded Implementation Report - Unit Desire Bridge

Date: 2026-04-19
Scope: runtime-only, bounded third slice
Primary file: `runtime/engine_skeleton.py`

## 1. Owner / Path Changed

This slice changes only the locomotion input owner inside `runtime/engine_skeleton.py`.

Exact active path changed:

- `EngineTickSkeleton._compute_unit_desire_by_unit(...)`
- `EngineTickSkeleton.integrate_movement(...)`

Concrete value path changed:

- before: `integrate_movement(...)` read fleet-level `movement_direction` directly into
  `target_term_x / target_term_y`
- after: `integrate_movement(...)` reads runtime-local, tick-local
  `_debug_state["unit_desire_by_unit"]`, specifically:
  - `desired_heading_xy`
  - `desired_speed_scale`

Concrete lines in the active file at implementation time:

- `runtime/engine_skeleton.py:1659`
- `runtime/engine_skeleton.py:2677`
- `runtime/engine_skeleton.py:2928`
- `runtime/engine_skeleton.py:2937`
- `runtime/engine_skeleton.py:2992`

Implementation shape:

- `_compute_unit_desire_by_unit(...)` now builds a per-unit carrier
- carrier is runtime-local
- carrier is tick-local
- carrier is non-persistent
- current third-slice read remains intentionally narrow:
  - `desired_heading_xy` mirrors the already-accepted fleet movement command
  - `desired_speed_scale` remains `1.0`

This keeps the third slice strictly at locomotion-input ownership clarification.
It does not open combat-adaptation doctrine.

## 2. What Did Not Change

The following stayed unchanged in this slice:

- no `BattleState` schema expansion
- no `resolve_combat(...)` owner change
- no change to same-tick target-selection owner
- `engaged_target_id` remains post-resolution engagement writeback only
- no mode introduction
- no retreat activation
- no persistent target memory
- no broad locomotion redesign
- no `test_run/` ownership growth
- no `runtime/runtime_v0_1.py` change
- no `docs/governance/` change

Important doctrinal note:

- `unit_desire_by_unit` is accepted here only as a transitional runtime-local carrier
- this slice does **not** claim that target-informed combat adaptation is already settled
- the carrier currently reroots locomotion input ownership without widening the behavior family

## 3. Static Audit Summary

Static owner/path audit result:

- same-tick target selection remains owned by `_compute_unit_intent_target_by_unit(...)`
  and `_select_targets_same_tick(...)`
- combat execution remains owned by `resolve_combat(...)`
- locomotion now consumes `unit_desire_by_unit` instead of directly treating
  fleet-level `movement_direction` as the practical per-unit owner inside
  `integrate_movement(...)`

This keeps the accepted separations intact:

- fleet front axis != unit facing != actual velocity
- target selection != combat execution
- combat adaptation seam is still not activated as doctrine

## 4. Validation

### 4.1 Compile Check

Command:

```powershell
python -m py_compile runtime/engine_skeleton.py runtime/runtime_v0_1.py
```

Result:

- passed

### 4.2 Narrow Smoke

Command posture:

- `run_active_surface(...)`
- `steps = 120`
- `capture_positions = False`
- `plot_diagnostics_enabled = False`
- `print_tick_summary = False`
- `post_elimination_extra_ticks = 0`

Result:

- `final_tick = 120`
- `engaged_count_final = 14`
- `contact_ticks_head = [61, 62, 63, 64, 65]`
- `damage_ticks_head = [61, 62, 63, 64, 65]`
- `in_contact_tail = [12, 12, 12, 16, 14]`
- `damage_tail = [12, 12, 12, 16, 14]`

This matches the accepted second-slice smoke window.

### 4.3 Paired Baseline Review

Primary baseline anchor set:

- `analysis/reference_notes/eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_battle_36v36_baseline_20260419.json`
- `analysis/reference_notes/eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_battle_100v100_baseline_20260419.json`
- `analysis/reference_notes/eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_neutral_36_baseline_20260419.json`
- `analysis/reference_notes/eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_neutral_100_baseline_20260419.json`

Review order used:

1. `battle_36v36`
2. `battle_100v100`
3. `neutral_36`
4. `neutral_100`

Behavior-bearing paired review result:

- `battle_36v36`
  - `combat_telemetry`: exact match
  - positions / orientation / velocity / HP / targets / `fleet_body_summary`: exact match
  - `first_contact_tick = 61` on both sides
  - contact trace `61..65 = [6, 24, 42, 48, 72]` on both sides
  - final HP:
    - `A alive=25 hp=1779.327760`
    - `B alive=27 hp=1844.239022`
- `battle_100v100`
  - `combat_telemetry`: exact match
  - positions / orientation / velocity / HP / targets / `fleet_body_summary`: exact match
  - `first_contact_tick = 58` on both sides
  - contact trace `61..65 = [80, 106, 120, 120, 146]` on both sides
  - final HP:
    - `A alive=72 hp=5534.064357`
    - `B alive=67 hp=5277.515490`
- `neutral_36`
  - full `position_frames`: exact match
  - `combat_telemetry`: exact match
  - `final_tick = 447`
  - `objective_reached_tick = 427`
  - `final_objective_distance = 1.537790`
- `neutral_100`
  - full `position_frames`: exact match
  - `combat_telemetry`: exact match
  - `final_tick = 448`
  - `objective_reached_tick = 428`
  - `final_objective_distance = 1.112345`

## 5. Human-Readable Evidence

Minimal evidence artifact for this slice:

- `battle_36v36` and `battle_100v100` do show frame-hash mismatch against the Phase II
  primary baseline, but the mismatch is limited to `frame["runtime_debug"]`
- within that debug surface, the carried delta is limited to:
  - `focus_indicators.{A,B}.effective_fire_axis_coherence`
  - `focus_indicators.{A,B}.front_axis_delta_deg`
  - `focus_indicators.{A,B}.front_reorientation_weight`
- `targets`, fleet body summary, positions, orientations, velocities, HP, and combat telemetry
  all remain matched

Example carried battle-side debug delta at first differing tick:

- `battle_36v36`, tick `61`
  - `effective_fire_axis_coherence`: current `0.1793783589723401`, baseline `0.0`
  - `front_axis_delta_deg`: current `1.9097416027786165`, baseline `0.0024945074438388276`
  - `front_reorientation_weight`: current `0.008854893476048193`, baseline `0.0`

Observer telemetry review note:

- full `observer_telemetry` hash differs only because `tick_elapsed_ms` is timing-sensitive
- no mechanism conclusion is drawn from that timing-only difference

Interpretation:

- no new locomotion-behavior drift was found in the third-slice owner/path
- the remaining visible baseline difference is diagnostic-only and sits outside the
  locomotion-input owner moved by this slice

## 6. Conclusion

Third slice is implemented as an owner/path reroot only.

Accepted read of the result:

- locomotion now consumes an explicit per-unit desire carrier
- the carrier stays runtime-local / tick-local / non-persistent
- the carrier does not yet widen into target-informed doctrine, mode, retreat, or
  locomotion-family redesign

This keeps the slice strictly smaller than a combat-adaptation or locomotion-rewrite wave.
