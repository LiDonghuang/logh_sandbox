## PR9 Phase II - `back_off_keep_front` Behavior-Line Bounded Implementation Proposal

Date: 2026-04-22  
Scope: document-first bounded proposal for Human + Governance  
Status: no implementation in this note

**Line classification:** Behavior line  
**Owner classification:** fleet-authorized / unit-realized  
**Honest claim boundary:** this note may propose bounded give-ground / reopen-space behavior under current locomotion semantics; it may not claim literal keep-front backward motion, full retreat doctrine, or a new locomotion capability already exists

### 1. Battle read first

The next slice should not try to make Units feel "freer."

It should try to create a very specific battle picture:

- when the fronts get too compressed, some front-rank Units stop continuing the
  push
- those Units reopen a little space instead of deepening overlap
- the fleet still reads like a fleet front, not like many independent dog
  fights
- the give-ground remains bounded:
  - not a full breakaway
  - not a turn-away retirement
  - not a free duel cloud

The intended human-readable battle read is:

- acceptable:
  - "they are easing off a bit, making room, and trying to restore a readable
    front"
- not acceptable:
  - "they are now literally backing up while still facing forward"
  - "they have entered retreat"
  - "each Unit is now free to solve its own dog fight"

Under the current locomotion semantics, some residual messiness remains honest
and acceptable:

- rotating pullback
- fragmented return
- collapse-like recovery once overlap is already deep

Those residuals are not a bug in wording.
They come from the fact that current locomotion still couples facing and travel
direction.

### 2. One-sentence conclusion

The smallest honest next `back_off_keep_front` slice is:

- a fleet-authorized, Unit-realized bounded give-ground behavior
- where Units reduce over-commit and reopen some space once fleet-level
  standoff is already too compressed
- while still staying below literal backward-with-front-preserved motion, below
  turn-away retirement, and below full retreat doctrine

### 3. What visible battle behavior this slice is trying to create

If later authorized, this slice should aim for all of the following:

1. Earlier reduction of needless forward overrun

- when the fronts are already too tight, front-rank Units should stop
  continuing to "win the angle" at any cost
- the line should cross less deeply before any restorative action begins

2. Deliberate reopening of some space

- once compression is real, some Units should give back a little ground instead
  of remaining nose-to-nose
- the result should be shallower overlap and less sticky first-contact welding

3. Better front readability during recovery

- recovery should still look imperfect
- but the fleet should read more like a compressed front trying to re-form, not
  like many unrelated duelists

4. Stronger return-to-line tendency after the worst compression window

- after local space opens, Units should bias back toward readable fleet-front
  coherence instead of remaining in prolonged off-axis circling

### 4. What remains explicitly out of reach

This proposal must stay honest about what current runtime semantics still cannot
do.

It does **not** claim:

1. Literal keep-front backward motion

- the runtime still writes orientation from realized heading
- and writes velocity along that same realized heading
- so it still lacks a true "face forward while translating backward" motion
  family

2. Turn-away retirement

- this slice is not a flee / disengage / break-contact doctrine
- the Unit is not being authorized to rotate away and leave the fight

3. Full retreat doctrine

- the fleet has not changed battle intent in this proposal
- this is still bounded give-ground under the current battle commitment

4. Clean parallel-sheet recovery after deep overlap already exists

- if the front is already badly interpenetrated, some rotating pullback and
  fragmented return remain structurally honest residuals

### 5. Acceptable residuals under current locomotion semantics

The proposal should explicitly accept the following as residuals that may remain
visible even in a successful bounded slice:

#### 5.1 Rotating pullback

- a Unit may need to rotate toward a space-reopening heading before it can
  create room
- so the give-ground can still read as an arc rather than a straight backward
  slide

#### 5.2 Fragmented return

- different Units see different local geometry
- some find a cleaner path to reopen space than others
- so the front may recover unevenly rather than as one perfect sheet

#### 5.3 Collapse-like recovery after already-deep overlap

- if the line has already crossed too far, the problem is no longer "do not
  cross"
- it becomes "recover from bad geometry"
- under current locomotion semantics that recovery will still show some
  rotational / fragmented behavior

### 6. Exact fleet-side authorization read

The next slice should keep fleet authorization explicit and above the Unit
layer.

The proposed authorization read is:

- bounded back-off becomes eligible only when fleet-side standoff says the
  fronts are already too compressed
- the primary fleet-side truth for that should be:
  - `battle_relation_gap_current`
- the fleet-side urgency / severity context should be:
  - `battle_brake_drive_current`
- the fleet-side coherence cap should be:
  - `battle_hold_weight_current`

Plain-language meaning:

- `battle_relation_gap_current`
  - answers:
    - "is this no longer just a local angle problem, but an actual front-gap
      compression problem?"
