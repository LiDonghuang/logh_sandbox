## PR9 Phase II - Unit Local Maneuver Envelope / Precontact No-Crossing And Standoff-Violation Response Bounded Implementation Report

Date: 2026-04-21  
Scope: bounded experimental maneuver-envelope implementation behind the existing explicit `local_desire` experimental switch  
Status: implemented locally; validation complete; still experimental

### 1. Static owner/path audit

Changed owner/path:

- `runtime/engine_skeleton.py`
  - `EngineTickSkeleton._compute_unit_desire_by_unit(...)` at line `1662`

Exact active-path read after this slice:

- same-tick target source stays:
  - `_compute_unit_intent_target_by_unit(...)` at line `3655`
- `local_desire` carrier shape stays:
  - `desired_heading_xy`
  - `desired_speed_scale`
- locomotion still consumes that carrier at:
  - `integrate_movement(...)` lines `3313-3378`
- combat execution still stays in:
  - `resolve_combat(...)` at line `3767`

Exact final maneuver-envelope additions kept in the active code:

- delayed contact-maturity gating at lines `1719-1720`
  - `LOCAL_DESIRE_CONTACT_MATURITY_GATE_START = 0.96`
  - `LOCAL_DESIRE_CONTACT_MATURITY_GATE_FULL = 0.999`
- precontact permission blending at lines `1958-1964`
  - `precontact_nocrossing_permission`
- heading-side bounded bias at lines `1969-1974`
  - still vector-only, still carrier-local
- speed-side bounded restorative response at lines `1984-2013`
  - including `standoff_violation_response`
- bounded restore-to-line relaxation at lines `2041-2055`
  - `restore_line_weight`

### 2. Plain-language battle read

What this slice tries to do:

- before contact is mature enough, a Unit should not peel out early enough to
  break fleet-level hold
- if standoff is already being violated, Unit-local response should become
  restorative rather than simply continuing target-chase freedom

What this slice is **not** trying to do:

- free-flying dog-fight behavior
- retreat behavior
- mode behavior
- second target ownership
- locomotion-family redesign

### 3. Exact mechanism change kept in final code

Final kept implementation in `_compute_unit_desire_by_unit(...)`:

- heading-side remains real
  - still uses `fleet front -> selected target bearing`
  - but is now multiplied by:
    - `heading_proximity_context`
    - `standoff_envelope`
    - `precontact_nocrossing_permission`
- speed-side remains brake-only
  - still uses `unit facing -> selected target bearing`
  - but now also includes:
    - `precontact_nocrossing_response`
    - `standoff_violation_response`
- restore-line tendency remains bounded
  - only relaxes heading back toward `fleet_front_hat`
  - does not introduce any named mode or retreat state

Important post-validation correction that is part of the final kept code:

- the first implementation used a much earlier contact-maturity window
- validation showed `engagement_geometry_active_current` is already very high at
  first contact on the maintained battle path
- therefore the kept final code delays "contact mature enough" to:
  - `0.96 -> 0.999`
- reason:
  - otherwise the precontact no-crossing branch turns off almost immediately and
    does not actually dominate first contact

### 4. What did not change

Still unchanged in this slice:

- single same-tick target source
  - `selected_target_by_unit`
- target-selection ownership
- `resolve_combat(...)` ownership
- `local_desire` carrier shape
- second target / guide target semantics
- mode
- retreat
- persistent target memory
- broad locomotion rewrite
- module split
- combat-coupling redesign

### 5. Compile check

Command:

```text
python -m py_compile runtime/engine_skeleton.py
```

Result:

- pass

### 6. Narrow smoke

Smoke posture:

- maintained active scenario
- `steps = 120`
- explicit experimental enablement
  - `runtime.physical.local_desire.experimental_signal_read_realignment_enabled = true`
- `capture_positions = false`
- `plot_diagnostics_enabled = false`
- `print_tick_summary = false`
- `post_elimination_extra_ticks = 0`

