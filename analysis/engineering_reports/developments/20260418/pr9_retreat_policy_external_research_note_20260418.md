# PR9 Retreat Policy External Research Note 20260418

## Scope

- Type: runtime design / governance discussion note
- Target topic: post-contact retreat policy for formation-era fleets
- Code status: no mechanism change in this note

## Why This Note Exists

Current runtime behavior around `tick 60~90` in `36 vs 36` shows a clear gap:

- fleets get too close before backing off
- once retreat intent appears, left and right wings rotate in opposite directions
- long periods of internal oscillation follow before a later large-scale orbit/chase appears

The immediate design question is not only "should ships back away," but:

- when should they keep their current front and make sternway
- when should they turn away and change front
- at which layer should that choice live

This note combines:

- current active code-path truth
- external shiphandling / ship-modeling references
- a recommended policy shape for governance review

## Current Active Code Truth

### 1. Retreat intent is currently generated as a signed movement command

In `runtime/engine_skeleton.py`, `_evaluate_target_with_v4a_bridge(...)` computes:

- `relation_drive = approach_drive - brake_drive`
- if `relation_drive < 0`, `movement_command_direction[fleet_id]` becomes the reverse of the current reference axis

Relevant path:

- `runtime/engine_skeleton.py:2267`

### 2. Reference axis and reverse command are now decoupled

After the latest bounded fix:

- `last_target_direction` remains the reference / coarse-body axis
- `movement_command_direction` carries the signed movement command
- `_resolve_v4a_reference_surface(...)` now reads `state.last_target_direction`

Relevant paths:

- `runtime/engine_skeleton.py:906`
- `runtime/engine_skeleton.py:922`
- `runtime/engine_skeleton.py:1255`
- `runtime/engine_skeleton.py:1312`

This was the correct first repair, because reverse command should not mirror the reference frame.

### 3. Low-level locomotion still has no true "sternway while keeping front"

In `integrate_movement(...)`, the low-level owner still does:

1. build `total_direction`
2. rotate current heading toward `desired_heading_hat` with `_rotate_direction_toward(...)`
3. move forward along `realized_heading_hat` with positive speed

Relevant paths:

- `runtime/engine_skeleton.py:824`
- `runtime/engine_skeleton.py:2841`
- `runtime/engine_skeleton.py:2879`
- `runtime/engine_skeleton.py:2897`
- `runtime/engine_skeleton.py:2915`

So the current runtime still lacks:

- signed longitudinal velocity in the body frame
- a separate decision between "back away while keeping front" and "turn away"

### 4. Current turn direction is shortest signed angle

`_rotate_direction_toward(...)` chooses clockwise or counterclockwise from the sign of the shortest angular delta.

That means the observed:

- left wing clockwise
- right wing counterclockwise

is not random. It is a direct consequence of:

- mirrored local desired headings
- shortest-angle turning
- absence of a dedicated retreat mode

## External Findings

## A. Standard ship maneuvering models separate longitudinal, lateral, and yaw dynamics

The MMG standard method models ship maneuvering in terms of a maneuvering simulation model with explicit motion-state handling, and practical implementations expose separate surge / sway / yaw state variables and separate control inputs for propulsion and rudder.

Why this matters here:

- a reverse / braking command is not the same thing as a heading command
- "change speed sign" and "change heading" are different control responsibilities
- our current low-level still collapses them into one direction-following rule

Sources:

- Yasukawa, Yoshimura, "Introduction of MMG standard method for ship maneuvering predictions"  
  https://link.springer.com/article/10.1007/s00773-014-0293-y
- `pymaneuvering` MMG implementation README, showing explicit surge / sway / yaw state and propulsion/rudder inputs  
  https://github.com/nikpau/pymaneuvering

## B. Astern maneuvering is real, but steering authority is weaker and slower than ahead

Multiple seamanship references are consistent on this point:

- rudder effectiveness is much stronger ahead than astern
- astern propulsion applied while still making headway gives poor or confused rudder response
- straight backing is possible, but it is slower, less stable, and more sensitive to propeller/side-force effects than normal ahead steerage

Why this matters here:

