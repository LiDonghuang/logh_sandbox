## PR9 Phase II - Local Desire 36v36 Mechanism Logic and Root-Cause Analysis

Date: 2026-04-20  
Scope: mechanism logic introduction and bounded root-cause analysis only  
Status: document-only analysis after `heading_bias_cap=0.03` worsening on maintained `battle_36v36`

### 1. One-sentence conclusion

The current `local_desire` problem is not a simple "cap too hot" issue; the
main failure is an asymmetric control structure in which heading-side
fleet-front-relative bias is live and behavior-bearing, while speed-side remains
too weak to preserve standoff or bound over-commit, so lowering
`heading_bias_cap` can move the system into a worse unilateral collapse regime
instead of cooling it monotonically.

### 2. Scope and active owner/path

This note is intentionally limited to maintained `battle_36v36`.

Active owner/path under analysis:

- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1662>)
  - `EngineTickSkeleton._compute_unit_desire_by_unit(...)`
- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:2705>)
  - `EngineTickSkeleton.integrate_movement(...)`
- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:3422>)
  - `EngineTickSkeleton._compute_unit_intent_target_by_unit(...)`
- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:3534>)
  - `EngineTickSkeleton.resolve_combat(...)`

What this note is **not** re-opening:

- target-selection ownership
- `resolve_combat(...)` ownership
- `local_desire` carrier shape
- second target / guide-target semantics
- mode / retreat / persistent memory
- broad locomotion-family redesign
- combat-scalar redesign

### 3. Assumptions used for this note

Assumptions made explicitly:

- comparison anchor is the refreshed temporary working-anchor baseline:
  [eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_battle_36v36_baseline_20260420.json](<E:/logh_sandbox/analysis/reference_notes/eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_battle_36v36_baseline_20260420.json:1>)
- active maintained settings still expose:
  - `turn_need_onset = 0.45`
  - `heading_bias_cap = 0.06`
  - `speed_brake_strength = 0.03`
  in [test_run/test_run_v1_0.runtime.settings.json](<E:/logh_sandbox/test_run/test_run_v1_0.runtime.settings.json:58>)
- controlled comparison run for this note uses the same maintained path, with
  only `runtime.physical.local_desire.heading_bias_cap` overridden to `0.03`
- existing `battle_36v36` is not perfectly mirror-symmetric in doctrine terms:
  fleet `A` and fleet `B` come from different archetype IDs in the maintained
  scenario, so some asymmetry already exists in the anchor; the question here is
  amplification, not creation from zero

### 4. Mechanism logic introduction

#### 4.1 Current same-tick chain

The current maintained battle chain is:

1. fleet-level movement direction is evaluated
2. same-tick unit target identity is selected
3. `local_desire` generates:
   - `desired_heading_xy`
   - `desired_speed_scale`
4. locomotion consumes those desire outputs together with cohesion / separation
5. post-movement combat re-checks range / cone / contact and applies damage

Relevant code anchors:

- target source:
  [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:3478>)
- local desire:
  [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1738>)
- locomotion consumption:
  [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:3079>)
- combat re-check:
  [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:3610>)

#### 4.2 What heading-side now reads

After the accepted signal-read realignment, heading-side local bias is driven by
fleet-front-relative off-axis geometry:

- `fleet_front_lateralness = abs(cross(fleet_front_hat, attack_hat_xy))`
- `front_bearing_need = clamp01(fleet_front_lateralness)`
- `local_heading_bias_weight = heading_bias_cap * near_contact_gate * front_bearing_need`

See:

- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1781>)
- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1813>)

Important read:

- this signal is magnitude-only
- it says "target is off-axis relative to fleet front"
- it does **not** encode left/right tactical meaning
- it does **not** encode standoff preservation
- it does **not** encode bounded recovery / back-out semantics

#### 4.3 What speed-side still reads

Speed-side remains unit-facing-relative and brake-only:

- `turn_need_raw = (1 - unit_facing_alignment) * 0.5`
- `heading_turn_need = smoothstep01(...)`
- `speed_turn_need = heading_turn_need^2`
- `desired_speed_scale = max(0.97, 1 - speed_brake_strength * near_contact_gate * speed_turn_need)`

See:

- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1786>)
- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1797>)
- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1830>)

Important read:

- speed-side can only brake
- the brake floor is `0.97`, so this line can remove at most `3%` of speed
- `turn_need_onset` affects this side, but not heading-side bias any more

#### 4.4 How locomotion consumes the desire

Locomotion then uses:

- `target_term = desired_heading_xy`
- `desired_speed_scale_input = clamp01(unit_desire["desired_speed_scale"])`
- `desired_heading_hat = normalize(cohesion + maneuver)`
- `realized_heading_hat = rotate_toward(current_heading_hat, desired_heading_hat, max_turn_deg_per_tick)`
- final desired speed:
  `unit.max_speed * desired_speed_scale_input * turn_speed_alignment_scale`

See:

- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:3088>)
- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:3124>)
- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:3141>)

The important asymmetry is:

