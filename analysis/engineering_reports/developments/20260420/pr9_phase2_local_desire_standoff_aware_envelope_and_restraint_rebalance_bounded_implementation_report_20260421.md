## PR9 Phase II - Local Desire Standoff-Aware Envelope And Restraint Rebalance Bounded Implementation Report

Date: 2026-04-21  
Scope: experimental `local_desire` standoff-aware envelope and brake-only restraint rebalance behind the existing temporary freeze switch  
Status: implemented locally; validation complete; maintained default remains frozen

### 1. Static owner/path audit

Changed owner/path:

- `runtime/engine_skeleton.py`
  - `EngineTickSkeleton._compute_unit_desire_by_unit(...)` at line `1662`

Exact active-path read after this slice:

- heading-side still comes from the existing same-tick `local_desire` carrier
- heading-side now adds a bounded standoff-aware envelope using:
  - `battle_relation_gap_current`
- speed-side remains brake-only and now uses bounded restraint context from:
  - `battle_hold_weight_current`
  - `battle_brake_drive_current`
- the experimental branch is still gated by:
  - `local_desire_experimental_signal_read_realignment_enabled`
    at line `1677`

What did not change:

- target-selection ownership
  - `_compute_unit_intent_target_by_unit(...)` at line `3503`
  - `_select_targets_same_tick(...)` at line `3612`
- `resolve_combat(...)` ownership at line `3615`
- `local_desire` carrier shape
  - `desired_heading_xy`
  - `desired_speed_scale`
- locomotion-family ownership
  - locomotion still consumes the existing carrier at lines `3161-3225`
- second target owner / guide target semantics
- mode / retreat / persistent memory
- module split
- maintained working default
  - `runtime.physical.local_desire.experimental_signal_read_realignment_enabled = false`

### 2. Exact mechanism change

Experimental `switch = true` branch inside `_compute_unit_desire_by_unit(...)` now does:

- heading-side:
  - primary geometry read remains `fleet front -> selected target bearing`
  - local heading bias is bounded by:
    - `front_bearing_need`
    - `near_contact_gate`
    - `standoff_envelope`
  - `standoff_envelope` is derived from `battle_relation_gap_current`
    using the bounded window:
    - fully open at `relation_gap >= 0.0`
    - fully closed at `relation_gap <= -0.35`
- speed-side:
  - remains brake-only
  - keeps unit-local geometry from `unit facing -> selected target bearing`
  - now multiplies that turn-need signal by bounded restraint context from:
    - `battle_hold_weight_current`
    - `battle_brake_drive_current`
  - effective experimental speed floor:
    - `0.85`
  - effective experimental restraint strength multiplier:
    - `4.0`

Maintained `switch = false` path remains the current temporary working anchor:

- no standoff-aware local envelope
- legacy local brake floor stays `0.97`
- no stronger experimental restraint multiplier

### 3. Files changed

- `runtime/engine_skeleton.py`
- `analysis/engineering_reports/developments/20260420/pr9_phase2_local_desire_standoff_aware_envelope_and_restraint_rebalance_bounded_implementation_report_20260421.md`

### 4. Compile check

Command:

```text
python -m py_compile runtime/engine_skeleton.py
```

Result:

- pass

### 5. Narrow smoke

Smoke posture:

- maintained active scenario
- `steps = 120`
- experimental switch `true`

Result:

- `final_tick = 120`
- `first_contact_tick = 61`
- `first_damage_tick = 61`
- `in_contact_count at tick 120 = 8`
- `damage_events_count at tick 120 = 8`

Read:

- the experimental branch is live
- first-contact timing is unchanged
- battle behavior remains meaningfully different from the frozen maintained path

### 6. Paired comparison against refreshed temporary working-anchor baselines

Anchor set:

- `analysis/reference_notes/eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_battle_36v36_baseline_20260420.json`
- `analysis/reference_notes/eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_battle_100v100_baseline_20260420.json`
- `analysis/reference_notes/eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_neutral_36_baseline_20260420.json`
- `analysis/reference_notes/eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_neutral_100_baseline_20260420.json`

#### `battle_36v36`

Final state:

| case | A alive / hp | B alive / hp |
| --- | --- | --- |
| temporary working anchor | `28 / 2106.809046` | `27 / 2200.015838` |
| current experimental branch | `24 / 1351.704887` | `20 / 1100.119848` |

Read:

- battle drift is still real and behavior-bearing
- opening timing stays identical
- final battle remains materially more lethal than the temporary working anchor