Result:

- `final_tick = 120`
- `first_contact_tick = 61`
- `first_damage_tick = 61`
- `in_contact_final = 8`
- `damage_events_final = 8`

Read:

- the experimental maneuver-envelope branch is live
- opening timing is unchanged
- the new logic affects battle continuation, not opening tick order

### 7. Paired comparison against current temporary working anchor

Anchor set:

- `analysis/reference_notes/eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_battle_36v36_baseline_20260420.json`
- `analysis/reference_notes/eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_battle_100v100_baseline_20260420.json`
- `analysis/reference_notes/eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_neutral_36_baseline_20260420.json`
- `analysis/reference_notes/eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_neutral_100_baseline_20260420.json`

Validation posture:

- explicit experimental enablement through the existing `testonly` surface
- `capture_positions = true`
- `capture_hit_points = true`
- `include_target_lines = true`

#### `battle_36v36`

Final state:

| case | A alive / hp | B alive / hp |
| --- | --- | --- |
| temporary working anchor | `28 / 2106.809046` | `27 / 2200.015838` |
| current experimental branch | `24 / 1287.975621` | `19 / 1152.466804` |

Window review:

| window | anchor mean contact | current mean contact | anchor mean front gap | current mean front gap | read |
| --- | --- | --- | --- | --- | --- |
| `61-90` | `36.10` | `32.30` | `3.81` | `5.81` | average first contact is calmer |
| `120-160` | `22.37` | `16.05` | `7.85` | `4.90` | mid-window contact drops, but relation compression is still present |
| `190-220` | `1.74` | `10.16` | `10.70` | `6.68` | late sticky contact still remains far above anchor |
| `230-280` | `2.39` | `12.08` | `10.88` | `6.75` | recovery-to-line is still too weak |

Important sample ticks:

- `tick 70`
  - anchor:
    - `in_contact_count = 72`
    - `front_gap_A = 4.579634`
    - `relation_gap_A = 0.162748`
  - current:
    - `in_contact_count = 72`
    - `front_gap_A = -0.383340`
    - `relation_gap_A = 0.041441`
- `tick 140`
  - anchor:
    - `in_contact_count = 25`
    - `front_gap_A = 5.460188`
  - current:
    - `in_contact_count = 5`
    - `front_gap_A = 5.835333`
- `tick 205`
  - anchor:
    - `in_contact_count = 1`
    - `front_gap_A = 13.508874`
  - current:
    - `in_contact_count = 11`
    - `front_gap_A = 9.961359`

Read:

- first-contact average behavior improves
- one strong mid-window return-to-line pocket appears
- late sticky contact is still materially above the anchor

#### `battle_100v100`

Final state:

| case | A alive / hp | B alive / hp |
| --- | --- | --- |
| temporary working anchor | `68 / 5344.369009` | `65 / 5181.952767` |
| current experimental branch | `58 / 3923.596037` | `51 / 3590.873193` |

Window review:

| window | anchor mean contact | current mean contact | anchor mean front gap | current mean front gap | read |
| --- | --- | --- | --- | --- | --- |
| `58-90` | `78.03` | `64.61` | `3.64` | `6.62` | average first contact is calmer |
| `120-170` | `32.94` | `36.80` | `3.30` | `0.75` | this window still degrades badly |
| `220-260` | `21.34` | `23.00` | `6.18` | `5.88` | later restraint is mixed, not clearly better |
| `280-340` | `17.87` | `26.38` | `7.97` | `4.46` | late sticky contact still remains too high |

Important sample ticks:

- `tick 70`
  - anchor:
    - `in_contact_count = 152`
    - `front_gap_A = 3.710692`
    - `relation_gap_A = 0.114933`
  - current:
    - `in_contact_count = 198`
    - `front_gap_A = -2.125917`
    - `relation_gap_A = -0.192290`
