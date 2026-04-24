## PR9 Phase II - Unit Local Maneuver Envelope Signal-Role Reassignment Bounded Implementation Proposal

Date: 2026-04-21  
Scope: document-first bounded proposal for Human + Governance  
Status: proposal only; no implementation in this note

### 1. One-sentence conclusion

The recommended next bounded slice is to keep the current `unit_local_maneuver`
owner/path and carrier, but reassign variable roles inside
`runtime/engine_skeleton.py` so that early no-crossing / precontact restraint is
driven by raw front-gap truth, while smoothed relation / hold / brake signals
are reserved for later restorative response.

### 2. Plain-language battle read first

For the current LOGH-style abstraction, a Unit may have some local maneuver
freedom, but that freedom must stay inside fleet-level line discipline.

That means:

- before first contact is mature, a Unit should not be allowed to peel through
  the front just because a local firing line looks attractive
- at first contact, fleet hold should remain readable before local opportunity
  is allowed to widen
- if the front is already being violated, Unit-local response should become
  restorative
- large, persistent dog-fight freedom is not acceptable for the maintained
  "`1 unit = 100 ships`" read

Acceptable battle read:

- modest local peel-out
- modest return-to-line
- front remains recognizable as a fleet front
- some local off-axis correction exists, but it does not dominate first contact

Unacceptable battle read:

- early front-rank crossing before contact is properly established
- deep first-contact overlap followed by late repair
- persistent free-flying dog-fight behavior
- rotational collapse caused by late restorative response trying to recover a
  line that has already broken

### 3. Exact owner/path to change

Proposed owner/path to change:

- `runtime/engine_skeleton.py`
- `EngineTickSkeleton._compute_unit_desire_by_unit(...)`

This proposal changes only:

- which existing or already-derived battle variables own:
  - early no-crossing embargo
  - early speed restraint onset
  - later restorative response context

This proposal does **not** change:

- same-tick target-selection ownership
- `resolve_combat(...)` ownership
- locomotion-family ownership
- carrier shape
- schema by default

### 4. Fixed background assumptions

This proposal assumes the following remain fixed:

- `unit_local_maneuver` / current `local_desire` layer stays
- single same-tick target source stays:
  - `selected_target_by_unit`
- carrier shape stays:
  - `desired_heading_xy`
  - `desired_speed_scale`
- maintained default stays on the safe frozen path
- experimental work remains behind explicit `testonly` enablement

### 5. Keep vs replace

#### Keep

- current owner/path family in `_compute_unit_desire_by_unit(...)`
- single same-tick target source
- split between:
  - heading-side local opportunity
  - speed-side brake-only restraint
- existence of late restorative response
- fleet/front axis != unit facing != actual velocity separation

#### Replace

- current live use of `engagement_geometry_active_current` as the release owner
  for "contact is mature enough to relax no-crossing"
- current live use of:
  - `precontact_nocrossing_permission = contact_maturity_gate + ((1 - contact_maturity_gate) * precontact_room_gate)`
  as if it were a true no-crossing control variable
- current role of `near_contact_gate` as a strong shared multiplier across both
  channels

### 6. Mechanism diagnosis carried into this proposal

The current experimental branch is now read as failing mainly because of
signal-role misassignment:

- `engagement_geometry_active_current` says fleets are geometrically involved;
  it does not honestly say that local crossing is now safe to relax
- `precontact_nocrossing_permission` is an overloaded mixed-permission variable,
  not a direct "crossing still forbidden" read
- `near_contact_gate` still gives raw unit-to-target proximity too much direct
  behavioral authority
- `battle_brake_drive_current` / `battle_hold_weight_current` are useful as
  later restorative context, but they arrive too late to serve as the first
  guard

Therefore the next bounded step should be role reassignment, not further tuning
of the current formula family.

### 7. Proposed read for early no-crossing ownership

#### 7.1 Preferred primary source

Preferred primary early-guard source:

- `battle_relation_gap_raw`

Reason:

- it is already derived from front-gap truth
- it is computed from the maintained battle-gap path:
  - `battle_current_front_strip_gap`
  - `battle_target_front_strip_gap`
- it is raw rather than relaxed, so it is better suited to first-contact guard
  semantics than `battle_relation_gap_current`

Preferred semantic read:

- this quantity should own:
  - "how close are we to violating the front-gap envelope right now?"
- it should **not** own:
  - "contact is mature enough now"

#### 7.2 Optional naming clarification

If Engineering later judges that the semantic burden of `battle_relation_gap_raw`
is still too broad, an internal runtime-local alias may be introduced for
clarity, for example:

- `front_crossing_margin_raw`

But the preferred bounded baseline remains:

- reuse the existing raw gap truth without schema expansion

### 8. Heading-side plan

Heading-side should remain:

- local
- vector-only
- target-informed through:
  - `fleet front -> selected target bearing`

But heading-side freedom should no longer be released by
`contact_maturity_gate` / `precontact_nocrossing_permission`.

Proposed role assignment:

- heading-side opportunity still reads:
  - `fleet front -> selected target bearing`
