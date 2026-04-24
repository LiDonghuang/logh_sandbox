## PR9 Phase II - Unit Local Maneuver Envelope Signal-Role Reassignment Bounded Implementation Report

Date: 2026-04-21  
Scope: bounded experimental runtime slice behind explicit `testonly` enablement  
Status: implemented locally; validation complete; still experimental

### 1. Battle read first

This slice does not read like a "temperature tweak."
It reads like a real controller-role change, but only a bounded one.

What the battle looks like now:

- first-contact crossing is no longer opening quite as early as before
- the deepest early overlap is materially reduced at both `36v36` and
  `100v100`
- late sticky dog-fight persistence is reduced more clearly than in the prior
  experimental branch
- fleet-front readability is somewhat stronger, especially after the initial
  compression phase

What still does not read as solved:

- the first-contact crossing problem is reduced, but not removed
- `36v36` still shows a localized late sticky-contact relapse around the
  `tick 230` neighborhood
- battle asymmetry is not gone; it remains present, although not explosively
  worse than the temporary working anchor

Plain-language judgment:

- this slice is a meaningful improvement in battle behavior
- but it is still an experimental mechanism step, not a maintained promotion

### 2. Mechanism judgment

This slice was implemented as:

- signal-role reassignment

It was **not** implemented as:

- target-owner redesign
- locomotion rewrite
- retreat
- mode introduction
- parameter heating as the primary tool

Primary controller-order read after this slice:

1. early front-gap truth constrains local freedom first
2. smoothed relation / hold / brake context contributes later restorative
   response second

That is closer to the intended battle rule:

- first prevent crossing
- then restore

### 3. Static owner/path audit

Changed owner/path:

- `runtime/engine_skeleton.py`
- `EngineTickSkeleton._compute_unit_desire_by_unit(...)` at line `1662`

Unchanged active surfaces:

- same-tick target source stays:
  - `_compute_unit_intent_target_by_unit(...)` at line `3606`
- locomotion still consumes the same carrier inside:
  - `integrate_movement(...)` at line `2889`
- combat execution still stays in:
  - `resolve_combat(...)` at line `3718`
- carrier shape stays:
  - `desired_heading_xy`
  - `desired_speed_scale`

### 4. Exact role reassignment implemented

Implemented early embargo owner:

- `battle_relation_gap_raw`
- read at line `1752`
- converted into bounded early permission / severity at lines `1876-1900`

Implemented heading-side read after reassignment:

- heading opportunity still reads `fleet front -> selected target bearing`
- local heading bias now uses:
  - `front_bearing_need`
  - `heading_turn_need`
  - bounded localizers
  - `early_embargo_permission`
- active lines:
  - `1923-1933`

Implemented speed-side read after reassignment:

- early speed restraint now reads raw front-gap embargo directly
- later restorative response still reads smoothed relation / brake context
- active lines:
  - early embargo response: `1940-1943`
  - later restorative response: `1945-1965`

Implemented restore-line path kept as later response only:

- `restore_line_weight` remains driven by later violation / brake context
- active lines:
  - `1992-2001`

Retired from live control ownership in this function:

- `engagement_geometry_active_current`
- `contact_maturity_gate`
- `precontact_nocrossing_permission`

Demoted to auxiliary-localizer status:

- `near_contact_gate`
- `maneuver_context_gate`
- local turn / bearing urgency signals

### 5. Coupling audit

Reused scalar family:

- `battle_relation_gap_raw`
- `battle_relation_gap_current`
- `battle_brake_drive_current`
- `battle_hold_weight_current`

Existing active job before this slice:

- the battle-gap bundle already derives these in the fleet-level relation path
  inside the same file:
  - `battle_relation_gap_current = self._relax_scalar(...)` at line `2564`
  - `battle_brake_drive_current` writeback from relaxed brake at line `2588`
  - `battle_hold_weight_current` writeback from relaxed hold at line `2602`

New bounded job added in this slice:

- `battle_relation_gap_raw`
  - early embargo / early speed-restraint onset
- `battle_relation_gap_current`
  - later violation severity context only
- `battle_brake_drive_current`
  - later restorative brake context only
- `battle_hold_weight_current`
  - later restorative hold context only

