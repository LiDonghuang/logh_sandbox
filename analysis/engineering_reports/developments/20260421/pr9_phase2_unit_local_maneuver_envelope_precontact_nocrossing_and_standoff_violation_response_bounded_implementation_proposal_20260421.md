## PR9 Phase II - Unit Local Maneuver Envelope Precontact Nocrossing And Standoff-Violation Response Bounded Implementation Proposal

Date: 2026-04-21  
Scope: proposal only; no runtime implementation in this note  
Status: document-first proposal after rehoming the current experimental family to test-only

### 1. Battle read first

For the current LOGH-style large-fleet model, a Unit may have only modest local
freedom.

Acceptable battle read:

- a front unit can edge slightly for a better firing lane
- a unit can slow or ease back into line when the front is getting too tight
- the fleet still reads as a fleet body with a readable front

What must never happen:

- precontact front-rank crossing that breaks hold before contact is truly mature
- many units slipping through each other as if each Unit were a single
  free-flying ship
- standoff collapse that is noticed only after the line is already broken

Plain-language target:

- stop early crossing first
- then make local response restorative when the standoff is already being
  violated

### 2. One-sentence conclusion

The smallest honest next slice is to keep the current owner/path and carrier,
but reinterpret the current experimental family as a **unit-local maneuver
envelope** that first enforces a precontact no-crossing gate and then switches
to a bounded standoff-violation response when fleet relation is already
collapsing.

### 3. Exact owner/path to change

Preferred next owner/path remains:

- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1662)
  - `EngineTickSkeleton._compute_unit_desire_by_unit(...)`

Current carrier may stay unchanged:

- `desired_heading_xy`
- `desired_speed_scale`

Current single target source may stay unchanged:

- `selected_target_by_unit`

Engineering answer on owner/path/carrier:

- yes, the next slice can still remain within the current owner/path and
  carrier
- no second target owner is required
- no schema expansion is required by default

### 4. Existing signal reads best suited to the next slice

#### 4.1 Contact maturity

Preferred primary signal:

- `engagement_geometry_active_current`

Why:

- it is the closest existing maintained read for "is contact now mature enough
  that bounded local freedom may be relaxed a little?"
- it already summarizes whether real engagement geometry has formed, rather than
  only whether one unit happens to be near one target

Reference:

- bundle write:
  [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:2531)
- current upstream read:
  [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1313)

Recommended role:

- use it as the primary maturity gate
- before this gate is sufficiently active, no-crossing discipline should stay
  dominant

#### 4.2 Standoff violation

Preferred primary signal:

- `battle_relation_gap_current`

Why:

- it is the cleanest existing maintained read of whether fleet relation still
  has space or has already been compressed / violated
- it is signed and already battle-context aware

Reference:

- bundle write:
  [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:2541)

Recommended role:

- use it as the main violation severity read
- not as a raw drive term
- only as envelope / violation state input

#### 4.3 Restore-line / restraint context

Preferred signals:

- `battle_brake_drive_current`
- `battle_hold_weight_current`

Why:

- `battle_brake_drive_current` is the sharper "tight relation / brake now"
  context
- `battle_hold_weight_current` is the smoother "stability pressure is already
  active" context

References:

- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:2562)
- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:2564)

Recommended role split:

- `battle_brake_drive_current`:
  - primary severity input for standoff-violation response
- `battle_hold_weight_current`:
  - secondary continuity / smoothing context

#### 4.4 Signal not preferred as the next primary driver

Not recommended as the first primary signal:

- `front_reorientation_weight_current`

Reason:

- useful later for richer restore-line shaping
- but not necessary for the smallest next slice

### 5. Precontact no-crossing definition

Plain-language definition first:

- before contact is mature enough, a unit may adjust locally
- but it may not use that local freedom to cross the effective front too early
- the controller should stop the crossing before the line is broken, not after

Minimal implementation read:

- when contact maturity is still low
- and fleet relation is already approaching the hold band
- heading-side local freedom should be clamped much harder than it is now
- speed-side should not allow local forward continuation to defeat fleet hold

What this means in practice:

- local peel-out remains mostly suppressed before mature contact
- first-contact overlap should be prevented earlier
- no-crossing is treated as a conservative gate, not an after-the-fact repair

### 6. Standoff-violation response definition

Plain-language definition first:

- once fleet relation is already too tight or collapsing, local response should
  stop being permissive
- it should become restorative
- but still remain below a full retreat family

Bounded response for the next slice:

- stronger brake-only restraint
- heading-side restore-line tendency
- no explicit retreat and no doctrine-scale withdrawal owner

Preferred read within the current carrier:

- `desired_speed_scale`
  - becomes more clearly violation-responsive
  - stays brake-only
- `desired_heading_xy`
  - stops opening outward local freedom
  - is biased back toward line-preserving / fleet-preserving heading

Important limit:

- this remains a bounded restore / restraint response
- not a retreat family

### 7. Keep vs replace summary

Keep:

- current owner/path
- current carrier shape
- single target source
- split between heading-side and speed-side channels
- explicit freeze posture on the maintained default

Replace:

- current experimental framing of the next step as "more local_desire tuning"
- current permissive precontact opening
- current speed-side logic that relaxes too quickly once unit-facing turn need
  collapses

### 8. Why this slice stays below retreat

This slice remains smaller than retreat because it still means:

- preserve fleet line if possible
- restore bounded relation if it is being violated
- do not concede contact as a doctrine decision

This slice does **not** yet mean:

- intentionally disengage as a fleet decision
- turn away and retire from the contact
- maintain a separate retreat authorization owner

### 9. What remains explicitly out of scope

- mode system
- second target owner
- persistent target memory
- broad locomotion rewrite
- module split
- combat-coupling redesign
- full retreat implementation in the same slice

### 10. Validation posture if later authorized

If later authorized, validation should focus on:

1. static owner/path audit
2. compile check
3. narrow smoke with explicit test-only enablement
4. paired comparison against the current temporary working anchor
5. targeted human-readable evidence for:
   - fewer precontact crossings
   - fewer first-contact deep overlaps
   - fewer late sticky-contact windows
   - stronger return-to-line after violation begins

### 11. Short engineering recommendation

The next bounded slice should be framed as:

- **unit-local maneuver envelope**

and not primarily as:

- more `local_desire` temperature tuning

The first honest priorities should be:

1. precontact no-crossing gate
2. standoff-violation response
