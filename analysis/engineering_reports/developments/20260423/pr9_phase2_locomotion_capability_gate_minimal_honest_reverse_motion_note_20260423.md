# PR9 Phase II - Locomotion Capability Gate Minimal Honest Reverse Motion Note

Date: 2026-04-23  
Scope: document-first locomotion capability note  
Status: no implementation in this note

**Line classification:** Locomotion capability line  
**Owner classification:** capability-layer clarification; no behavior-line over-claim  
**Honest claim boundary:** current locomotion can support behavior-semantic
give-ground / reopen-space / restore-line tendency, but it cannot honestly
claim literal keep-front backward motion.

## 1. Battle Read First

The current behavior-line `back_off_keep_front` can make the battle read like:

- Units stop over-committing as much
- some space is reopened
- the front tries to remain readable
- the fleet looks less like a free dog-fight cloud

But it still cannot make the battle read like:

- front-rank Units keep facing the enemy/front
- while their actual travel direction moves backward
- under a native locomotion rule

That is why current recovery still shows honest residuals:

- rotating pullback
- fragmented return
- arc-like give-ground instead of straight backpedal
- collapse-like recovery after deep overlap has already happened

This is not just a cold parameter problem. It is structural under current
locomotion semantics because facing and travel remain coupled.

## 2. What Exact Capability Is Missing?

The missing capability is:

- a native way for locomotion to realize movement opposite, or partly opposite,
  to the Unit's facing / front-preserving orientation

In plain battle language:

- the Unit needs to keep its face/front toward the battle
- while its body gives ground
- without first turning its facing into the retreat direction

Current runtime path does not have that.

Current active read in `runtime/engine_skeleton.py`:

- Unit desire supplies:
  - `desired_heading_xy`
  - `desired_speed_scale`
- locomotion combines desire / cohesion / separation / boundary into one
  `total_direction`
- `realized_heading_hat` is rotated toward that direction
- `orientation` is written from `realized_heading_hat`
- `velocity` is also written as `realized_heading_hat * step_speed`
- `step_speed` is clamped non-negative

So current semantics are:

- facing = realized travel heading
- velocity direction = realized travel heading
- speed magnitude >= 0

That means "back off" can only be approximated by changing the heading and
slowing down. It cannot literally travel backward while preserving forward
facing.

Important clarification:

- `attack_speed_backward_scale` is not reverse locomotion
- it only reduces movement allowance when the attack direction lies behind the
  current facing
- it does not create negative travel, backpedal, or facing/travel separation

## 3. Candidate Capability Comparison

### Candidate A - Signed Longitudinal Movement Relative To Facing

Plain meaning:

- locomotion may receive a signed longitudinal movement ask
- positive means travel forward along current / desired facing
- negative means travel backward while keeping facing as the facing owner

What it would enable:

- the smallest direct version of backpedal-like motion
- a Unit can preserve front-facing posture while giving ground along its own
  facing axis
- behavior-line give-ground could become visibly less rotational

What it still would not enable:

- full retreat doctrine
- arbitrary sideways strafing
- independent translation in any direction
- fleet authorization for when back-off is allowed
- clean recovery from already-deep overlap by itself

Invasiveness:

- moderate
- current `desired_speed_scale` is unsigned and clamped to `[0, 1]`
- current velocity write assumes `velocity = realized_heading_hat * step_speed`
- a signed longitudinal component would require a locomotion-level signed speed
  semantic and acceleration/deceleration handling across zero

Smallest honest next gate?

- close, but not sufficient if added alone as a hidden sign on current
  `desired_speed_scale`
- it must be explicit, because overloading `desired_speed_scale < 0` would
  silently change an existing carrier's meaning

### Candidate B - Independent Facing And Translation Carriers

Plain meaning:

- one carrier says where the Unit should face
- another carrier says where the Unit should travel
- locomotion realizes both within turn-rate, acceleration, and speed limits

What it would enable:

- literal keep-front backward motion
- sideways motion / strafing if later authorized
- clean separation of:
  - fleet front axis
  - Unit facing
  - actual velocity
- better future 3D compatibility

What it still would not enable:

- retreat authorization
- battle doctrine for when to back off
- target selection changes
- collision / overlap solution by itself

Invasiveness:

- high
- it changes the current carrier meaning more broadly
- it requires locomotion to own two realization problems, not one:
  - facing realization
  - translation realization
- it likely touches diagnostics, VIZ interpretation, and future settings
  language

Smallest honest next gate?

