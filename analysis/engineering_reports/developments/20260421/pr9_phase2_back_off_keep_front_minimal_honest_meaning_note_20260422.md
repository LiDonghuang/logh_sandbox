## PR9 Phase II - `back_off_keep_front` Minimal Honest Meaning Note

Date: 2026-04-22  
Scope: document-only concept clarification for Human + Governance  
Status: no implementation in this note

**Line classification:** Behavior line  
**Owner classification:** fleet-authorized / unit-realized  
**Honest claim boundary:** this note may claim bounded give-ground / space reopening under current runtime semantics; it may not claim literal keep-front backward motion, full retreat doctrine, or new locomotion capability

### 1. Battle read first

If Human asks for "`back_off_keep_front`" in the current runtime, the most
honest first answer is not a formula answer.

It is a battle-picture answer.

The smallest honest version should look like this:

- front-rank Units stop pushing through so hard once the line is already too
  tight
- some Units give back a little space instead of continuing the dog-fight
- the fleet can still read broadly as a fleet front, not as many free duels
- but the withdrawal is still messy in a bounded, physical way:
  - Units arc
  - Units rotate while creating space
  - Units may pull back unevenly

In other words:

- acceptable read:
  - "they are easing off and reopening space without fully turning the whole
    fleet into a retreat"
- unacceptable over-claim:
  - "they are literally flying backward while still facing the enemy the whole
    time"

### 2. One-sentence conclusion

Under the current locomotion semantics, the minimal honest meaning of
`back_off_keep_front` is:

- a **behavior-semantic** back-off
- where Units reduce over-commit, reopen some space, and help preserve overall
  fleet-front readability
- but **not** a literal kinematic ability to keep facing forward while moving
  backward

### 3. What the current runtime actually does

Only after the battle read do we need the motion semantics.

The active low-level movement path is currently:

- upstream produces:
  - `desired_heading_xy`
  - `desired_speed_scale`
- low-level locomotion then computes:
  - `desired_heading_hat`
  - `realized_heading_hat`
- and finally writes:
  - `orientation_vector = realized_heading_hat`
  - `velocity = realized_heading_hat * step_speed`
- with `step_speed >= 0`

Active code path:

- `runtime/engine_skeleton.py`
- `integrate_movement(...)`

Important practical consequence:

- facing and travel direction are still coupled
- speed is non-negative
- so the runtime has no native "face forward, translate backward" expression

### 4. What the current semantics can do

The current runtime can honestly support these `back_off_keep_front` behaviors:

1. Stop pushing deeper into overlap

- if the line is already too compressed, Units can reduce forward commitment
- this can help the front stop overrunning as aggressively

2. Reopen some space

- Units can bias movement away from the worst local over-commit
- this can create a small buffer instead of endless nose-to-nose sticking

3. Keep overall fleet-front readability better than pure free dog-fight

- fleet-side front and standoff signals still exist above the Unit layer
- so local motion can remain bounded inside a broader fleet picture

4. Produce a readable "give ground a little" battle impression

- the Human can read:
  - "they are backing off a bit"
- even though the literal motion is still realized through turn + forward
  travel rather than true reverse thrust

### 5. What the current semantics cannot do

The current runtime cannot honestly claim these behaviors:

1. Literal keep-front backward motion

- a Unit cannot presently keep its nose pointed forward and translate backward
  in the same tick under a native motion rule

2. Clean straight-line frontal withdrawal

- because travel follows realized heading, a Unit that wants to create space
  must usually rotate some amount first

3. Perfect front preservation during local back-off

- once local geometry is messy, Units will not all back out in one perfectly
  parallel sheet
- some will turn earlier, some later

4. Guaranteed non-rotational recovery after overlap already exists

- once the fronts have already interpenetrated, recovery will often show curved
  paths, rotating return, and uneven re-spacing

### 6. Which residual artifacts are currently unavoidable

Under the present semantics, the following residuals are not just "bad tuning."
They are structurally hard to avoid once overlap is already in the system.

#### 6.1 Rotating pullback

Why it happens:

- the Unit must rotate toward a heading that opens space
- then it travels along that heading

Battle read:

- what Human sees is not a clean straight backward slide
- it is an arcing or rotating back-out

#### 6.2 Fragmented return / broken-line recovery

Why it happens:

- local geometry differs from Unit to Unit
- some Units have a cleaner lane to reopen space than others
- separation, cohesion, and turn limits all apply per Unit

Battle read:

- the front can partially fracture before becoming readable again

#### 6.3 Rotational collapse after overrun is already deep

Why it happens:

- if the line has already crossed too far, the system is no longer solving a
  "don't cross" problem
- it is solving a "recover from a bad geometry" problem
- with forward-travel-only locomotion, that recovery usually manifests as turn
  + pullback rather than flat reverse

Battle read:

- Human can still see:
  - rotation
  - curling
  - uneven collapse and re-formation

These are not necessarily signs that the back-off idea is meaningless.
They are signs that the current motion semantics only support a bounded,
behavior-level version of it.

### 7. What is missing for literal keep-front backward motion

If Governance wants the phrase `back_off_keep_front` to mean its literal
kinematic meaning, the smallest missing locomotion capability is:

- some explicit decoupling between facing and travel direction

The minimum honest additions would be one of these:

1. Signed longitudinal movement relative to facing

- a Unit can face one way
- but receive a negative forward-speed command relative to that facing

2. Independent facing and translation carriers

- facing command:
  - where the ship/group is pointed
- translation command:
  - where the ship/group is actually moving

3. Explicit reverse / backpedal realization support in low-level locomotion

- not merely lower speed
- not merely turn more slowly
- but an actual reverse-motion family with bounded reverse authority

Without one of those, "keep front while moving backward" is only a verbal
description, not a truthful runtime capability.

### 8. Important clarification about existing names

There is already an active setting name:

- `runtime.movement.v4a.engagement.attack_speed_backward_scale`

This does **not** mean the runtime already supports literal backward travel
while holding facing.

What it actually does:

- it scales the allowed movement speed when the attack direction lies behind the
  Unit's current facing
- but the realized motion still follows realized heading

So this is:

- a speed-budget modifier

not:

- a true reverse-thrust / backward-translation capability

### 9. Final distinction Governance should carry forward

Governance should keep these two meanings explicitly separate.

#### A. Behavior-semantic `back_off_keep_front`

Meaning:

- Units help reopen space
- the fleet still reads broadly frontally coherent
- local motion stays bounded under fleet-side discipline

What it permits:

- modest peel-away
- modest give-ground
- readable restore-line tendency
- some unavoidable arc / rotation while doing so

This meaning can likely stay within the current maneuver-envelope / restore-line
family.

#### B. Literal kinematic keep-front backward motion

Meaning:

- the Unit keeps facing forward
- while its actual travel vector goes backward

What it requires:

- new low-level locomotion semantics
- or new decoupled facing vs travel capability

This meaning is **not** already present in the runtime and should not be
treated as a small parameter or local-desire extension.

### 10. Shortest conclusion

The minimal honest current meaning of `back_off_keep_front` is:

- "bounded give-ground while trying to preserve a readable fleet front"

It is **not**:

- "literal backward motion with forward-facing posture preserved"

If Governance wants the second meaning, that is a locomotion-capability
question, not just a bounded battle-behavior slice.