- adding a true sternway / back-off mode is reasonable
- but it should not behave like "instant reverse forward-motion"
- sternway should be slower and lower-authority than ahead motion

Sources:

- Victorian marine training material, "Vessel Handling"  
  https://files-em.em.vic.gov.au/public/MSAR/Trainer/archive/07-Master-to-30NM/09-Vessel-Handling-Master-To-30NM-2018.pdf
- New York Naval Militia seamanship manual  
  https://dmna.ny.gov/forms/naval/NYNMINST_3120_2_MEBS_Seamanship_Manual.pdf
- U.S. aids-to-navigation seamanship manual  
  https://chet-aero.com/wp-content/uploads/2016/11/cim_16500_21_seamanship.pdf

## C. Naval withdrawal / danger-avoidance is usually expressed as turn-away / retirement, not long stern-first fighting

Historical fleet instructions repeatedly describe disengagement and torpedo avoidance as:

- turn away
- retirement action
- formation-preserving changes of course

not as prolonged stern-first retreat by each ship independently.

Why this matters here:

- a local "back off a little" maneuver is plausible
- a sustained fleet-level disengagement should probably become a coordinated turn-away / retirement action, not endless reverse command on a fixed front

Sources:

- U.S. Navy War Instructions (1944), night action and turn-away / retirement guidance  
  https://www.ibiblio.org/hyperwar/USN/ref/WarInst/WarInst-8.html  
  https://www.ibiblio.org/hyperwar/USN/ref/WarInst/WarInst-12.html
- British fighting instructions examples for battlefleet course alterations / evasive maneuvers  
  https://www.hmshood.org.uk/reference/official/adm239/adm239-261_SectVIII.html

## Design Implications For This Repo

## 1. The codebase needs two different retreat families, not one overloaded reverse command

The sources suggest we should distinguish:

- **Back-off / sternway mode**
  - short-range spacing correction
  - keep the coarse-body front mostly stable
  - allow limited negative longitudinal realization
  - weak yaw change, weak speed, short duration

- **Turn-away / retirement mode**
  - larger or sustained disengagement
  - coordinated fleet-level heading change
  - new reference axis chosen upstream
  - low-level locomotion then turns into that new axis normally

Current code has neither family explicitly.
It only has:

- reverse movement command upstream
- shortest-angle turn downstream

That is why current behavior becomes a mirrored pinwheel instead of a controlled retreat.

## 2. "Back off" should be narrow and bounded, not the default disengagement language

Based on seamanship and naval tactics references, the most defensible first slice is:

- add a **short-range sternway/back-off** mode only
- use it only in the narrow band where fleets are too close but should not yet reorient the battle line

This is safer than immediately making all negative `relation_drive` into backward motion.

Recommended first-policy intent:

- if retreat demand is small, recent, and axis coherence is still acceptable:
  - keep front
  - allow bounded sternway
- if retreat demand is large, sustained, or lateral geometry is already breaking coherence:
  - promote to turn-away / retirement action

## 3. The decision should be fleet-level first, unit-level second

The current unwanted motion is amplified because each unit individually resolves reverse intent via local shortest-angle turning.

For this repo, the cleaner ownership split is:

- fleet / coarse-body layer decides the retreat family
- unit / locomotion layer realizes that family within per-unit limits

That means:

- whether we are in `back_off` or `turn_away` should not be independently re-decided by each unit
- unit-level logic should only realize the already-chosen family

## 4. If sternway is added, it should be materially weaker than ahead motion

External references do support the human intuition already raised in thread:

- sternway should be slower and less authoritative than ahead motion

For this codebase, that means a future sternway mode should likely have:

- lower max speed fraction than ahead
- lower effective steering authority
- lower acceleration into sternway than normal ahead acceleration
- hysteresis so it does not chatter on and off across a contact boundary

This does **not** mean `max_decel_per_tick` should directly stand in for sternway speed.
Those are different semantics:

- deceleration limit: how fast speed magnitude changes
- sternway capability: how much negative longitudinal motion is allowed once retreat mode is chosen

## Recommended Governance Direction

## Recommended policy statement

For PR #9, the most suitable direction appears to be:

1. keep the current `reference axis` / `reverse command` decoupling
2. do **not** let negative `relation_drive` mean "every unit shortest-turns toward a reverse vector"
3. add a bounded fleet-level retreat-family decision:
   - `back_off_keep_front`
   - `turn_away_retirement`
4. implement `back_off_keep_front` first, narrowly:
   - short duration
   - short range
   - limited sternway speed
   - minimal reference-axis change
5. leave full retirement / battle-line turn-away as a later explicit slice

## Why this is the best fit for our current code

It matches both sides of the problem:

- external shiphandling: astern motion exists, but is weaker and not identical to ahead steering
- naval tactics: sustained disengagement is usually a coordinated turn-away problem

It also matches our local runtime truth:

- current bug is not only "no backward motion"
- it is also "reverse intent is being forced through a heading-change-only realization"

## Practical First-Slice Criteria For Discussion

These are not yet implementation instructions. They are a governance-ready proposal for the next bounded slice.

Possible `back_off_keep_front` entry conditions:

- `relation_drive < 0`
- fleets already in contact / over-close band
- `front_axis_delta` still small
- no explicit retirement / flank-turn signal
- retreat demand is recent and modest, not long-sustained

Possible `back_off_keep_front` realization characteristics:

- keep using `last_target_direction` as reference axis
- allow signed longitudinal motion along negative reference axis
- cap sternway to a low fraction of normal speed
- reduce turn authority while in this mode
- exit with hysteresis, not immediate sign flip

Possible escalation to `turn_away_retirement`:

- retreat demand sustained for many ticks
- front-axis coherence already breaking
- lateral distortion large
- enemy no longer approximately ahead on the current reference frame

## Governance Questions

The next governance discussion should explicitly settle:

1. Is PR #9 intended to support only **short-range back-off while keeping front**, or also a full **retirement action** family?
2. Should the retreat-family decision live purely at fleet/coarse-body level, with unit locomotion only realizing it?
3. Is signed longitudinal motion in low-level locomotion acceptable as a new runtime capability, if kept narrow and explicitly recorded?

## Bottom Line

External references do **not** support the current emergent behavior as a good long-term answer.

They support a more explicit split:

- reverse spacing correction is a bounded sternway problem
- sustained disengagement is a coordinated turn-away / retirement problem

For this repo, the most appropriate next step is therefore:

- **not** more parameter tweaking
- **not** more shortest-angle turning around a negative command
- but an explicit retreat policy that separates `back_off_keep_front` from `turn_away_retirement`

## Sources

- IMO Resolution A.601(15), Provision and Display of Manoeuvring Information on Board Ships  
  https://wwwcdn.imo.org/localresources/en/KnowledgeCentre/IndexofIMOResolutions/AssemblyDocuments/A.601%2815%29.pdf
- IMO Resolution MSC.137(76), Standards for Ship Manoeuvrability  
  https://wwwcdn.imo.org/localresources/en/KnowledgeCentre/IndexofIMOResolutions/MSCResolutions/MSC.137%2876%29.pdf
- Yasukawa, Yoshimura, "Introduction of MMG standard method for ship maneuvering predictions"  
  https://link.springer.com/article/10.1007/s00773-014-0293-y
- `pymaneuvering` MMG implementation README  
  https://github.com/nikpau/pymaneuvering
- Vessel Handling training material  
  https://files-em.em.vic.gov.au/public/MSAR/Trainer/archive/07-Master-to-30NM/09-Vessel-Handling-Master-To-30NM-2018.pdf
- NY Naval Militia Seamanship Manual  
  https://dmna.ny.gov/forms/naval/NYNMINST_3120_2_MEBS_Seamanship_Manual.pdf
- Aids to Navigation Manual - Seamanship  
  https://chet-aero.com/wp-content/uploads/2016/11/cim_16500_21_seamanship.pdf
- U.S. Navy War Instructions (1944), HyperWar  
  https://www.ibiblio.org/hyperwar/USN/ref/WarInst/WarInst-8.html  
  https://www.ibiblio.org/hyperwar/USN/ref/WarInst/WarInst-12.html
- ADM 239/261 Fighting Instructions excerpt  
  https://www.hmshood.org.uk/reference/official/adm239/adm239-261_SectVIII.html