Why the reuse is still bounded:

- raw gap truth is now separated from smoothed restorative context
- no single scalar family member is acting as:
  - early guard
  - mixed permission owner
  - maturity release owner
  - restore owner
  all at once

Residual coupling risk that still remains:

- the relation-gap family still influences both fleet-level motion and
  unit-local maneuver
- so duplicated cross-stage influence still exists
- the risk is reduced, but not eliminated, because the family is now split into
  raw early guard vs smoothed later restore rather than fully decoupled

### 6. What did not change

Still unchanged:

- no second target owner
- no guide-target semantics
- no mode
- no retreat implementation
- no persistent target memory
- no broad locomotion rewrite
- no module split
- no combat-coupling redesign in this slice

Also not changed in this slice:

- no viewer/HUD redesign
- the old `contact_maturity` / `precontact_nocrossing_permission` debug readout
  was not repurposed to new semantics
- those old surfaces should now be treated as retired from live control meaning,
  not as active mechanism truth

### 7. Compile check

Command:

```text
python -m py_compile runtime/engine_skeleton.py
```

Result:

- pass

### 8. Narrow smoke

Smoke posture:

- maintained active scenario
- `battle_36v36`
- explicit experimental enablement:
  - `runtime.physical.local_desire.experimental_signal_read_realignment_enabled = true`
- `steps = 120`
- `capture_positions = false`
- `include_target_lines = false`
- `print_tick_summary = false`
- `plot_diagnostics_enabled = false`
- `post_elimination_extra_ticks = 0`

Result:

- `final_tick = 120`
- `first_contact_tick = 60`
- `first_damage_tick = 60`
- `in_contact_final = 16`
- `damage_events_final = 16`

Read:

- the bounded experimental branch remains live
- the run completes normally
- contact remains active, but the end-of-smoke contact load is lower than the
  prior intermediate implementation in this turn

### 9. Paired comparison against current temporary working anchor

Anchor set:

- `analysis/reference_notes/eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_battle_36v36_baseline_20260420.json`
- `analysis/reference_notes/eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_battle_100v100_baseline_20260420.json`
- `analysis/reference_notes/eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_neutral_36_baseline_20260420.json`
- `analysis/reference_notes/eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_neutral_100_baseline_20260420.json`

Validation posture:

- explicit experimental enablement through the existing `testonly` surface
- baseline execution settings reused from each stored anchor

#### `battle_36v36`

Final state:

| case | A alive / hp | B alive / hp |
| --- | --- | --- |
| temporary working anchor | `28 / 2106.809046` | `27 / 2200.015838` |
| current experimental branch | `28 / 2259.192599` | `26 / 2116.436041` |

Key battle-read summary:

- first front-gap crossing is delayed:
  - `73 -> 74`
- first negative relation-gap is delayed:
  - `72 -> 73`
- the early deepest front overlap becomes much shallower:
  - `-3.929596 -> -2.300341`
- late sticky contact is slightly lower overall
- return-to-line window is better on averages, but not uniformly clean

Window review:

| window | anchor mean contact | current mean contact | anchor mean front gap | current mean front gap | anchor min front gap | current min front gap |
| --- | --- | --- | --- | --- | --- | --- |
| `61-90` | `35.93` | `37.30` | `3.54` | `3.71` | `-3.93` | `-2.30` |
| `120-160` | `22.54` | `21.93` | `7.74` | `8.23` | `5.46` | `5.58` |
| `190-220` | `1.74` | `1.71` | `10.88` | `10.96` | `8.43` | `8.72` |
| `230-280` | `2.51` | `2.31` | `10.81` | `11.11` | `6.79` | `8.81` |

Important localized evidence:

- at `tick 90`, current battle is more open than the anchor:
  - `front_gap = 5.804272` vs `8.969004`
  - `in_contact = 0` vs `1`
- at `tick 190`, current battle is cleaner than the anchor:
  - `front_gap = 10.430138` vs `8.432633`
  - `in_contact = 0` vs `2`
- but at `tick 230`, a local sticky-contact pocket still exists:
  - `in_contact = 14` vs `2`

Read:

- `36v36` shows a real early-overlap improvement
- late sticky contact is lower on averages
- but localized relapse still exists, so the battle is not fully stabilized

#### `battle_100v100`

Final state:

| case | A alive / hp | B alive / hp |
| --- | --- | --- |
| temporary working anchor | `68 / 5344.369009` | `65 / 5181.952767` |
| current experimental branch | `69 / 5433.242669` | `71 / 5594.684001` |

Key battle-read summary:

- first front-gap crossing is delayed more clearly:
  - `73 -> 75`
- first negative relation-gap is also delayed:
  - `73 -> 74`
- the early deepest overlap is cut by more than half:
  - `-1.894438 -> -0.842697`
- late sticky contact drops materially
- return-phase contact and front-gap both improve

Window review:

| window | anchor mean contact | current mean contact | anchor mean front gap | current mean front gap | anchor min front gap | current min front gap |
| --- | --- | --- | --- | --- | --- | --- |
| `58-90` | `79.42` | `78.70` | `3.14` | `3.61` | `-1.89` | `-0.84` |
| `120-170` | `32.84` | `31.53` | `3.48` | `3.48` | `-3.53` | `-2.75` |
| `220-260` | `22.44` | `18.10` | `6.13` | `6.67` | `-0.69` | `2.05` |
| `280-340` | `18.08` | `14.05` | `8.02` | `8.72` | `5.67` | `5.88` |

Important localized evidence:

- at `tick 90`, current contact is lower, but first crossing has only just
  started:
  - `front_gap = -0.014347` vs `0.616950`
  - `in_contact = 47` vs `52`
- at `tick 120`, overlap is still present, but shallower than the anchor:
  - `front_gap = -1.337390` vs `-2.192404`
- at `tick 220`, current battle still has contact:
  - `13` vs `11`
  but the later window as a whole is meaningfully cleaner

Read:

- `100v100` shows the clearest benefit from this slice
- crossing is delayed
- deepest overlap is reduced
- late sticky contact is materially reduced

#### `neutral_36`

Final state:

| case | A alive / hp | final centroid_x |
| --- | --- | --- |
| temporary working anchor | `36 / 3600.0` | `349.609520` |
| current experimental branch | `36 / 3600.0` | `349.609520` |

Read:

- no observable drift

#### `neutral_100`

Final state:

| case | A alive / hp | final centroid_x |
| --- | --- | --- |
| temporary working anchor | `100 / 10000.0` | `348.995671` |
| current experimental branch | `100 / 10000.0` | `348.995671` |

Read:

- no observable drift

### 10. Human-readable evidence summary

If this slice is described only in battle language, the clearest evidence is:

- Units still do not obey a perfect no-crossing line, but they now break that
  line later
- when they do cross, the overlap is less deep
- the battle returns to a readable fleet-front state more often, especially in
  the larger battle
- the larger-scale fight benefits more clearly than the smaller one
- the experimental branch is still not symmetry-clean or relapse-free

### 11. Drift explanation

Accepted experimental drift:

- this slice intentionally changes runtime behavior
- so exact match to the temporary working anchor is not the goal

Observed drift:

- `36v36`
  - early mean contact rises slightly even though overlap depth improves
  - one localized late sticky-contact relapse remains
- `100v100`
  - overall lethality decreases and later front readability improves
  - asymmetry remains present, though not explosively worse than the anchor
- neutral fixtures remain unchanged

Mechanism interpretation of the drift:

- using raw gap truth for early restraint improved crossing timing and overlap
  depth
- removing `speed_turn_need` from the early embargo brake made the early guard
  materially more behavior-bearing
- later restorative context remained bounded to smoothed relation / brake / hold
  signals, which reduced late sticky contact rather than expanding free-fight
  behavior

### 12. Short conclusion

This bounded experimental slice is a real improvement over the temporary
working anchor in the maneuver-envelope line.

Most important effects:

- early crossing is delayed
- deepest early overlap is reduced
- late sticky contact is reduced
- neutral behavior stays unchanged

Most important limitation:

- the battle still does not satisfy a fully stable fleet-front read, especially
  at `36v36`

So the correct current read is:

- successful bounded experimental signal-role reassignment
- still experimental
- not yet maintained-promotion ready
