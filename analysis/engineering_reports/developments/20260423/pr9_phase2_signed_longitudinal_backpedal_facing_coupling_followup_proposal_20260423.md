# PR9 Phase II - `signed_longitudinal_backpedal` Facing-Coupling Follow-up Proposal

Date: 2026-04-23
Scope: document-first / design-first follow-up proposal only
Status: proposal only; no runtime implementation in this note

**Line classification:** Locomotion capability line
**Owner classification:** capability-layer correction proposal; fleet authorization unchanged
**Honest claim boundary:** prevent turn-away forward motion from masquerading as
keep-front backpedal

## 1. Battle Read First

Human VIZ read on `battle_36v36`:

- at tick 60, both fleets are still cleanly readable as three rows of roughly
  12 units each
- by tick 66, each fleet's first row begins turning away, split between the two
  rotational sides, while rows two and three mostly remain stable
- by tick 71, rows two and three begin to lose stability
- by tick 80, both formations show bad longitudinal compression
- after that, both fleets tend to remain at distance while individual units
  rotate and the internal formation stays broken

Engineering re-read of tick 60 to tick 80 matches the human observation.

Using tick 60 as the row anchor, the front-row facing / speed read for fleet A
is:

| tick | front-row facing dot to enemy axis | front-row signed speed along own facing | front-row velocity along enemy axis | row depth R1-to-R3 |
| --- | ---: | ---: | ---: | ---: |
| 60 | 1.000 | 1.000 | 1.000 | 7.15 |
| 66 | 0.954 | 0.180 | 0.172 | 7.14 |
| 71 | -0.299 | 0.202 | -0.060 | 7.05 |
| 80 | -0.010 | 0.373 | -0.004 | 3.33 |

The key point is tick 71:

- facing has already rotated away from the enemy axis
- signed speed along the unit's own facing is still positive
- velocity along the enemy axis is negative only because the unit's facing has
  already turned away

That is not honest keep-front backpedal. It is forward travel along a turned-away
orientation.

The current signed-longitudinal capability is real, but the critical tick 60 to
tick 80 failure is still dominated by turn-away realization.

## 2. Current Code-Path Diagnosis

Active runtime owner remains:

- `runtime/engine_skeleton.py`
- `EngineTickSkeleton._compute_unit_desire_by_unit(...)`
- `EngineTickSkeleton.integrate_movement(...)`

Current carrier split remains correct in concept:

- `desired_heading_xy`
  - intended facing / heading intent
- `desired_speed_scale`
  - unsigned speed envelope / cap
- `desired_longitudinal_travel_scale`
  - signed longitudinal travel intent

The implementation problem is after the Unit desire seam.

Current locomotion realization computes:

```text
target_term = desired_heading_xy
total_direction = normalize(cohesion + target_term + separation + boundary)
realized_heading_hat = rotate current orientation toward total_direction
signed travel is then applied along realized_heading_hat
```

This means the same vector still acts as:

- translation pressure
- formation correction pressure
- collision / separation correction pressure
- facing target
- signed longitudinal travel axis

So when local contact / separation / restore pressure turns `total_direction`
away from the enemy axis, locomotion rotates the Unit's facing away first. Then a
positive signed longitudinal speed moves the Unit backward in battle terms.

That is the wrong coupling:

- the new carrier is signed
- but the axis it uses is still allowed to become a turn-away axis
- therefore positive forward speed along a rotated axis can look like give-ground

Observed focus payload during the critical tick 60 to tick 80 window supports
this:

- `desired_longitudinal_travel_scale_min` remains `+1.0`
- `realized_signed_longitudinal_speed_min` remains positive
- visible backward travel is coming from facing rotation, not from negative
  signed-longitudinal travel

## 3. Proposed Next Design Gate

Proposed concept name:

- `signed_longitudinal_facing_axis_guard`

Short battle read:

- when the signed-longitudinal capability is enabled, the Unit's facing axis
  must remain battle-facing unless fleet / behavior authorization explicitly
  changes that facing intent
- local translation pressure must not be allowed to turn the facing axis away
  merely to realize give-ground
- if backward travel is needed, it must come through the explicit signed
  longitudinal carrier, not through rotated-forward motion

Preferred implementation judgment:

- no new primary carrier
- no boolean as locomotion design
- no negative overload of `desired_speed_scale`
- no behavior-line retuning in this step
- treat the guard as a correction to the existing experimental
  `signed_longitudinal_backpedal` gate

If Governance requires an explicit A/B switch for review, it should be a
temporary experimental gate only. It should not become a new locomotion design
carrier.

## 4. Exact Realization Rule Proposed

Plain-language rule:

1. `desired_heading_xy` remains the facing intent.
2. Turn-rate limits apply to facing realization from the current orientation
   toward that facing intent.
3. `desired_longitudinal_travel_scale` controls travel forward / zero /
   backward along the realized facing axis.
4. Local formation, separation, and boundary pressures may affect speed
   restraint and projection / correction, but must not silently become a
   turn-away facing target during the signed-longitudinal keep-front experiment.
5. If the signed carrier is non-negative and local pressure would require
   turning away to move backward, locomotion should slow / hold rather than
   synthesize backward motion through a rotated facing axis.
6. If the signed carrier is negative, locomotion may move backward along the
   realized facing axis, still under the reverse-authority cap.