- `tick 120`
  - anchor:
    - `in_contact_count = 43`
    - `front_gap_A = -1.295192`
  - current:
    - `in_contact_count = 9`
    - `front_gap_A = 7.028706`
- `tick 150`
  - anchor:
    - `in_contact_count = 38`
    - `front_gap_A = 2.616520`
  - current:
    - `in_contact_count = 48`
    - `front_gap_A = 0.052012`
- `tick 340`
  - anchor:
    - `in_contact_count = 20`
    - `front_gap_A = 9.148629`
  - current:
    - `in_contact_count = 5`
    - `front_gap_A = 9.105925`

Read:

- the slice creates real restore windows
- but first-contact deep overlap is still not safely constrained at scale
- the larger battle still shows unstable alternation between sharp recovery and
  renewed sticky contact

#### `neutral_36`

JSON-normalized comparison:

- `position_frames`: exact match
- `combat_telemetry`: exact match
- `observer_telemetry` excluding `tick_elapsed_ms`: exact match

#### `neutral_100`

JSON-normalized comparison:

- `position_frames`: exact match
- `combat_telemetry`: exact match
- `observer_telemetry` excluding `tick_elapsed_ms`: exact match

Read for both neutral anchors:

- no behavior-bearing neutral drift was introduced by this slice
- observed drift remains battle-path specific

### 8. Targeted human-readable evidence

#### Evidence A - precontact no-crossing is now real, but still incomplete

`battle_36v36`, first-contact window `61-90`:

- mean contact drops:
  - anchor `36.10`
  - current `32.30`
- mean front gap widens:
  - anchor `3.81`
  - current `5.81`
- worst-case overlap improves:
  - anchor `min front_gap = -3.929596`
  - current `min front_gap = -2.673849`

But it still does not fully dominate:

- `tick 70`
  - current `front_gap_A = -0.383340`

#### Evidence B - mid-window restore-line behavior is visible

`battle_36v36`, `tick 140`:

- anchor:
  - `in_contact_count = 25`
  - `front_gap_A = 5.460188`
- current:
  - `in_contact_count = 5`
  - `front_gap_A = 5.835333`

`battle_100v100`, `tick 120`:

- anchor:
  - `in_contact_count = 43`
  - `front_gap_A = -1.295192`
- current:
  - `in_contact_count = 9`
  - `front_gap_A = 7.028706`

Read:

- the restorative seam is real
- it is not just a formula no-op

#### Evidence C - late sticky contact remains the main unresolved failure

`battle_36v36`, window `230-280`:

- anchor mean contact:
  - `2.39`
- current mean contact:
  - `12.08`

`battle_100v100`, window `280-340`:

- anchor mean contact:
  - `17.87`
- current mean contact:
  - `26.38`

Read:

- late contact persistence is still too strong
- current slice is still not acceptable as the maintained `1 unit = 100 ships`
  battle read

### 9. Explicit drift explanation

Current engineering explanation of the remaining drift:

1. the delayed contact-maturity gate fixes a real structural issue
   - precontact no-crossing was previously shutting off almost immediately

2. that change is enough to create real restore windows
   - especially around the first post-contact recovery band

3. but heading-side opportunity is still not fully dominated at the sharpest
   first-contact spike
   - large-scale battle can still produce deep overlap before the restorative
     side catches up

4. speed-side restraint is stronger than before, but it is still not durable
   enough to suppress later sticky contact across the whole battle

Shortest mechanism read:

- first-contact discipline is better than the earlier frozen experimental family
- restore-line response is real
- late sticky contact and some scale-sensitive first-contact spikes still remain

### 10. Current engineering judgment

Implemented correctly relative to the authorized owner/path:

- yes

Useful seam found:

- yes

Ready for maintained promotion:

- no

Current engineering read:

- keep this as an experimental result only
- do not read this as a maintained battle behavior endorsement
- the next concept question is still:
  - how to keep early local freedom inside fleet hold more reliably at scale
  - while also making late restorative restraint durable enough to reduce
    sticky contact