- `battle_brake_drive_current`
  - answers:
    - "how strongly should the fleet stop pressing and start making room?"
- `battle_hold_weight_current`
  - answers:
    - "how much should the response stay disciplined as a front-preserving
      action rather than turning into free local wandering?"

Important non-owner:

- `battle_relation_gap_raw` should **not** become the main back-off owner
- it should remain the earlier guard for:
  - "do not silently grant too much local freedom before contact geometry is
    honestly tight enough"

### 7. Exact Unit-side realization allowed

The Unit side should still realize behavior only through the existing
same-tick carrier:

- `desired_heading_xy`
- `desired_speed_scale`

Allowed Unit-side realization in this proposal:

1. Reduce over-commit

- Units may stop leaning so hard into off-axis firing opportunity once the
  fleet-side compression read says the line is too tight

2. Reopen some space

- Units may bias heading and speed so that they stop deepening overlap and
  create a modest buffer

3. Bounded restore-line tendency

- once compression is real, heading may also bias back toward readable
  fleet-front coherence
- speed may apply a stronger brake-only restraint so the recovery does not rely
  only on heading

What remains explicitly not allowed at Unit side:

- no literal keep-front backward motion claim
- no turn-away retirement
- no second target owner
- no guide-target / parallel-target semantics
- no full retreat doctrine

### 8. Variable / role discipline

This slice should only proceed if variable roles stay explicit.

#### 8.1 Early guard owner

Use:

- `battle_relation_gap_raw`

Job:

- early no-crossing / do-not-release-too-soon guard

What it should not become:

- not the full back-off authorization owner
- not the restore owner
- not the retreat owner

#### 8.2 Later restorative authorization / severity

Use:

- `battle_relation_gap_current`
- `battle_brake_drive_current`

Jobs:

- `battle_relation_gap_current`
  - persistent "line is too tight" truth
- `battle_brake_drive_current`
  - bounded severity / urgency for making room

What they should not become:

- they should not silently become a full retreat doctrine
- they should not by themselves authorize turn-away behavior

#### 8.3 Fleet-front coherence cap

Use:

- `battle_hold_weight_current`

Job:

- keep the response reading like bounded fleet-front give-ground rather than
  many Units freelancing in different directions

#### 8.4 Auxiliary localizers only

Use:

- `near_contact_gate`
- local target bearing / turn-need geometry

Jobs:

- localize which Units are actually in the problem geometry
- localize how urgent the local maneuver angle is

What they should not become:

- not strategic release owners
- not fleet-level authorization owners

### 9. Keep vs replace summary

#### 9.1 Keep

- current owner/path family
- single same-tick target source:
  - `selected_target_by_unit`
- current carrier shape:
  - `desired_heading_xy`
  - `desired_speed_scale`
- fleet-authorized / unit-realized split
- explicit separation between:
  - target selection
  - movement realization
  - combat execution

#### 9.2 Replace or rebalance

- replace the practical "keep pushing, then repair later" read with:
  - "first stop deeper over-commit once standoff is too tight, then restore"
- demote purely local geometry from practical owner of the whole response
- make speed-side restraint a real partner in reopen-space behavior rather than
  a weak afterthought

### 10. Minimal implementation shape if later authorized

If Governance later opens the slice, the minimal implementation should stay
within:

- `runtime/engine_skeleton.py`
- current same-tick Unit desire path

Preferred implementation shape:

1. keep the same carrier
2. keep the same target source
3. use fleet-side standoff / brake / hold reads as authorization and bounded
   severity context
4. use local geometry only to localize which Units need the response most
5. strengthen speed-side brake-only restraint enough that "make room" is not
   carried by heading alone
6. avoid any logic that reads like turn-away retirement

### 11. What still does not change

This proposal remains below all of the following:

- full retreat
- locomotion rewrite
- literal keep-front backward-motion capability
- second target owner
- mode system
- persistent target memory
- broad locomotion redesign
- module split

### 12. Validation posture if later authorized

If this slice is later authorized, Engineering should report with:

1. static owner/path audit
2. compile check
3. narrow smoke behind explicit experimental enablement
4. paired comparison against the current temporary working anchor
5. targeted human-readable evidence focused on:
   - shallower first-contact crossing
   - less deep early overlap
   - clearer reopen-space behavior
   - stronger return-to-line tendency
   - preserved fleet-front readability
6. explicit explanation of residual rotating / fragmented recovery

### 13. Shortest conclusion

The next honest `back_off_keep_front` slice should be read as:

- fleet-authorized bounded give-ground
- Unit-realized reopen-space and restore-line behavior
- under current locomotion semantics

It must **not** be described as:

- literal backward-with-front-preserved motion
- turn-away retirement
- or full retreat