- heading can materially change the direction of the target term
- speed-side local brake can only weakly reduce speed
- therefore local desire currently has a strong steering lever and a very weak
  restraint lever

#### 4.5 Why the local-desire gate is late

The current near-contact gate opens only late:

- start ratio: `0.35`
- full ratio: `0.20`

Given maintained `attack_range = 20.0`, this means:

- gate begins at distance `7.0`
- gate is fully on only at distance `4.0`

See:

- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1703>)
- [test_run/test_run_v1_0.runtime.settings.json](<E:/logh_sandbox/test_run/test_run_v1_0.runtime.settings.json:32>)

So the current `local_desire` line is being activated precisely in the regime
where standoff failure and front-rank overrun matter most.

### 5. Hypotheses and validation

#### 5.1 Hypothesis A: this is just a hot-cap problem

Naive expectation:

- lower `heading_bias_cap`
- less break-away
- less asymmetry

Controlled 36v36 result:

- temporary anchor final: `28 : 27`
- current `0.06` final: `21 : 20`
- current `0.03` final: `14 : 27`

So this hypothesis is false.

Lowering the cap does **not** cool the system monotonically.

#### 5.2 Hypothesis B: target owner or combat owner drift caused the asymmetry

Static audit says no.

This turn did **not** change:

- same-tick target source
- fire-cone target selection owner
- `resolve_combat(...)` owner
- damage quality owner

The changed line remains local to:

- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1813>)

So the asymmetry is not coming from a hidden reroot of target or combat owners.

#### 5.3 Hypothesis C: current root problem is signal/feedback mismatch

This hypothesis is supported.

Claim:

- heading-side is now strong enough to move units off the coarse fleet front
- speed-side is not strong enough to bound that motion
- the signal itself does not protect standoff / separation
- once one fleet starts losing reciprocal firing geometry, the current line can
  amplify that fleet's breakdown instead of damping it

Supported by both static path and run evidence below.

### 6. 36v36 dynamic evidence

#### 6.1 Anchor behavior

Temporary working anchor:

- final alive: `28 : 27`
- first alive gap `>= 3`: tick `141`
- first alive gap `>= 5`: none
- window `190..220`
  - mean in-contact count: `1.742`
  - mean target links:
    - `A->B = 1.000`
    - `B->A = 0.645`
  - mean `front_gap = 10.703`
  - mean `front_strip_gap = 13.874`

Read:

- anchor does show some transient asymmetry
- but it still re-establishes separation in the later battle window

#### 6.2 Current default `heading_bias_cap = 0.06`

Current default realignment:

- final alive: `21 : 20`
- first alive gap `>= 3`: tick `324`
- first alive gap `>= 5`: none
- window `130..160`
  - mean in-contact count: `17.548`
  - mean target links:
    - `A->B = 8.710`
    - `B->A = 8.258`
  - mean `front_gap = 2.850`
  - mean `front_strip_gap = 7.977`
  - mean hostile overlap pairs: `0.097`
- at tick `130`
  - `front_gap = -2.550`
  - `front_strip_gap = 2.892`

Read:

- this slice already damages standoff behavior
- first-contact overrun is visible
- but battle remains roughly reciprocal between fleets

#### 6.3 Reduced cap `heading_bias_cap = 0.03`

Controlled `0.03` run:

- final alive: `14 : 27`
- first alive gap `>= 3`: tick `153`
- first alive gap `>= 5`: tick `199`
- first alive gap `>= 10`: tick `424`
- window `130..160`
  - mean in-contact count: `14.935`
  - mean target links:
    - `A->B = 5.742`
    - `B->A = 8.581`
  - mean `front_gap = 2.005`
  - mean `front_strip_gap = 8.314`
  - mean hostile overlap pairs: `0.419`
- window `190..220`
  - mean in-contact count: `11.097`
  - mean target links:
    - `A->B = 4.677`
    - `B->A = 6.387`
  - mean `front_gap = 6.723`
  - mean `front_strip_gap = 9.174`

Critical ticks:

- tick `130`
  - alive: `32 : 34`
  - links: `12 : 14`
  - `front_gap = -9.216`
  - `front_strip_gap = 1.111`
- tick `140`
  - alive: `31 : 33`
  - links: `0 : 3`
- tick `160`
  - alive: `30 : 33`
  - links: `2 : 5`
  - `front_gap = 0.939`
  - `front_strip_gap = 2.001`
- tick `200`
  - alive: `28 : 33`
  - links: `1 : 1`
  - `front_gap = 11.461`
  - `front_strip_gap = 15.846`
- tick `500`
  - alive: `14 : 27`
  - links: `1 : 9`
  - in-contact count: `10`

Read:

- reducing the cap did **not** restore fleet separation
- the first-contact overrun actually became much deeper
- reciprocal target links became strongly skewed toward fleet `B`
- once that skew appears, fleet `A` never recovers to anchor-like reciprocity

### 7. Why the reduced cap makes things worse

#### 7.1 The cap is not acting on a symmetric cooler

