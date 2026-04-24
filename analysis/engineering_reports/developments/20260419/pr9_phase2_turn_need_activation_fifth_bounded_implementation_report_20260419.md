# PR9 Phase II Turn-Need Activation Fifth Bounded Implementation Report 20260419

Change class: bounded runtime regime activation with minimal settings-surface exposure

Scope read:

- runtime behavior change: yes
- public runtime settings surface change: yes
- module split / file extraction: no
- target-selection owner change: no
- combat execution owner change: no

## 1. Authorized Owner/Path

This fifth slice changes only the approved local desire activation regime path:

- `runtime/engine_skeleton.py`
  - `EngineTickSkeleton._compute_unit_desire_by_unit(...)`

The slice stays bounded to:

- same-tick local desire content
- heading-side turn-need weighting
- brake-only speed adaptation

It does not widen into:

- target-selection ownership changes
- `resolve_combat(...)` ownership changes
- broad locomotion-family redesign
- mode / retreat / persistent memory

## 2. Files Changed

- `runtime/engine_skeleton.py`
- `test_run/settings_accessor.py`
- `test_run/test_run_scenario.py`
- `test_run/test_run_execution.py`
- `test_run/test_run_v1_0.runtime.settings.json`
- `test_run/test_run_v1_0.settings.comments.json`
- `README.md`

## 3. What Changed

### 3.1 Runtime activation regime

Inside `EngineTickSkeleton._compute_unit_desire_by_unit(...)`:

- heading-side turn-need weighting now uses a smooth monotonic ramp instead of the previous hard late-start linear gate
- speed-side turn-need weighting is derived from the heading-side weight and remains later / weaker
- near-contact distance gating remains structurally unchanged
- speed adaptation remains brake-only

Concrete runtime read:

- `turn_need_raw = clamp01((1 - unit_facing_alignment) * 0.5)`
- `heading_turn_need = smoothstep01((turn_need_raw - turn_need_onset) / (1 - turn_need_onset))`
- `speed_turn_need = clamp01(heading_turn_need^2)`
- `local_heading_bias_weight = heading_bias_cap * near_contact_gate * front_bearing_need * heading_turn_need`
- `desired_speed_scale = max(speed_floor, 1 - speed_brake_strength * near_contact_gate * speed_turn_need)`

This keeps heading influence earlier and smoother while leaving speed influence conservative.

### 3.2 Minimal parameter exposure

The slice exposes only the minimum approved tuning set on the public runtime surface:

- `runtime.physical.local_desire.turn_need_onset`
- `runtime.physical.local_desire.heading_bias_cap`
- `runtime.physical.local_desire.speed_brake_strength`

These values are read in `test_run/test_run_scenario.py`, carried through the existing `movement_cfg` bridge, and written into the existing runtime `_movement_surface` in `test_run/test_run_execution.py`.

No new top-level runtime_cfg section was made mandatory, so existing Phase II primary baseline replay inputs remain valid.

## 4. Parameter Surface

### 4.1 `runtime.physical.local_desire.turn_need_onset`

- purpose: define when same-tick heading-side turn-need weighting begins to activate
- observable effect: lower values make heading bias begin earlier as target bearing diverges from current unit facing
- default: `0.45`
- safe range: `[0.0, 0.95]`
- classification: runtime-local, tick-local, non-persistent desire activation regime

### 4.2 `runtime.physical.local_desire.heading_bias_cap`

- purpose: cap the maximum same-tick local heading relaxation away from fleet base heading toward target bearing
- observable effect: higher values permit slightly stronger desired-heading bias in near-contact high-turn geometry
- default: `0.06`
- safe range: `[0.0, 0.15]`
- classification: runtime-local, tick-local, non-persistent desire activation regime

### 4.3 `runtime.physical.local_desire.speed_brake_strength`

- purpose: scale the brake-only speed reduction under near-contact turn pressure
- observable effect: higher values lower `desired_speed_scale` more strongly, but never above baseline and never as a sprint/lunge
- default: `0.03`
- safe range: `[0.0, 0.10]`
- classification: runtime-local, tick-local, non-persistent desire activation regime

Still internal / unexposed in this slice:

- near-contact gate ratios
- speed floor (`0.97`)

## 5. What Did Not Change

Still unchanged after this slice:

- no skeleton/unit module split
- no new owner for target selection
- no new owner for `resolve_combat(...)`
- no change to `engaged_target_id` semantics
- no `BattleState` schema expansion
- no mode implementation
- no retreat activation
- no persistent target memory
- no broad locomotion rewrite
- no Formation / FR combat-adaptation owner flow-back
- no harness-owned doctrine growth