- no, not as the first gate
- it is the cleanest long-term direction, but bigger than the smallest honest
  experiment

### Candidate C - Explicit Reverse / Backpedal Realization Family

Plain meaning:

- locomotion keeps the existing ordinary forward realization
- but gains a small, explicit reverse/backpedal realization branch
- this branch says:
  - preserve facing toward the desired front / target-facing direction
  - allow bounded travel opposite that facing when a signed reverse ask is
    present

What it would enable:

- the first honest literal keep-front backward-motion experiment
- less rotating pullback in front-rank give-ground windows
- clearer distinction between behavior-line authorization and locomotion
  capability

What it still would not enable:

- full retreat
- turn-away retirement
- broad independent translation
- module split
- behavior-line decision ownership

Invasiveness:

- moderate
- narrower than full independent facing/translation carriers
- larger than parameter tuning
- requires a new explicit locomotion capability input rather than reuse of
  `attack_speed_backward_scale` or hidden negative `desired_speed_scale`

Smallest honest next gate?

- yes, if framed narrowly
- this is the best first experimental capability gate if Governance later
  authorizes implementation

## 4. Fleet Authorization vs Unit Realization

The owner split should not change just because a locomotion capability line is
opened.

Fleet / reference side should still own:

- fleet front axis
- standoff / hold / terminal relation truth
- higher-level movement envelope
- whether back-off or retreat is authorized
- any future retreat doctrine

Unit / locomotion side may own:

- how a permitted movement ask is physically realized
- whether facing and translation can be realized separately
- acceleration / deceleration / turn-rate limits
- signed or reverse movement realization if explicitly authorized

Locomotion capability must not silently swallow battle intent.

Plain-language boundary:

- fleet side answers "are we allowed to give ground?"
- behavior line answers "what local give-ground response is being asked?"
- locomotion answers "can the Unit physically realize that ask without turning
  its face away?"

## 5. What Is Still Out Of Scope

This note is not:

- retreat implementation
- behavior-line optimization
- target-owner redesign
- owner rewiring
- module split
- broad locomotion rewrite
- full 3D locomotion redesign
- a proposal to promote current experimental behavior-line work

This note also does not authorize:

- changing `desired_heading_xy`
- changing `desired_speed_scale`
- adding signed speed
- changing VIZ replay semantics
- changing combat behavior

It only defines the missing capability and compares the minimum honest gates.

## 6. Smallest Possible Experimental Gate If Later Authorized

Recommended smallest later gate:

- explicit reverse/backpedal realization family
- locomotion capability line only
- behind an explicit experimental enablement
- no behavior-line retuning in the same slice

Minimal carrier question:

- current carrier is not enough if kept literally:
  - `desired_heading_xy` currently acts as travel-heading desire
  - `desired_speed_scale` is unsigned
- the smallest honest addition would be a separate explicit field such as:
  - `desired_longitudinal_speed_scale`
  - or `desired_travel_longitudinal_scale`
- allowed range would need to be signed, for example `[-1.0, 1.0]`
- negative would mean bounded backward travel relative to realized facing

Facing / translation decoupling needed?

- yes, but only in a narrow form for the first gate
- full arbitrary translation-vector decoupling is not required for the first
  experiment
- the minimum is:
  - facing remains realized from desired facing / front-preserving orientation
  - longitudinal travel may be signed along that facing axis

Signed speed needed?

- yes, if the claim is literal backward travel
- otherwise the runtime still only has slower forward movement or rotational
  give-ground

New carrier needed?

- likely yes
- do not overload `desired_speed_scale`
- do not claim `attack_speed_backward_scale` already provides this

Expected first visible behavior changes if later authorized:

- front-rank Units can give ground with less rotation
- `back_off_keep_front` windows can read more like controlled backpedal and
  less like arc-turn recovery
- fleet front readability should improve during restore-space windows
- some fragmented recovery will still remain when overlap is already deep

What should not change from this gate alone:

- retreat authorization
- target selection
- combat execution
- fleet-side standoff ownership
- mode system
- broad locomotion architecture

## 7. Recommended Next Governance Question

Before implementation, Governance should decide whether the first locomotion
capability experiment should be:

- `signed_longitudinal_backpedal`

with this narrow claim:

- "locomotion can realize bounded backward travel along the Unit's facing axis
  while preserving front-facing orientation"

and this explicit non-claim:

- "this is not retreat, not turn-away retirement, and not a full
  facing/translation decoupling system."