`heading_bias_cap` is not cooling a complete local-adaptation controller.

It is scaling only this heading-side term:

- `heading_bias_cap * near_contact_gate * front_bearing_need`

That means:

- it changes how much units are pulled toward selected-target-bearing relative
  to fleet front
- it does **not** strengthen the missing restraint side
- it does **not** add standoff preservation
- it does **not** add backward recovery

So lowering the cap is not "less of the whole behavior." It is only less of one
side of an already asymmetric controller.

#### 7.2 The signal does not encode keep-distance semantics

`front_bearing_need` is:

- `abs(cross(fleet_front_hat, attack_hat_xy))`

So it answers only:

- how off-axis is the selected target relative to the fleet front?

It does not answer:

- should the unit keep distance?
- should it avoid crossing through the front?
- should it recover backward instead of rotating across the line?

Therefore parameter tuning alone cannot make this signal protect standoff; the
signal lacks that content.

#### 7.3 Speed-side is too weak to counter heading-side damage

Static path explains why speed-side has very little authority:

- speed is only brake-only
- local brake floor is `0.97`
- so the local-desire line can shave at most `3%` before turn-speed alignment
  scaling

This is the key control mismatch:

- heading-side can move where units point
- speed-side cannot meaningfully stop overrun

This matches the earlier engineering tuning result that
`speed_brake_strength` behaved like an inert knob on the maintained battle path.

#### 7.4 The current line can amplify pre-existing fleet asymmetry

The maintained battle is not a pure mirror duel.

Because heading-side now reads each fleet's own coarse front:

- any existing per-fleet difference in front coherence or fire-axis organization
  can feed back into local-desire behavior

Observed evidence from focus indicators:

- at tick `100` under `0.03`
  - `A fire_eff = 0.302`
  - `B fire_eff = 0.440`
- at tick `140`
  - `A fire_eff = 0.000`
  - `B fire_eff = 0.084`
- at tick `200`
  - `A effective_fire_axis_coherence = 0.679`
  - `B effective_fire_axis_coherence = 0.979`

Read:

- once fleet `A` begins to lose reciprocal fire organization, the current
  heading-side line does not help it recover boundedly
- instead, the fleet-front-relative signal can continue to generate unit peel
  without a meaningful speed-side counterforce
- that is how a moderate early imbalance turns into a large late alive gap

#### 7.5 Deterministic target-selection details are not the primary root cause

The target selector does contain deterministic tie-breaks:

- nearest target first
- then local numeric rank / scan order

See:

- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:3516>)
- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:3522>)

But this is not the primary explanation here because:

- the anchor already contains those same tie-breaks
- the anchor does **not** produce catastrophic `14 : 27` collapse

Engineering read:

- deterministic selection may be an amplifier
- it is not the main causal change

### 8. Root-cause judgment

Current best root-cause judgment:

1. the current heading-side signal is live and behavior-bearing
2. that signal is fleet-front-relative, magnitude-only, and does not encode
   standoff / bounded recovery semantics
3. speed-side remains too weak to act as the compensating restraint
4. therefore `heading_bias_cap` tuning is operating an incomplete controller
5. in that incomplete controller, lower cap can land the system in a worse
   regime:
   - still enough to break standoff
   - not enough to maintain reciprocal engagement cleanly
   - strong enough to amplify pre-existing fleet asymmetry into one-sided
     collapse

This is why the current problem should be read as:

- not "find the right scalar cap"
- but "the signal/controller structure is missing the bounded counterforce and
  bounded separation semantics that tuning assumes exist"

### 9. What this means for next governance discussion

What should be preserved from the current slice:

- `local_desire` carrier
- single same-tick target source
- heading-side read no longer being silently collapsed by unit-facing fire-cone
  compression

What should **not** be assumed:

- that a lower `heading_bias_cap` will solve the problem
- that the present speed-side line is already a meaningful regulator
- that the current signal read can preserve fleet-scale standoff by tuning alone

Most bounded next-step question, in engineering terms:

- how to add a real bounded restraint / activation balance to local desire,
  especially on the speed-side and separation-preservation side, without
  introducing mode / retreat / second target owner

### 10. Validation commands used for this note

Static audit:

- `rg -n "desired_heading_xy|desired_speed_scale|unit_desire_by_unit|coarse_body_heading_current|_compute_unit_intent_target_by_unit|resolve_combat" runtime/engine_skeleton.py`

Controlled 36v36 reruns:

- inline Python using:
  - [test_run/test_run_scenario.py](<E:/logh_sandbox/test_run/test_run_scenario.py:1119>)
    `prepare_active_scenario(...)`
  - [test_run/test_run_entry.py](<E:/logh_sandbox/test_run/test_run_entry.py:45>)
    `run_active_surface(...)`
- overrides applied only to:
  - `runtime.physical.local_desire.heading_bias_cap`
  - `capture_positions=True`
  - `capture_hit_points=True`
  - `frame_stride=1`
  - `include_target_lines=True`

No runtime code was changed for this note.