The accepted separations remain intact:

- fleet front axis != unit facing != actual velocity
- target selection != combat execution
- local desire adaptation != Formation / FR owner flow-back

## 6. Validation

### 6.1 Static owner/path audit

Verified active owner/path:

- target identity still comes from the existing same-tick target-selection line
- local desire content still lives only inside `_compute_unit_desire_by_unit(...)`
- locomotion still only consumes the existing `unit_desire_by_unit` carrier
- combat execution still only consumes selected target and performs re-check / fire / damage / engagement writeback

### 6.2 Compile check

Command:

```powershell
python -m py_compile runtime/engine_skeleton.py runtime/runtime_v0_1.py test_run/settings_accessor.py test_run/test_run_scenario.py test_run/test_run_execution.py
```

Result:

- passed

### 6.3 Narrow smoke

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

This matches the accepted fourth-slice smoke window.

### 6.4 Paired baseline review

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
  - `observer_telemetry` excluding `tick_elapsed_ms`: exact match
  - final HP:
    - `A alive=25 hp=1779.327760`
    - `B alive=27 hp=1844.239022`
- `battle_100v100`
  - `combat_telemetry`: exact match
  - positions / orientation / velocity / HP / targets / `fleet_body_summary`: exact match
  - `observer_telemetry` excluding `tick_elapsed_ms`: exact match
  - final HP:
    - `A alive=72 hp=5534.064357`
    - `B alive=67 hp=5277.515490`
- `neutral_36`
  - full `position_frames`: exact match
  - `combat_telemetry`: exact match
  - `observer_telemetry` excluding `tick_elapsed_ms`: exact match
  - `final_tick = 447`
  - `objective_reached_tick = 427`
  - `final_objective_distance = 1.537790`
- `neutral_100`
  - full `position_frames`: exact match
  - `combat_telemetry`: exact match
  - `observer_telemetry` excluding `tick_elapsed_ms`: exact match
  - `final_tick = 448`
  - `objective_reached_tick = 428`
  - `final_objective_distance = 1.112345`

## 7. Human-Readable Evidence

The current maintained baseline set still matches exactly on behavior-bearing surfaces, so the smallest honest evidence for this slice is a controlled local turn-need comparison against the previous fourth-slice regime.

Controlled local evidence setup:

- fleet base heading = `(1.0, 0.0)`
- fleet front axis = `(1.0, 0.0)`
- same-tick target bearing = `(0.0, 1.0)`
- target distance = `0.8`
- unit current facing = `-10 degrees` from fleet heading

Observed helper output:

- previous regime (`turn_need_onset=0.65`, `heading_bias_cap=0.03`, `speed_brake_strength=0.03`)
  - `desired_heading_xy = (1.0, 0.0)`
  - `desired_speed_scale = 1.0`
- current regime (`turn_need_onset=0.45`, `heading_bias_cap=0.06`, `speed_brake_strength=0.03`)
  - `desired_heading_xy = (0.999999, 0.001034)`
  - `desired_speed_scale = 0.999920`

Interpretation:

- heading-side turn-need now begins earlier in a geometry that the fourth-slice regime still treated as zero-effect
- speed-side response remains present but materially weaker than the heading-side change
- the slice therefore opens the activation regime without widening into a broad locomotion rewrite

## 8. Drift Explanation

No new behavior-bearing drift was found in the current Phase II primary baseline set.

Battle baseline replay still carries the previously documented battle-side diagnostic-only difference in:

- `frame["runtime_debug"]`

That carried difference predates this fifth slice and does not extend into:

- positions
- orientations
- velocities
- HP
- targets
- `fleet_body_summary`
- `combat_telemetry`
- `observer_telemetry` excluding `tick_elapsed_ms`

So the fifth-slice change is currently behavior-bearing in controlled local geometry, but not yet behavior-bearing on the maintained primary baseline scenarios at the chosen defaults.

This is an inference from the paired baseline review, not proof of broader invariance outside the reviewed scenarios.

## 9. Recommendation

Current recommendation:

- the result should still be read as an activation-ready proof-of-seam, not yet as a candidate maintained regime

Reason:

- same-tick local turn-need now activates earlier and more smoothly
- the minimal tuning knobs now exist on the public settings surface
- but the maintained Phase II primary baselines still match exactly on behavior-bearing surfaces at the current defaults

So this slice opens the correct regime seam and keeps it tunable, while still stopping short of a maintained-battle behavioral re-baseline.