Shortest engineering read:

```text
facing_target_hat = normalize(desired_heading_xy)
realized_facing_hat = rotate current orientation toward facing_target_hat

unsigned_speed_cap =
    unit.max_speed
    * fixture_step_magnitude_gain
    * desired_speed_scale
    * turn_limited_speed_scale

if desired_longitudinal_travel_scale < 0:
    signed_speed_target =
        -unsigned_speed_cap
        * abs(desired_longitudinal_travel_scale)
        * reverse_authority_scale
else:
    signed_speed_target =
        unsigned_speed_cap
        * desired_longitudinal_travel_scale

travel_axis = realized_facing_hat
velocity = travel_axis * signed_speed_after_accel_decel
orientation = realized_facing_hat
```

The important correction is not the formula's speed surface. The important
correction is that local translation pressure no longer gets to become the
facing axis in the signed-longitudinal keep-front gate.

## 5. What This Solves

This proposal directly targets the observed tick 60 to tick 80 failure:

- first-row turn-away should no longer be the mechanism that creates backward
  battle-axis movement
- rows two and three should not be pulled into the same rotating collapse as
  quickly
- longitudinal compression should be reduced if the previous compression was
  caused by turn-away forward motion
- any visible backward motion should be attributable to a negative
  `desired_longitudinal_travel_scale`, not to positive speed along a reversed
  orientation

It also restores the honest semantic split:

- behavior / fleet side decides whether give-ground is authorized
- locomotion side realizes the permitted ask physically
- locomotion no longer invents retreat-like turn-away movement as a side effect

## 6. What This Does Not Solve

This proposal does not authorize:

- retreat
- turn-away retirement
- arbitrary strafing
- broad facing / translation decoupling
- target-owner redesign
- combat-owner redesign
- behavior-line retuning
- module split
- full 3D locomotion redesign

It also may not by itself produce more early backward travel in tick 60 to tick
80, because the observed critical-window carrier read was still `+1.0`.

If the guard removes turn-away motion but the formation simply stalls or presses
too hard, that would be a separate behavior-line authorization question. It
should not be smuggled into this locomotion correction.

## 7. Owner Split Preserved

Fleet / reference side still owns:

- front axis
- standoff / hold / terminal truth
- higher-level envelope
- back-off / retreat authorization

Unit / locomotion side only owns:

- realizing a permitted physical ask
- preserving the declared carrier semantics
- preventing local steering pressure from silently becoming turn-away retreat

This proposal does not move target selection, combat selection, or retreat
authorization into locomotion.

## 8. Minimal Implementation Surface If Later Authorized

Likely runtime touch:

- `runtime/engine_skeleton.py`
  - `EngineTickSkeleton.integrate_movement(...)`
  - the local block where `total_direction`, `realized_heading_hat`,
    signed-longitudinal speed, orientation, and velocity are computed

Likely harness / VIZ touch:

- no new debug catalog by default
- use existing replay frame position / orientation / velocity fields for the
  tick 60 to tick 80 review
- keep existing `lng` / `vspd` focus reads

Only if Governance needs a compact proof field should Engineering add one small
read, such as:

- `turnaway_forward_motion_guarded_count`

But the preferred first review is to avoid a new indicator unless the replay
read is insufficient.

No required changes expected in:

- `test_run/settings_accessor.py`
- `test_run/test_run_scenario.py`
- `test_run/test_run_execution.py`
- `viz3d_panda/app.py`

unless Governance explicitly requests an A/B experimental setting or a minimal
VIZ proof field.

## 9. Proposed Validation Read If Later Authorized

First validation target:

- `battle_36v36`
- tick window: 60 to 80
- row anchor: tick 60, three rows of 12 units per fleet

Required human-readable questions:

1. Does first-row facing remain battle-facing instead of rotating through
   side/back angles?
2. Does any backward battle-axis movement now come from negative signed
   longitudinal speed rather than from positive speed along turned-away facing?
3. Do rows two and three remain more stable through tick 71?
4. Is row-depth compression around tick 80 reduced?
5. Did the change stay below retreat / turn-away semantics?

Suggested measurable checks:

- front-row average facing dot to enemy axis should not cross below zero during
  the tick 60 to tick 80 keep-front review window
- front-row positive signed speed with negative battle-axis velocity should be
  strongly reduced or eliminated
- R1-to-R3 depth should not collapse from roughly `7.15` to roughly `3.33` in
  the same way
- `desired_longitudinal_travel_scale_min < 0` should be the explanation for
  literal backward travel when it occurs

Then validate:

- `battle_100v100`
- neutral fixtures only if the implementation touches shared movement paths

Default-off no-drift remains mandatory before experimental-on comparison.

## 10. Recommendation

Engineering recommendation:

- do not tune reverse authority yet
- do not retune the behavior-line ask yet
- do not add a broader facing / translation redesign
- first correct the locomotion coupling so `signed_longitudinal_backpedal` cannot
  be replaced by turn-away forward movement

Shortest conclusion:

- the signed carrier remains the right design
- the current axis realization is still wrong in the critical contact window
- next bounded step should be `signed_longitudinal_facing_axis_guard`
- the guard should preserve battle-facing orientation and force any backward
  realization to pass through the explicit signed longitudinal carrier
