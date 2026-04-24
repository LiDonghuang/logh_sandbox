# PR9 Phase II Fourth Bounded Implementation Report - Local Desire Adaptation

Date: 2026-04-19
Scope: runtime-only, bounded fourth slice
Primary file: `runtime/engine_skeleton.py`

## 1. Owner / Path Changed

This slice changes only same-tick local desire content generation inside
`runtime/engine_skeleton.py`.

Exact active path changed:

- `EngineTickSkeleton._compute_unit_desire_by_unit(...)`

Concrete owner/path read:

- target selection ownership stays at `_compute_unit_intent_target_by_unit(...)`
- combat execution ownership stays at `resolve_combat(...)`
- locomotion-family realization ownership stays inside `integrate_movement(...)`
- fourth slice changes only what content is written into the already-accepted
  per-unit desire carrier before locomotion consumes it

Concrete lines in the active file at implementation time:

- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1659)
- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1708)
- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1733)
- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1785)

## 2. What The Fourth Slice Now Does

The fourth slice uses only the approved three local signals:

1. target bearing relative to fleet front
2. target bearing relative to current unit facing
3. target range / near-contact relation

It changes only the accepted two outputs:

- `desired_heading_xy`
- `desired_speed_scale`

Current implementation read:

- `desired_heading_xy` still defaults to the raw fleet movement vector
- if a same-tick selected target exists and near-contact gating opens, a small
  bounded relax from base heading toward target bearing is applied
- `desired_speed_scale` remains brake-only
- no sprint / lunge / advance-boost family is introduced

Important boundedness notes:

- heading bias is explicitly capped and small
- target bearing never becomes an unbounded replacement of base heading
- no persistent memory is added
- no mode vocabulary is introduced

## 3. What Did Not Change

The following stayed unchanged in this slice:

- no mode implementation
- no retreat activation
- no persistent target memory
- no broad locomotion redesign
- no Formation / FR combat-adaptation owner flow-back
- no harness-owned doctrine growth
- no `BattleState` schema expansion
- no carrier shape expansion
- no new owner for `resolve_combat(...)`
- no new owner for target selection
- no `test_run/` edits
- no `runtime/runtime_v0_1.py` edits
- no `docs/governance/` edits

## 4. Static Audit Summary

Static owner/path audit result:

- `_compute_unit_desire_by_unit(...)` remains the only new content owner
- `integrate_movement(...)` still only consumes the carrier and realizes facing /
  speed / velocity under existing low-level constraints
- target selection remains separated from combat execution
- fleet front axis, unit facing, and actual velocity remain distinct surfaces

## 5. Validation

### 5.1 Compile Check

Command:

```powershell
python -m py_compile runtime/engine_skeleton.py runtime/runtime_v0_1.py
```

Result:

- passed

### 5.2 Narrow Smoke

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

This matches the accepted third-slice smoke window.

### 5.3 Paired Baseline Review

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

## 6. Human-Readable Evidence

Primary baseline behavior remained matched, so the smallest honest evidence for
this slice is a controlled local geometry read on the active helper itself.

Controlled local evidence setup:

- fleet base heading = `(1.0, 0.0)`
- current unit facing = `(0.0, -1.0)`
- same-tick selected target at near-contact distance `2.0`
- target bearing = `(0.0, 1.0)`

Observed helper output for `A1`:

- `desired_heading_xy = (0.999522, 0.030913)`
- `desired_speed_scale = 0.97`
- heading delta vs fleet base heading = `1.771470°`

Interpretation:

- the carrier is no longer placeholder-only in near-contact high-turn-need geometry
- heading bias remains small and bounded
- speed adaptation remains brake-only

## 7. Drift Explanation

No new visible behavior drift was found in the current Phase II primary baseline set.

Battle `position_frames` still differ by hash from the primary baseline, but the
carried battle-side difference remains the same diagnostic-only surface already
documented in the accepted third-slice report:

- `frame["runtime_debug"]`

No new fourth-slice drift was observed in:

- positions
- orientations
- velocities
- HP
- targets
- `fleet_body_summary`
- `combat_telemetry`

Observer telemetry hash still differs because `tick_elapsed_ms` is timing-sensitive.

## 8. Conclusion

Fourth slice is implemented as a bounded local desire-content change only.

Accepted read of the result:

- same-tick target identity remains separate
- same-tick desire carrier remains explicit and schema-light
- desire content is now capable of bounded local adaptation under approved
  near-contact / turn-need geometry
- no doctrine-scale mode system, retreat semantics, or locomotion rewrite was opened