- heading-side permission / embargo should primarily read:
  - raw front-gap truth via `battle_relation_gap_raw`

Practical read:

- if the front-gap margin is still being consumed, heading-side freedom should
  remain tightly bounded
- only once early no-crossing pressure has genuinely relaxed should local
  heading opportunity be allowed to open further

This keeps the heading-side seam real, but subordinates it to fleet-level line
discipline during first contact.

### 9. Speed-side plan

Speed-side should remain:

- later than heading-side
- brake-only
- stronger as restraint than the current experimental branch

But speed-side should be split into two distinct roles.

#### 9.1 Early restraint

Early speed restraint should primarily read:

- raw front-gap truth via `battle_relation_gap_raw`

Reason:

- the first useful job of speed is to help prevent crossing, not merely to
  repair it later

#### 9.2 Later restorative response

Later restorative response should continue to read smoothed battle context:

- `battle_relation_gap_current`
- `battle_brake_drive_current`
- `battle_hold_weight_current`

Reason:

- these are appropriate as later severity / hold / brake context
- they should not be promoted into the first guard against crossing

So the intended control order becomes:

- first prevent
- then restore

rather than:

- first allow local urgency
- then try to repair after overlap is already established

### 10. `near_contact_gate` role after reassignment

`near_contact_gate` should be demoted.

Preferred read after reassignment:

- it may remain as a secondary localizer
- it should not remain a strong shared primary multiplier for both heading-side
  and speed-side behavior

Reason:

- it answers:
  - "this Unit is close to its selected target"
- it does **not** answer:
  - "fleet-level hold may now be relaxed"

This means proximity may still shape local responsiveness, but only after
early-front discipline has already granted room.

### 11. Coupling audit

This proposal reuses existing battle-gap variables, so coupling risk must be
named explicitly.

#### 11.1 Reused scalar family

Primary reused scalar family:

- `battle_relation_gap_raw`
- `battle_relation_gap_current`
- `battle_brake_drive_current`
- `battle_hold_weight_current`

#### 11.2 Where they are already used

Current active uses include:

- fleet-level relation drive in the battle bundle path
- approach / close / brake / hold shaping
- current experimental local maneuver branch

#### 11.3 Risk

Main risks:

- duplicated effect
  - the same relation-gap family can influence both fleet motion and
    unit-local maneuver
- hidden cross-stage amplification
  - if the same scalar is used as a raw drive term in too many places, local
    response may overreact
- semantic overload
  - one variable family may be asked to answer too many different questions

#### 11.4 Recommendation

Reuse is acceptable only under a strict role split:

- raw relation-gap truth:
  - early embargo / early brake onset
- smoothed relation / hold / brake:
  - later restorative context

What should be avoided:

- using smoothed relation / brake / hold as the first early guard
- using raw relation-gap truth as a broad new drive multiplier across the whole
  branch

So this proposal is not asking to give one scalar more power.
It is asking to narrow each scalar to a more honest job.

### 12. What still does not change

Still out of scope:

- second target owner
- guide target / parallel target semantics
- mode system
- retreat implementation
- persistent target memory
- broad locomotion rewrite
- module split
- combat-coupling redesign
- harness / telemetry-owned doctrine growth

This proposal also does **not** recommend:

- promoting `in_contact_count` or other observer-facing telemetry into active
  runtime doctrine ownership

### 13. Minimal implementation shape if later authorized

If later authorized, the bounded implementation shape should be:

1. keep current owner/path and carrier
2. remove `contact_maturity_gate` and `precontact_nocrossing_permission` from
   live control ownership
3. introduce one raw-gap-driven early embargo / early restraint read using the
   existing battle-gap path
4. keep heading-side and speed-side split
5. reserve smoothed battle context for later restorative response only
6. keep `near_contact_gate` secondary if it remains at all

This remains smaller than:

- a combat-adaptation family redesign
- a locomotion rewrite
- a retreat slice
- a target-owner change

### 14. Validation posture if later authorized

Required validation posture:

- static owner/path audit
- compile check
- narrow smoke with explicit experimental enablement
- paired comparison against the current temporary working anchor
- targeted human-readable evidence focused on:
  - fewer precontact crossings
  - less first-contact deep overlap
  - less persistent sticky dog-fight behavior
  - stronger early preservation of fleet-front readability
- explicit drift explanation

Recommended additional evidence:

- a short trace centered on the first-contact window showing:
  - `battle_relation_gap_raw`
  - `battle_relation_gap_current`
  - heading-side local bias weight
  - speed-side restraint weight

### 15. Short governance-facing conclusion

Engineering recommends that the next bounded experimental step be framed as a
signal-role reassignment slice:

- keep the current `unit_local_maneuver` layer, owner/path, target source, and
  carrier
- retire `contact_maturity_gate` / `precontact_nocrossing_permission` from live
  control ownership
- use raw front-gap truth as the early no-crossing / precontact restraint owner
- reserve smoothed relation / hold / brake variables for later restorative
  response only

This is judged to be the smallest honest next slice after the current
mechanism-variable diagnosis.
