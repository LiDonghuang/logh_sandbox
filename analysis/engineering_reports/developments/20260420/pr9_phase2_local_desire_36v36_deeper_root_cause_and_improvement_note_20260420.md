## PR9 Phase II - Local Desire 36v36 Deeper Root-Cause and Improvement Note

Date: 2026-04-20  
Scope: deeper mechanism discussion, direct answers, and bounded improvement suggestions only  
Status: superseding follow-up to the earlier preliminary 36v36 local-desire root-cause note

### 1. One-sentence conclusion

The strongest current read is that heading-side fleet-front-relative bias is the
main active problem, not because heading-side should be removed, but because it
is being driven by a shared near-contact multiplier that does not encode
standoff preservation, while speed-side remains too weak to counterbalance it;
this makes the controller structurally asymmetric and explains why lowering
`heading_bias_cap` to `0.03` can worsen one-sided collapse instead of cooling
the battle.

### 2. Direct answers first

#### 2.1 What exactly is `near_contact_gate`?

Active owner:

- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1662>)
  - `EngineTickSkeleton._compute_unit_desire_by_unit(...)`

Definition:

- `near_contact_gate` is a local same-tick proximity scalar derived from
  attacker-to-selected-target distance
- it is **not** a semantic combat-state flag
- it is **not** contact hysteresis state
- it is just a geometric ramp in `[0, 1]`

Current formula:

- start ratio: `0.35`
- full ratio: `0.20`
- with maintained `attack_range = 20.0`
  - gate starts at distance `7.0`
  - gate is fully on at distance `4.0`

Code:

- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1755>)
- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1763>)

Engineering read:

- this gate means "the unit is now close enough that local combat geometry
  should start mattering"
- it does **not** mean "we are in a good regime to break formation"
- it does **not** mean "standoff has already been safely satisfied"

#### 2.2 Why is `near_contact_gate` used as a direct multiplier in multiple formulas, and is that appropriate?

Current active uses of this exact scalar inside `local_desire`:

1. heading-side:

- `local_heading_bias_weight = heading_bias_cap * near_contact_gate * front_bearing_need`
- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1813>)

2. speed-side:

- `desired_speed_scale = max(0.97, 1 - speed_brake_strength * near_contact_gate * speed_turn_need)`
- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1830>)

So yes, the same distance gate is currently acting as a direct multiplier for
two different behavioral outputs:

- heading bias
- speed brake

Engineering judgment:

- using a shared distance-derived regime gate is not inherently wrong
- but in the current implementation it is **not appropriate as the main
  multiplier for both channels**

Why it is not appropriate now:

- heading-side and speed-side do different jobs
  - heading-side chooses how much off-axis reorientation to allow
  - speed-side should bound over-commit and preserve recoverability
- the shared gate says only "target is now nearby"
- it says nothing about:
  - whether the fleets are still respecting standoff
  - whether front ranks are already interpenetrating
  - whether further peel-out should be suppressed
  - whether brake should become stronger than heading bias in this regime

So the deeper problem is not just that `near_contact_gate` exists. The deeper
problem is that it is currently being treated as a universal activation scalar
for two channels that should not share the same semantic gate.

#### 2.3 Are personality parameters or random seed the real cause of the current mild asymmetry?

Current active read: no, not in the maintained runtime path that is relevant to
this analysis.

Static code-path truth:

- `fleet_a_parameters` / `fleet_b_parameters` are still built in
  [test_run/test_run_scenario.py](<E:/logh_sandbox/test_run/test_run_scenario.py:1145>)
- but that file also already documents:
  - "PersonalityParameters remains a high-level prepared payload only; it does
    not flow back into maintained runtime state evolution on the current
    mainline."
  - [test_run/test_run_scenario.py](<E:/logh_sandbox/test_run/test_run_scenario.py:227>)
- `prepare_active_scenario(...)` returns those parameters as payload metadata,
  but they do not enter:
  - `runtime_cfg`
  - `observer_cfg`
  - `EngineTickSkeleton` hot-path logic

Random/seed truth:

- `resolve_effective_seed(-1)` does produce a random integer at scenario prep
  time:
  [test_run/test_run_scenario.py](<E:/logh_sandbox/test_run/test_run_scenario.py:967>)
- but on the current maintained battle path:
  - `effective_random_seed` and `effective_background_map_seed` are summary-side
    only
  - `effective_metatype_random_seed` only affects archetype/meta preparation
- because those personality/meta outputs do **not** currently flow into runtime
  state evolution, seed is not a credible explanation for the observed
  `local_desire` battle asymmetry in this note

So your correction is right in the engineering sense:

- the currently relevant mild asymmetry is more plausibly coming from
  deterministic geometry/order effects
- especially:
  - nearest-target selection under deterministic tie-break
  - fleet/unit iteration order
  - unit ID/rank ordering
  - small geometric differences getting amplified by the current local-desire
    controller

