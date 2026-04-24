## PR9 Phase II - Unit Local Maneuver Envelope Signal-Role Reassignment Implementation-Ready Confirmation

Date: 2026-04-21  
Scope: document-first implementation-ready confirmation for Human + Governance  
Status: confirmation only; no runtime edit in this note

### 1. Battle read first

Current battle read on the experimental maneuver-envelope branch is:

- first-contact front-rank crossing still happens too early
- the branch found a real and useful local maneuver seam and should not be
  thrown away
- but early line discipline is still too weak
- later restorative response is doing too much recovery work after the front is
  already structurally broken
- the resulting battle surface still shows too much:
  - deep first-contact overlap
  - sticky dog-fight persistence
  - late restore-line behavior
  - fleet-front readability loss

The preserved good read is:

- Units are no longer completely locked to fleet-level coarse heading
- some local peel-out / return-to-line potential is visible

The unacceptable read is:

- local opportunity being allowed to outrun fleet-level hold

### 2. Mechanism judgment

Current judgment is:

- this is a mechanism-variable role problem
- it is not mainly a parameter-temperature problem
- the next honest bounded slice, if later authorized, should remain:
  - within the existing `unit_local_maneuver` owner/path
  - within the existing same-tick target source
  - within the existing carrier

This slice should be read as:

- signal-role reassignment

It should **not** be read as:

- target-owner redesign
- locomotion rewrite
- combat-doctrine redesign
- retreat slice

### 3. Exact owner/path under review

Current owner/path under review:

- `runtime/engine_skeleton.py`
- `EngineTickSkeleton._compute_unit_desire_by_unit(...)`

Unchanged active surfaces:

- same-tick target source:
  - `selected_target_by_unit`
- same carrier shape:
  - `desired_heading_xy`
  - `desired_speed_scale`

### 4. Variable-role split to carry into any next runtime slice

#### 4.1 Early embargo owner

Engineering recommendation:

- early no-crossing embargo should be owned by:
  - `battle_relation_gap_raw`

Battle-read reason:

- this is the closest current maintained runtime read of:
  - "how much front-gap room is actually left right now?"
- it is more suitable for first-contact prevention than:
  - `engagement_geometry_active_current`
  - `battle_relation_gap_current`
  - `battle_brake_drive_current`

Mechanism read:

- this variable should answer:
  - "should local maneuver still remain tightly bounded because the fleet front
    is too close to violation?"

It should **not** answer:

- "contact is mature enough now"
- "restore pressure should increase now"

#### 4.2 Later restorative context owner

Engineering recommendation:

- later restorative context should be owned by the smoothed battle-context
  family:
  - `battle_relation_gap_current`
  - `battle_brake_drive_current`
  - `battle_hold_weight_current`

Battle-read reason:

- these quantities are suitable for:
  - violation severity
  - hold pressure
  - brake context
  after the battle has already entered a tighter or violated relation state

Mechanism read:

- these variables should answer:
  - "how much restore / brake pressure should now exist?"

They should **not** answer:

- "is early crossing still forbidden?"

#### 4.3 Auxiliary localizers only

Engineering recommendation:

- these variables should be demoted to auxiliary-localizer status only:
  - `near_contact_gate`
  - `maneuver_context_gate`
  - `front_bearing_need`
  - `heading_turn_need`
  - `speed_turn_need`

Battle-read reason:

- these values describe local opportunity or local geometry urgency
- they do not legitimately own fleet-level permission to break line discipline

Mechanism read:

- they may shape local response
- they must not silently become the effective strategic owner

#### 4.4 Variables to retire from live control ownership

Engineering recommendation:

- retire from live control ownership:
  - `engagement_geometry_active_current` as maturity-release owner
  - `contact_maturity_gate`
  - `precontact_nocrossing_permission`

Reason:

- these currently mix geometric engagement, release timing, and permission in a
  way that does not line up with actual first-contact battle behavior

### 5. Parameter judgment

Current engineering judgment:

- parameter changes are secondary in this line
- cap / onset / strength tuning should not be used to compensate for:
  - wrong early-guard owner
  - wrong late-restore owner
  - overloaded mixed-permission variables

This means:

- `local_desire_turn_need_onset`
- `local_desire_heading_bias_cap`
- `local_desire_speed_brake_strength`

should be treated as bounded tuning knobs only after variable-role reassignment
is judged correct.

### 6. Coupling risk statement

The main reused scalar family remains:

- `battle_relation_gap_raw`
- `battle_relation_gap_current`
- `battle_brake_drive_current`
- `battle_hold_weight_current`

Existing job already present on the active path:

- fleet-level relation / approach / close / brake / hold shaping

Proposed new bounded job:

- raw relation-gap:
  - early embargo / early speed-restraint onset
- smoothed relation / brake / hold:
  - later restorative context only

Known risk:

- duplicated effect across fleet-level and unit-local stages
- hidden cross-stage amplification if the same scalar becomes a broad drive term
- semantic overload if one scalar family is allowed to answer too many
  controller questions

Engineering recommendation:

- reuse is acceptable only under a strict role split
- reuse is not acceptable if the same scalar family is again allowed to act as:
  - early guard
  - permission owner
  - severity owner
  - restore owner
  all at once

### 7. Minimal runtime-shape read if later authorized

If Human + Governance later authorize the next bounded runtime slice, the
minimal implementation read should be:

1. keep the same owner/path
2. keep the same target source
3. keep the same carrier
4. replace early release / permission logic with a raw-gap-driven embargo read
5. keep heading-side opportunity real but subordinate it to early embargo
6. keep speed-side brake-only
7. reserve smoothed battle context for later restorative response only
8. keep localizers auxiliary rather than primary

### 8. What still does not change

Still unchanged:

- no second target owner
- no guide-target semantics
- no mode system
- no retreat implementation
- no persistent target memory
- no broad locomotion rewrite
- no module split
- no combat-coupling redesign in this line
- no harness-owned doctrine growth

### 9. Short conclusion

Engineering's implementation-ready read is now explicit:

- early embargo owner:
  - `battle_relation_gap_raw`
- later restorative context owners:
  - `battle_relation_gap_current`
  - `battle_brake_drive_current`
  - `battle_hold_weight_current`
- auxiliary localizers only:
  - `near_contact_gate` and related local geometry signals
- retired from live control ownership:
  - `engagement_geometry_active_current`
  - `contact_maturity_gate`
  - `precontact_nocrossing_permission`

So the next bounded slice, if authorized, should be judged as a
signal-role-reassignment slice, not as further formula tuning.