Window review:

| window | anchor mean contact | current mean contact | anchor mean front gap | current mean front gap | read |
| --- | --- | --- | --- | --- | --- |
| `61-90` | `36.10` | `32.40` | `3.81` | `5.86` | early window is partially calmer |
| `130-170` | `22.07` | `10.61` | `6.65` | `6.28` | mid window contact drops, but overlap spikes still occur |
| `190-220` | `1.74` | `9.65` | `10.70` | `6.48` | late contact stays too sticky |
| `230-280` | `2.39` | `11.08` | `10.88` | `6.32` | recovery-to-line remains too weak |

Important residual negatives:

- `min front_gap` still falls below zero in:
  - `130-170`: `-1.078638`
  - `230-280`: `-0.847713`
- `min relation_gap` also falls negative in both windows:
  - `130-170`: `-0.205471`
  - `230-280`: `-0.178590`

#### `battle_100v100`

Final state:

| case | A alive / hp | B alive / hp |
| --- | --- | --- |
| temporary working anchor | `68 / 5344.369009` | `65 / 5181.952767` |
| current experimental branch | `51 / 3161.207299` | `46 / 3136.133879` |

Read:

- large-scale battle drift is also real
- opening timing stays identical
- current experimental branch remains much more lethal than the temporary working anchor

Window review:

| window | anchor mean contact | current mean contact | anchor mean front gap | current mean front gap | read |
| --- | --- | --- | --- | --- | --- |
| `58-90` | `78.03` | `64.67` | `3.64` | `6.81` | average first-contact pressure drops |
| `140-190` | `45.67` | `23.33` | `5.18` | `0.62` | contact drops, but overlap deepens too far |
| `220-260` | `21.34` | `36.63` | `6.18` | `4.13` | late contact grows too strong again |
| `280-340` | `17.87` | `33.77` | `7.97` | `4.51` | recovery remains too weak |

Important residual negatives:

- first-contact still has deeper worst-case overlap:
  - anchor `min front_gap = -1.894438`
  - current `min front_gap = -2.579384`
- recovery window still reaches severe negative front-gap excursions:
  - `280-340`: `-3.845640`

#### `neutral_36`

JSON-normalized comparison:

- `position_frames`: exact match
- `combat_telemetry`: exact match
- `observer_telemetry` excluding `tick_elapsed_ms`: exact match

Important note:

- a raw Python-object equality check on `position_frames` returns `false`
  because the in-memory run surface contains tuples while the JSON baseline
  materializes lists, and `NaN != NaN` under direct Python equality
- after JSON-normalization, the capture is identical

#### `neutral_100`

JSON-normalized comparison:

- `position_frames`: exact match
- `combat_telemetry`: exact match
- `observer_telemetry` excluding `tick_elapsed_ms`: exact match

Read for both neutral anchors:

- no behavior-bearing neutral drift was introduced by this slice
- observed drift remains battle-path specific

### 7. Coupling audit for reused battle-context scalars

#### `battle_relation_gap_current`

Existing active writes:

- bundle write at line `2541`

Existing active pre-slice use:

- `_prepare_v4a_bridge_state(...)` at lines `1369` and `1376`

New use in this slice:

- experimental local heading envelope inside `_compute_unit_desire_by_unit(...)`
  at lines `1747`, `1845-1857`

Current read of the coupling:

- the scalar is now consumed in two stages on the active battle path:
  - coarse bridge behavior
  - local heading permission
- the new use is envelope-only, not a raw drive term
- this keeps the semantic reuse narrower than a second direct advance signal

Residual risk:

- same-tick cross-stage amplification is still possible
- the same relation-gap read can now simultaneously:
  - alter coarse bridge handling
  - suppress or allow local peel-out
- current results suggest this is not exploding uncontrollably, but it is still
  a real coupling surface

#### `battle_hold_weight_current`

Existing active writes:

- bundle write at line `2564`

Existing active pre-slice use:

- `_apply_v4a_transition_speed_realization(...)` at lines `1483-1487`

New use in this slice:

- experimental local speed restraint context inside `_compute_unit_desire_by_unit(...)`
  at lines `1748-1749`, `1874-1875`

Current read of the coupling:

- the scalar now contributes to:
  - transition-speed stability shaping
  - local brake-only restraint context
- the new use is still bounded context only
- it is not used as a raw replacement for unit-local geometry

Residual risk:

- duplicated stability pressure remains possible
- however, the current validation shows the opposite practical problem:
  local speed restraint is still too easy to relax once unit-facing turn need
  falls

#### `battle_brake_drive_current`

Existing active writes:

- bundle write at line `2562`

Existing active pre-slice use:

- none found on the maintained active path before this slice

New use in this slice:

- secondary speed restraint context inside `_compute_unit_desire_by_unit(...)`
  at lines `1751-1752`, `1874-1875`

Current read of the coupling:

- duplication risk is lower than with `battle_hold_weight_current`
  because this is its first direct consumer in the live path
- semantic coupling still exists because it comes from the same battle bundle
  family and therefore is not a free signal

### 8. Targeted human-readable evidence

#### Evidence A - first-contact is partially improved, not fully solved

`battle_36v36`, window `61-90`:

- mean contact drops:
  - anchor `36.10`
  - current `32.40`
- mean front gap widens:
  - anchor `3.81`
  - current `5.86`
- low-contact ticks increase:
  - anchor `7 / 30`
  - current `11 / 30`

`battle_100v100`, window `58-90`:

- mean contact drops:
  - anchor `78.03`
  - current `64.67`
- mean front gap widens:
  - anchor `3.64`
  - current `6.81`

But the worst-case overlap is still not safely constrained:

- `battle_100v100`, `tick 70`
  - anchor:
    - `in_contact_count = 152`
    - `front_gap_A = 3.710692`
    - `relation_gap_A = 0.114933`
  - current:
    - `in_contact_count = 198`
    - `front_gap_A = -2.365992`
    - `relation_gap_A = -0.193791`

Read:

- the new envelope helps average first-contact behavior
- it does not yet prevent sharp overrun spikes

#### Evidence B - late dog-fight persistence is still too strong

`battle_36v36`, `tick 205`:

- anchor:
  - `in_contact_count = 1`
  - `target links = 1`
  - `front_gap_A = 13.508874`
- current:
  - `in_contact_count = 22`
  - `target links = 22`
  - `front_gap_A = 6.400445`

`battle_100v100`, recovery window `280-340`:

- anchor mean contact:
  - `17.87`
- current mean contact:
  - `33.77`

Read:

- late battle still stays much more engaged than the temporary working anchor
- this remains the clearest sign that dog-fight persistence is not yet solved

#### Evidence C - return-to-line tendency improves only partially

`battle_36v36`, `tick 140`:

- anchor:
  - `in_contact_count = 25`
  - `front_gap_A = 5.460188`
- current:
  - `in_contact_count = 3`
  - `front_gap_A = 10.569026`

This is a genuine improvement window.

But that improvement does not hold through the recovery band:

- `battle_36v36`, window `230-280`
  - anchor mean front gap:
    - `10.88`
  - current mean front gap:
    - `6.32`
  - anchor mean relation gap:
    - `0.3300`
  - current mean relation gap:
    - `0.0754`

Read:

- some local return-to-line behavior does appear
- it is not yet strong or stable enough to carry through the whole later fight

### 9. Explicit drift explanation

Current engineering explanation of the mixed result:

1. heading-side is now genuinely standoff-aware, so average early peel-out is
   less free than the previous frozen experimental family

2. but heading permission still stays quite open whenever relation-gap remains
   non-negative or only mildly compressed

3. speed-side restraint is stronger than before, but it still depends on
   unit-facing turn-need:
   - once a unit has already turned into its selected target, the speed brake
     relaxes even if fleet relation is already too tight

4. therefore the current controller can show this sequence:
   - bounded early peel-out improves
   - unit turns into target
   - speed brake weakens
   - local contact re-accumulates later
   - recovery-to-line stays too weak

Shortest mechanism read:

- this slice improved envelope awareness on the heading side
- it did not yet create a sufficiently durable standoff-aware restraint on the
  speed side

### 10. Current engineering judgment

Implemented correctly relative to the authorized owner/path:

- yes

Maintained default should remain frozen:

- yes

Current experimental read:

- worth keeping as an experimental result
- not acceptable yet as the maintained battle behavior for the
  `1 unit = 100 ships` model

Plain-language judgment:

- the slice found a real and useful seam
- it partially improved early local freedom control
- but it still does not suppress late overrun / dog-fight persistence strongly
  enough

Recommended immediate governance read:

- keep the maintained default with the freeze switch `OFF`
- treat this implementation as a bounded experimental result, not a promotion
- use the remaining late-contact persistence as the main next concept question