Personality/archetype identity may still matter at the metadata/prepared level,
but it is not the active runtime cause for the present local-desire behavior.

### 3. Refined mechanism logic

#### 3.1 Current same-tick chain

The maintained 36v36 battle chain is:

1. fleet-level movement direction is evaluated
2. same-tick `selected_target_by_unit` is chosen
3. `local_desire` emits:
   - `desired_heading_xy`
   - `desired_speed_scale`
4. locomotion consumes desire + cohesion + separation
5. combat re-checks range / cone / contact and applies damage

Anchors:

- target source:
  [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:3478>)
- local desire:
  [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1738>)
- locomotion consumption:
  [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:3079>)
- combat re-check:
  [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:3610>)

#### 3.2 What heading-side now really does

Current heading-side read:

- `front_bearing_need = abs(cross(fleet_front_hat, attack_hat_xy))`
- `local_heading_bias_weight = heading_bias_cap * near_contact_gate * front_bearing_need`

Meaning:

- the farther the selected target bearing is from the current fleet front, the
  more heading-side wants to bias toward that target
- and it wants to do so exactly when the unit is already entering the near
  contact regime

This signal is:

- fleet-front-relative
- magnitude-only
- standoff-blind
- recovery-blind

#### 3.3 What speed-side now really does

Current speed-side read:

- remains unit-facing-relative
- remains brake-only
- is still controlled by `turn_need_onset`
- is still clamped by a `0.97` floor

That means the local-desire speed line has extremely weak authority:

- at most a `3%` local brake
- and only after a facing-turn burden has already been detected

This is why speed-side has repeatedly looked inert in maintained battle tuning.

#### 3.4 Existing battle context is already available, but local_desire ignores it

This is the most important deeper structural finding.

`_compute_unit_desire_by_unit(...)` already receives:

- `movement_bundle_by_fleet`
  - [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1667>)

But then it immediately discards it:

- `_ = movement_bundle_by_fleet`
  - [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1706>)

Why this matters:

- the maintained v4a bundle already carries battle/standoff-aware signals such
  as:
  - `battle_relation_gap_current`
  - `battle_hold_weight_current`
  - `engagement_geometry_active_current`
  - `front_reorientation_weight_current`
- these are exactly the kinds of signals that say:
  - are fleets still separated?
  - is the current contact geometry already tight?
  - should we prioritize internal stability over more peel-out?

Current local_desire does **not** read any of them.

So the present local-desire controller is trying to decide near-contact
adaptation while ignoring the existing maintained battle context that already
knows whether standoff is being preserved.

This is a stronger root-cause clue than the earlier note made explicit.

### 4. Why heading-side bias is likely the main culprit

The current controller has three important properties:

1. heading-side is now live and behavior-bearing
2. heading-side uses a near-contact multiplier that does not know whether
   standoff is already broken
3. speed-side is too weak to counter the resulting over-commit

This is why heading-side is the main culprit in the current failure:

- not because heading-side should never exist
- but because heading-side currently has real steering authority without a
  comparably real restraint authority

In plain words:

- units now have a real mechanism to peel off the coarse front
- but they do not have a comparably real mechanism to say:
  - stop over-advancing
  - preserve line separation
  - recover without rotational collapse

### 5. Why `heading_bias_cap = 0.03` can be worse than `0.06`

This was the key user challenge, and the code/evidence support a clearer answer
now.

Naive intuition:

- lower cap = less local desire = cooler battle

But that intuition assumes the cap is scaling a complete, balanced controller.
It is not.

What the cap is actually scaling is only:

- heading-side off-axis pull

What it is **not** scaling:

- a real speed-side braking authority
- a standoff-safe gate
- a bounded recovery gate

So the real behavior is:

- `0.06`:
  - too much peel-out
  - standoff damage is visible
  - but reciprocal reorientation is still relatively strong, so both fleets stay
    in the fight more symmetrically
- `0.03`:
  - still enough near-contact heading action to damage standoff
  - but not enough reciprocal heading response to maintain balanced firing
    geometry after overrun begins
  - speed-side still does not step in
  - so one fleet can lose reciprocal target links first and then never recover

This matches the 36v36 evidence:

- temporary anchor final: `28 : 27`
- current `0.06` final: `21 : 20`
- current `0.03` final: `14 : 27`

And more specifically:

- `0.03`, tick `130`
  - `front_gap = -9.216`
  - `front_strip_gap = 1.111`
- `0.03`, tick `140`
  - target links `A->B = 0`
  - target links `B->A = 3`

So `0.03` is not a cooler version of the same regime. It is a different regime:

- still destructive enough to break standoff
- less able to sustain reciprocal local heading recovery
- therefore more vulnerable to one-sided collapse

