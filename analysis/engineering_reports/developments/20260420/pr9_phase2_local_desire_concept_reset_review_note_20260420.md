## PR9 Phase II - Local Desire Concept Reset Review Note

Date: 2026-04-20  
Scope: Human + Governance + Engineering concept-reset review only  
Status: implementation wave frozen; layer/carrier kept; no new runtime slice proposed in this note

### 1. Human-readable opening

For the current "1 unit = 100 ships" battle model, `local_desire` should be
allowed to do only a modest amount of local reshaping near the front:

- let some units lean out of the coarse line a little when a local firing
  opportunity is clearly better than staying perfectly flush
- let those units settle back into the line when that local opportunity passes
- create readable small-scale loosen / tighten behavior inside a still-coherent
  fleet body

`local_desire` should **not** be allowed to do the following:

- turn the battle into sustained unit-level dog fight
- make the two fronts fully pass through each other at first contact
- produce a long-lasting shredded front that no longer reads like a grouped
  fleet body
- force recovery mainly by turning/circulating because there is no clean
  backward separation path

Acceptable battle read:

- modest peel-out
- modest return-to-line
- some local looseness
- but the fleet still reads like a fleet
- front-line distance still matters
- first contact still looks like bounded engagement, not full overlap

Unacceptable battle read:

- persistent unit-by-unit dog fight
- deep front-rank overrun
- obvious loss of keep-distance / standoff behavior
- rotational collapse as the main recovery shape

Plain-language conclusion:

- the current implementation found a real seam
- but it currently gives units too much local freedom without enough local
  restraint
- that is why the layer should be kept, but the current formula family should
  be frozen

### 2. Current mechanism map

Current relevant active path:

1. same-tick target source
   - `selected_target_by_unit`
   - owner:
     [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:3422>)
2. local_desire inputs
   - fleet-level movement direction
   - fleet coarse front heading
   - selected target bearing / distance
   - unit facing
   - also receives `movement_bundle_by_fleet`, but currently does not use it
   - owner:
     [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1662>)
3. local_desire outputs
   - `desired_heading_xy`
   - `desired_speed_scale`
   - owner:
     [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1839>)
4. locomotion realization
   - consumes desire together with cohesion / separation / turn-speed alignment
   - owner:
     [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:3079>)
5. combat execution
   - re-checks range / cone / contact and applies damage
   - owner:
     [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:3534>)

Current local_desire read:

- heading-side primary read:
  - `fleet front -> selected target bearing`
- speed-side primary read:
  - `unit facing -> selected target bearing`

Current over-commit entry point:

- heading-side bias is now live, but it is gated mainly by:
  - `near_contact_gate`
  - `front_bearing_need`
- speed-side remains weak, brake-only, and heavily limited by the current
  `0.97` speed floor

So the current controller has:

- a real steering lever
- but not a comparably real restraint lever

### 3. Existing battle-context signals already available

This is the most important concept-reset fact:

- `local_desire` already receives `movement_bundle_by_fleet`
- but `_compute_unit_desire_by_unit(...)` immediately discards it
- see:
  [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1667>)
  and
  [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1706>)

Existing maintained bundle signals already available include:

- standoff preservation / current relation state:
  - `battle_relation_gap_current`
  - `battle_current_front_strip_gap`
  - `battle_target_front_strip_gap`
- hold pressure / do-not-over-commit pressure:
  - `battle_hold_weight_current`
  - `battle_brake_drive_current`
  - `battle_close_drive_current`
- engagement geometry tightness:
  - `engagement_geometry_active_current`
  - `battle_enemy_front_strip_activation`
- front reorientation state:
  - `front_reorientation_weight_current`
  - `effective_fire_axis_coherence_current`

Relevant owner lines:

- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:2338>)
- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:2458>)
- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:2478>)

Engineering read of best candidate constraints for heading-side peel-out:

1. `battle_relation_gap_current`
   - best direct candidate for "are we still in a standoff-safe relation, or are
     we already too close / too far?"
   - this is the strongest primary candidate

2. `battle_hold_weight_current`
   - best secondary candidate for "should bounded formation stability now matter
     more than more peel-out?"
   - this is the best companion candidate

Other signals are useful but less ideal as the first constraint:

- `engagement_geometry_active_current`
  - good for saying the fight is geometrically tight
  - too coarse by itself for standoff-safe gating
- `front_reorientation_weight_current`
  - useful as orientation-state context
  - not a direct standoff safety signal

Concept judgment:

- the next correction should preferably reuse one or two of these existing
  maintained battle signals
- not invent a second target owner
- not invent a mode system

### 4. Experiment recap

#### 4.1 Temporary working anchor

Lesson:

- battle still had some local asymmetry and contact windows
- but fleets could re-establish distance later
- `local_desire` heading-side remained effectively too silent to show the seam

Behavioral read:

- more stable
- more fleet-like
- less dog-fight-like

#### 4.2 Signal-read realignment

Lesson:

- this was not meaningless
- it successfully made heading-side adaptation real
- it exposed the correct seam: fleet-front-relative local heading opportunity

