## PR9 Phase II - Local Desire Standoff-Aware Envelope And Restraint Rebalance Bounded Implementation Proposal

Date: 2026-04-20  
Scope: proposal only; no runtime implementation in this note  
Status: document-first proposal for Human + Governance review

### 1. One-sentence conclusion

If a next experimental slice is later authorized behind the existing temporary
freeze switch, the most honest bounded move is to keep the current
`local_desire` layer/carrier and single target source, but replace the current
shared proximity-led live family with a standoff-aware envelope on
heading-side plus a genuinely live, later, brake-only restraint on speed-side.

### 2. Plain-language battle read

For the current `1 unit = 100 ships` abstraction, a single Unit should be
allowed only a modest amount of local freedom:

- it may lean a little out of the coarse line to improve a local firing angle
- it may drift back toward the line when that local opportunity is no longer
  worth taking
- it may slow down locally to avoid pushing too deep through a front that
  should still read as a fleet front

What must remain under higher-level fleet / formation discipline:

- the fleet still owns the broad advance direction
- the fleet still owns the readable front
- local behavior must not make the battle read like many independent dog fights

Acceptable peel-out / return-to-line:

- a few front units slightly edge outward near contact
- they do not run far ahead of the body
- they return without the whole front losing its readable line

Unacceptable behavior:

- units peeling so far that both sides behave like many free-flying duelists
- front-line overrun where first contact immediately produces deep overlap
- persistent rotational collapse where the line dissolves into spinning,
  interpenetrating clusters

Shortest human read:

- local_desire may add small local shaping
- it may not take over battle posture from the fleet body

### 3. Exact owner/path to change

Only this owner/path would change if later authorized:

- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1662>)
  - `EngineTickSkeleton._compute_unit_desire_by_unit(...)`

The proposal does **not** change:

- target-selection ownership
- `resolve_combat(...)` ownership
- locomotion-family ownership
- `local_desire` carrier shape
- single same-tick target source
- maintained default switch posture

Maintained default remains:

- `runtime.physical.local_desire.experimental_signal_read_realignment_enabled = false`

This proposal is only for the `switch = true` experimental branch if a future
slice is explicitly authorized.

### 4. Heading-side plan

#### 4.1 Proposed primary read

Heading-side should remain real, but it should stop being opened mainly by raw
proximity. The proposed primary read is:

- off-axis opportunity:
  - fleet front -> selected target bearing
- plus one standoff-safe gate:
  - primarily `battle_relation_gap_current`

#### 4.2 Why this is the right bounded correction

Current frozen experimental line made heading-side real by using:

- `near_contact_gate`
- `front_bearing_need`

That succeeded in revealing the seam, but it also allowed heading-side peel-out
to stay too live when the fleets were already too close. The problem is not
that off-axis opportunity is meaningless. The problem is that opportunity is
currently granted without a real "is this still a safe fleet-level relation?"
envelope.

`battle_relation_gap_current` is the best first candidate for that envelope
because it already encodes whether the fleet relation is:

- still outside the target strip
- roughly in the intended standoff band
- already too close / overlapping

Engineering recommendation:

- heading-side should read off-axis opportunity
- but the final heading bias should be opened only when a transformed,
  standoff-safe read of `battle_relation_gap_current` says the fleet relation
  still has room for bounded local deviation

#### 4.3 Near-contact role

`near_contact_gate` should not remain the shared primary multiplier.

Proposed role after rebalance:

- keep it only as a secondary auxiliary limiter
- use it to stop heading-side effect from showing far outside contact context
- do **not** let it be the main semantic controller

### 5. Speed-side plan

#### 5.1 Proposed primary read

Speed-side should remain:

- later
- stronger than today
- brake-only

Its primary geometry read should remain:

- unit facing -> selected target bearing

But it should no longer rely mainly on that geometry plus raw near-contact
alone. It should be enveloped by later battle restraint context, with
`battle_hold_weight_current` as the first scalar to assess.

#### 5.2 Why speed-side should stay on the single target source

No second target source is needed here.

Reason:

- speed-side is not deciding "who to engage"
- it is only deciding "how much to suppress local over-commit while still
  pursuing the already selected target"

That means the current single source:

- `selected_target_by_unit`

is still sufficient for speed-side geometry, as long as a later fleet-context
restraint envelope is added around it.

#### 5.3 Intended behavioral role

Speed-side should become the real restraint channel that the current frozen wave
never fully achieved.

Desired battle read:

- a unit may still start to peel a little on heading
- but when the battle relation is already tight, speed should help stop that
  local motion from turning into deep overrun
- the result should be less front overlap, less rotational collapse, and a
  stronger return-to-line tendency

### 6. Coupling audit for reused battle-context signals

This section is mandatory because the proposal intentionally reuses battle
bundle scalars already present on the active path.

#### 6.1 Candidate scalar: `battle_relation_gap_current`

What it is:

- smoothed current fleet relation gap relative to the target front-strip gap
- written into the battle bundle at
  [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:2473>)