### 6. Evidence summary

#### 6.1 Temporary working anchor

- final alive: `28 : 27`
- first alive gap `>= 5`: none
- later battle window `190..220` returns to low contact:
  - mean in-contact count `1.742`
  - mean `front_gap = 10.703`

#### 6.2 Current default `0.06`

- final alive: `21 : 20`
- first-contact overrun already visible:
  - tick `130`
    - `front_gap = -2.550`
- but still relatively reciprocal:
  - window `130..160`
    - `A->B = 8.710`
    - `B->A = 8.258`

#### 6.3 Reduced cap `0.03`

- final alive: `14 : 27`
- deeper overrun:
  - tick `130`
    - `front_gap = -9.216`
- faster asymmetry:
  - first alive gap `>= 5`: tick `199`
- more persistent one-sided target-link skew:
  - window `130..160`
    - `A->B = 5.742`
    - `B->A = 8.581`
  - tick `500`
    - `A->B = 1`
    - `B->A = 9`

#### 6.4 Focus-indicator support

Under `0.03`, focus indicators show fleet-side divergence in fire organization:

- tick `100`
  - `A fire_eff = 0.302`
  - `B fire_eff = 0.440`
- tick `140`
  - `A fire_eff = 0.000`
  - `B fire_eff = 0.084`
- tick `200`
  - `A effective_fire_axis_coherence = 0.679`
  - `B effective_fire_axis_coherence = 0.979`

Read:

- once one side loses reciprocal organization, current local_desire does not
  help it recover
- it continues to act as steering freedom without real bounded damping

### 7. Improvement suggestions

These are engineering suggestions only, not implementation instructions.

#### 7.1 Keep

What should be preserved:

- `local_desire` layer and carrier
- single same-tick target source:
  - `selected_target_by_unit`
- split of heading-side and speed-side responsibilities
- heading-side no longer being compressed by unit-facing fire-cone alone

#### 7.2 Replace

What should be replaced:

- current use of shared `near_contact_gate` as the main direct multiplier for
  both heading and speed outputs
- current heading-side primary activation:
  - `heading_bias_cap * near_contact_gate * front_bearing_need`

#### 7.3 Most bounded design correction

Most bounded correction direction, still within the existing owner/path:

1. heading-side should no longer be gated mainly by raw near-contact distance
2. heading-side should instead be conditioned by:
   - off-axis opportunity
   - plus a standoff-safe / not-already-overrun gate
3. speed-side should be made genuinely live as a later restraint

The best minimal source for that additional context is likely **already present**
in `movement_bundle_by_fleet`, because the maintained v4a bundle already knows:

- relation gap
- hold weight
- engagement geometry activity
- front reorientation state

So the best improvement path is **not** "invent more local target logic." It is
more likely:

- keep the current target source
- keep the current desire carrier
- let local_desire read one existing standoff-aware battle scalar from the
  already-passed movement bundle

#### 7.4 Near-contact gate should be demoted, not necessarily deleted

Engineering recommendation:

- do not necessarily delete `near_contact_gate`
- demote it from "primary behavioral multiplier" to "auxiliary regime limiter"

That would mean:

- it can still say "this only matters when the fight is getting close"
- but it should not, by itself, decide how much heading peel-out is allowed

#### 7.5 Speed-side needs to become a real regulator

Engineering recommendation:

- the next correction should probably make speed-side genuinely capable of
  bounded restraint
- not through retreat
- not through mode
- not through a second target source
- but through a stronger and more context-aware brake semantics

Most likely qualitative goal:

- heading-side:
  - earlier and softer
  - but standoff-aware
- speed-side:
  - later and stronger
  - and actually capable of preventing overrun / rotational-collapse recovery

### 8. Most likely next governance question

If this goes back to governance, the most useful bounded question is now:

- how should local_desire stop using raw near-contact as its shared primary
  multiplier, and instead read one existing standoff-aware battle scalar while
  keeping:
  - one target source
  - the current carrier
  - no mode
  - no retreat
  - no second owner

### 9. Validation basis for this note

Static owner/path audit:

- `rg -n "near_contact_gate|front_bearing_need|heading_turn_need|speed_turn_need|movement_bundle_by_fleet|battle_relation_gap_current|battle_hold_weight_current|engagement_geometry_active_current" runtime/engine_skeleton.py`
- `rg -n "fleet_a_parameters|fleet_b_parameters|PersonalityParameters|effective_random_seed|effective_metatype_random_seed" test_run/test_run_scenario.py runtime/runtime_v0_1.py`

Controlled 36v36 reruns:

- maintained `prepare_active_scenario(...)`
- maintained `run_active_surface(...)`
- overrides only to:
  - `runtime.physical.local_desire.heading_bias_cap`
  - plus capture controls for frame-level analysis

No runtime code was changed for this note.