Behavioral read:

- visible peel-out / return-to-line appeared
- but battle became too dog-fight-like
- keep-distance / standoff behavior weakened

#### 4.3 Cap reduction observations

Lesson:

- direct tuning did not solve the problem
- lowering `heading_bias_cap` was not monotonic cooling
- `0.03` could be worse than `0.06`

Behavioral read:

- this is not a small parameter problem
- current formula family is structurally unbalanced

#### 4.4 Additional recap: speed-side tuning

Lesson:

- `speed_brake_strength` did not behave like a strong live regulator on the
  maintained battle path

Behavioral read:

- current local_desire is not failing because heading exists
- it is failing because heading is real while restraint is still too weak

### 5. Keep / retire / redesign judgment

#### 5.1 Keep

Keep:

- `local_desire` layer
- `local_desire` carrier shape
- single same-tick target source:
  - `selected_target_by_unit`
- split of heading-side and speed-side responsibilities
- the general idea that heading-side should no longer be silently collapsed by
  unit-facing fire-cone compression

#### 5.2 Retire

Retire:

- the assumption that direct cap tuning is the right next move
- the assumption that raw near-contact distance can serve as the main shared
  multiplier for both heading and speed
- the assumption that the current speed-side brake logic is already an adequate
  regulator

#### 5.3 Re-design

Re-design:

- current heading-side gate logic
  - it should no longer be primarily:
    `heading_bias_cap * near_contact_gate * front_bearing_need`
- current speed-side brake logic
  - it needs to become a real bounded restraint, not a nearly inert local brake
- role of `near_contact_gate`
  - keep it only as an auxiliary proximity limiter if needed
  - not as the main semantic controller
- role of standoff-aware battle context
  - promote it into the actual local_desire decision logic
- split between heading-side and speed-side
  - keep the split
  - but make the two channels semantically different on purpose:
    - heading-side = controlled opportunity
    - speed-side = controlled restraint

### 6. Bounded next-step options

Only bounded concept options are listed here. No new runtime slice is proposed
in this note.

#### Option A - Standoff-aware heading gate replacement

What changes:

- heading-side no longer uses raw `near_contact_gate` as its main multiplier
- heading-side instead reads:
  - off-axis opportunity
  - plus one standoff-aware bundle scalar
  - ideally `battle_relation_gap_current`

What stays unchanged:

- same target source
- same carrier
- same owner/path
- no mode / no retreat / no second target owner

Expected behavioral effect:

- less deep peel-out when the fleets are already too close
- less first-contact overrun
- heading remains real, but more bounded

Main risk:

- speed-side may still remain too weak, so this alone may not be enough

#### Option B - Speed-side restraint correction first

What changes:

- speed-side becomes a genuinely live regulator using existing battle-context
  signals such as:
  - `battle_hold_weight_current`
  - `battle_brake_drive_current`
- heading-side stays conceptually similar for one more bounded slice

What stays unchanged:

- same target source
- same carrier
- no mode / no retreat / no second target owner

Expected behavioral effect:

- less overrun
- less rotational collapse
- stronger tendency to keep the fleet body readable

Main risk:

- battle may become too sticky or too conservative if speed-side is corrected in
  isolation

#### Option C - Minimal dual-channel rebalance

What changes:

- heading-side reads:
  - off-axis opportunity
  - plus a standoff-safe gate
- speed-side reads:
  - later hold / brake context
- `near_contact_gate` is demoted to a secondary limiter only

What stays unchanged:

- same target source
- same carrier
- same owner/path
- no mode / no retreat / no second target owner

Expected behavioral effect:

- best chance of preserving visible local adaptation while restoring
  fleet-scale standoff and reducing rotational collapse

Main risk:

- this is the largest of the bounded options and needs careful scope control

### 7. Current recommendation

Current engineering recommendation:

- freeze the present formula family exactly as governance directed
- do not continue parameter tuning on the current implementation
- if a future slice is authorized, the most honest bounded direction is:
  - keep the carrier
  - keep the target source
  - stop using raw near-contact as the shared primary multiplier
  - let local_desire consume one or two already-available standoff-aware bundle
    signals

Shortest engineering read:

- heading-side found the seam
- speed-side did not become a real restraint
- current failure is conceptual, not just parametric

### 8. Validation basis

Static owner/path audit:

- `rg -n "near_contact_gate|front_bearing_need|heading_turn_need|speed_turn_need|movement_bundle_by_fleet|battle_relation_gap_current|battle_hold_weight_current|engagement_geometry_active_current|front_reorientation_weight_current" runtime/engine_skeleton.py`
- `rg -n "fleet_a_parameters|fleet_b_parameters|PersonalityParameters|effective_random_seed|effective_metatype_random_seed" test_run/test_run_scenario.py runtime/runtime_v0_1.py`

Behavior evidence basis:

- refreshed temporary working-anchor baseline
- current signal-read realignment report
- 36v36 controlled reruns with `heading_bias_cap` comparison

No runtime code was changed for this note.