Where it is already used today:

- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1369>)
- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1376>)

Current active role:

- when `battle_relation_gap_current <= 0.0`, transition advance share is forced
  toward full advance handling rather than heading-led projection
- this already affects coarse movement command realization before
  `local_desire`

Coupling risk if reused inside `local_desire`:

- duplicated effect:
  - the same fleet relation scalar would affect both coarse movement bridge
    behavior and local heading bias
- hidden cross-stage amplification:
  - if reused raw, a close / overlap condition could simultaneously alter
    movement command handling and local peel-out gating
- semantic mismatch:
  - raw relation gap is a fleet relation measure, not a unit-local opportunity
    measure
- one variable carrying too many jobs:
  - relation gap would be asked to speak both for fleet standoff and local
    maneuver permission

Engineering read:

- reuse is still acceptable only if bounded and transformed
- recommendation:
  - do **not** reuse raw `battle_relation_gap_current` as a direct gain term
  - use it only as a standoff-safe envelope / permission gate on heading-side

Why this is still reasonable:

- the scalar's meaning aligns with "is there room for local deviation?"
- the proposal uses it as a limiter, not as another drive magnitude

#### 6.2 Candidate scalar: `battle_hold_weight_current`

What it is:

- smoothed fleet-side hold pressure near the intended relation band
- written into the battle bundle at
  [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:2496>)

Where it is already used today:

- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1483>)

Current active role:

- it feeds `near_contact_stability` inside
  `_apply_v4a_transition_speed_realization(...)`
- that already relaxes:
  - `forward_transport_speed_scale`
  - `shape_speed_scale`

Coupling risk if reused inside `local_desire`:

- duplicated effect:
  - the same scalar would shape speed behavior once in transition-speed
    realization and again in local_desire speed restraint
- hidden cross-stage amplification:
  - hold pressure might become too sticky if both stages push toward stability
    in the same window
- semantic mismatch:
  - hold weight is fleet stability context, not direct unit-local turn burden
- one variable carrying too many jobs:
  - it could become both a fleet hold smoother and a local brake trigger

Engineering read:

- reuse is possible, but riskier than `battle_relation_gap_current`
- recommendation:
  - if used, do not use it raw as a full brake multiplier
  - use it only as a later restraint envelope around the existing
    unit-facing-to-target geometry

Why this may still be acceptable:

- its semantics line up with "stability should matter more now"
- that is exactly the missing piece on speed-side

Current recommendation on coupling risk:

- `battle_relation_gap_current` is the better primary candidate for
  heading-side gating
- `battle_hold_weight_current` is the better secondary candidate for
  speed-side restraint
- both should be reused only through bounded reinterpretation, not raw direct
  multiplication

#### 6.3 Mentioned but not promoted in this proposal

Other existing bundle scalars that exist but are not proposed as primary inputs
for this slice:

- `battle_brake_drive_current`
- `engagement_geometry_active_current`
- `front_reorientation_weight_current`

Engineering reason for not promoting them first:

- they are useful context
- but they are either too downstream, too coarse, or too close to already
  derived behavior pressure
- promoting them first would raise coupling complexity faster than needed for
  this bounded slice

### 7. Keep / replace summary

Keep:

- `local_desire` layer
- `local_desire` carrier shape
- single same-tick target source
- split between heading-side and speed-side channels
- maintained default with the temporary freeze switch `OFF`

Replace:

- current frozen experimental heading-side primary family:
  - replace raw proximity-led permission with off-axis opportunity plus a
    standoff-safe envelope
- current weak speed-side read:
  - replace nearly inert brake behavior with later, bounded restraint that is
    actually able to resist overrun
- current role of raw `near_contact_gate`:
  - demote from shared main multiplier to secondary limiter only

### 8. Validation posture if later authorized

If a later experimental slice is explicitly authorized, validation should be:

1. static owner/path audit
2. compile check
3. narrow smoke with switch `true`
4. paired comparison against the current temporary working-anchor baselines
5. targeted human-readable evidence focused on:
   - heading-side peel-out becoming more standoff-aware
   - speed-side actually suppressing overrun / rotational collapse
   - fewer first-contact deep overlaps
6. explicit drift explanation before any further slice proposal

Suggested human-readable checks:

- `battle_36v36` first-contact window:
  - do front rows still overrun and cross too deeply?
- `battle_36v36` mid-fight:
  - does the fight read like fleet fronts with local shaping, or like free dog
    fights?
- `battle_36v36` return phase:
  - do units recover line readability without strong rotational collapse?

### 9. Short engineering recommendation

If Human + Governance want the smallest next bounded direction, the proposal
should be read as:

- keep the layer
- keep the carrier
- keep the single target source
- keep maintained default frozen behind the switch
- if one more experimental slice is later allowed:
  - heading-side should gain a standoff-aware envelope using transformed
    `battle_relation_gap_current`
  - speed-side should become a real later brake using bounded reuse of
    `battle_hold_weight_current`
  - raw `near_contact_gate` should stop being the shared primary multiplier
