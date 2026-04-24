## PR9 Phase II - Unit Local Maneuver Envelope Mechanism-Variable Misread Diagnostic Addendum

Date: 2026-04-21  
Scope: document-only diagnostic addendum for Human + Governance  
Status: no new implementation in this note

### 1. One-sentence conclusion

The main problem in the current experimental `local_desire` branch is not
primarily that some HUD indicators are confusing; it is that several active
controller inputs are being asked to do the wrong job inside
`runtime/engine_skeleton.py`, so the mechanism releases local maneuver too late,
re-opens it at the wrong moment, and then tries to repair the damage with a
weaker restorative path.

### 2. Companion context

This note is a companion addendum to:

- `analysis/engineering_reports/developments/20260421/pr9_phase2_unit_local_maneuver_envelope_precontact_nocrossing_and_standoff_violation_response_bounded_implementation_report_20260421.md`

It should be read as:

- a diagnosis of which active mechanism variables are currently misread or
  overburdened
- a clarification of why Human-observed crossing / overlap / dog-fight
  persistence still happens even after the bounded maneuver-envelope slice

It should **not** be read as:

- a new implementation proposal
- a claim that the `local_desire` layer/carrier should be removed
- a mode / retreat / locomotion-rewrite recommendation

### 3. Plain-language battle read first

What Human is objecting to is not merely "the debug block looks odd."

The real battle read is:

- at first contact, front-rank Units are still allowed to push through and
  overlap too deeply
- after that, local maneuver remains too free for too long
- the restore path exists, but it arrives after the line is already broken
- the result is prolonged dog-fight behavior, broken fleet readability, and
  late rotational collapse / pullback patterns

That means the core problem is upstream in the active control variables:

- which quantities are allowed to release heading freedom
- which quantities are allowed to suppress speed
- which quantities are treated as "contact is mature enough now"
- which quantities are treated as "crossing is still forbidden"

### 4. Active owner/path under diagnosis

Current active code path:

- `runtime/engine_skeleton.py`
- `EngineTickSkeleton._compute_unit_desire_by_unit(...)`

Relevant current controller variables on the active path:

- `engagement_geometry_active_current`
- `contact_maturity_gate`
- `precontact_room_gate`
- `precontact_nocrossing_permission`
- `near_contact_gate`
- `battle_relation_gap_current`
- `standoff_envelope`
- `relation_violation_severity`
- `battle_hold_weight_current`
- `battle_brake_drive_current`

Current output path remains:

- `desired_heading_xy`
- `desired_speed_scale`

This note is about the variables that feed those outputs, not about viewer-only
presentation.

### 5. Main diagnosis: which variables are currently doing the wrong job

#### 5.1 `engagement_geometry_active_current` is the wrong source for "contact maturity"

Current code builds:

- `contact_maturity_gate = smoothstep01((engagement_geometry_active_current - 0.96) / (0.999 - 0.96))`

Problem:

- `engagement_geometry_active_current` is a front-strip / engagement-activation
  signal
- it tells us that opposing bodies are geometrically engaged
- it does **not** tell us that local crossing is now safe to relax
- it also does **not** tell us that fleet-level hold has remained intact

So the variable is being used for the wrong role.

It is currently acting as:

- the release owner for "precontact no-crossing may now relax"

But semantically it only supports:

- "the fleets are geometrically involved"

Those are not the same question.

Observed consequence in `battle_36v36`:

- real broad-front crossing occurs at about `tick 70`
- `ct_m` only begins to move there, and is still near zero
- then it rises while overlap is already worsening

That means the branch is not failing because the number is visually ugly; it is
failing because the wrong upstream signal owns the release decision.

#### 5.2 `precontact_nocrossing_permission` is not a true no-crossing variable

Current code builds:

- `precontact_nocrossing_permission = contact_maturity_gate + ((1 - contact_maturity_gate) * precontact_room_gate)`

Problem:

- this blends two different semantics into one control variable:
  - "is there still room left?"
  - "has contact matured enough that we may relax?"
- once room collapses, the variable falls toward `contact_maturity_gate`
- later, as `contact_maturity_gate` rises, the same variable rises again

So this variable is not actually representing:

- "crossing should still be suppressed"

It is representing:

- "combined controller permission after mixing room-left and maturity-release"

That is the wrong variable to feed directly into heading-side freedom.

Observed consequence:

- around first crossing, `nx_p` can drop sharply
- then, even while overlap worsens, it rises again
- that means the active controller is re-opening permission while the battle
  still looks structurally wrong

This is a mechanism-variable problem, not a HUD-label problem.

#### 5.3 `near_contact_gate` still has too much direct authority

Current code still gives `near_contact_gate` direct weight in both channels:

- heading-side through `heading_proximity_context`
- speed-side through `geometry_speed_response`

Current source:

- `near_contact_gate` is driven purely by `attack_distance`
- with maintained `attack_range = 20.0`
- current activation window is:
  - start near `7.0`
  - full near `4.0`

Problem:

- this is a unit-to-selected-target distance read
- it is not a fleet-level hold / standoff permission read
- when Units get close to their selected targets, this variable pushes local
  behavior harder even if fleet-level discipline should still dominate

So raw target proximity is still too close to the mechanism core.

This is exactly the kind of variable that can make:

- heading bias feel locally urgent
- speed restraint arrive too late
- Units chase immediate geometry instead of preserving the fleet front

#### 5.4 `battle_relation_gap_current` is carrying too many jobs at once

The current branch reuses the same relation-gap family for all of these:

- `precontact_room_gate`
- `standoff_envelope`
- `relation_violation_severity`
- `battle_brake_drive_current`
- `battle_hold_weight_current`

This is not automatically wrong, but in the current branch it means one scalar
family is being stretched across several different controller roles:

- room-left / release logic
- permission envelope
- violation severity
- restorative brake context
- hold context

That creates two risks:

- semantic collapse
  - one number family is being asked to answer too many different questions
- cross-stage amplification
  - the same battle relation read re-enters heading and speed through multiple
    partially overlapping paths

So the problem is not merely that `battle_relation_gap_current` exists.
The problem is that it is currently overburdened inside the experimental local
controller.

#### 5.5 `battle_brake_drive_current` and `battle_hold_weight_current` are restorative context, not early guard

Current speed-side restraint uses:

- `speed_restraint_context = max(battle_hold_weight_current, battle_brake_drive_current)`
- plus additional violation-side terms

Problem:

- both of these are already downstream battle-context quantities
- both are relaxed / smoothed fleet-level responses
- they are appropriate as late restorative context
- they are not strong candidates for the first guard against early crossing

Observed consequence:

- by the time `brk` is visibly meaningful, the battle is already deep in
  contact
- the speed-side response becomes a repair path, not a prevent path

So the present branch still has the classic control-order problem:

- early freedom is controlled by the wrong variables
- later repair is asked to compensate after the line is already broken

### 6. Evidence from the observed `36v36` window

Observed window:

- maintained `battle_36v36`
- explicit experimental enablement
- focused review on `tick 61..80`

Measured first geometry crossing:

- `first_neg_strip_gap_tick = 70`
- `first_neg_front_gap_tick = 70`

Representative values:

| tick | in_contact | front_gap | relation_gap | eng_act | ct_m | nx_p | brk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `61` | `6` | `17.052` | `0.859` | `0.784` | `0.000` | `1.000` | `0.000` |
| `65` | `72` | `9.051` | `0.538` | `0.902` | `0.000` | `1.000` | `0.000` |
| `69` | `72` | `1.155` | `0.144` | `0.956` | `0.000` | `0.583` | `0.083` |
| `70` | `72` | `-0.383` | `0.041` | `0.964` | `0.026` | `0.026` | `0.141` |
| `75` | `68` | `-2.391` | `-0.359` | `0.987` | `0.759` | `0.759` | `0.418` |

What this shows mechanically:

- the line is already being compressed hard by `tick 65`
- by `tick 69`, there is almost no room left
- at `tick 70`, real crossing has already happened
- yet the maturity-release path has barely started
- after that, the maturity / permission family rises while overlap worsens
- the brake path also rises only after the violation is already underway

So the observed failure matches the control structure:

- wrong release owner
- mixed permission variable
- proximity still too close to the drive path
- restorative variables arriving later than the violation they are supposed to
  contain

### 7. What the `NaN` issue does and does not mean

Human also observed that both `ct_m` and `nx_p` can become `NaN`.

That is real, but it is a **secondary** problem.

What it means:

- the current debug export owner for those values is not truly fleet-level
- they are initialized per fleet as `NaN`
- then only written when a unit actually enters the selected-target local branch

So a `NaN` tick tells us:

- the exported debug surface for these values is not robust

What it does **not** mean:

- that the main battle-behavior problem is merely a viewer bug

The primary mechanism diagnosis stands even if the export path were perfect:

- the wrong variables currently own release / permission / restraint roles

### 8. Keep / retire / redesign judgment

#### Keep

- `local_desire` layer/carrier
- single same-tick target source
- split between heading-side and speed-side outputs
- presence of a restorative speed-side path

#### Retire from active control ownership

- treating `engagement_geometry_active_current` as the owner of "contact is now
  mature enough to relax no-crossing"
- treating `precontact_nocrossing_permission` as if it were a true
  no-crossing-safe control variable
- letting `near_contact_gate` remain a strong direct multiplier in both
  channels

#### Redesign

- the precontact release logic
- the variable that represents "early crossing is still forbidden"
- the split between:
  - early envelope / permission
  - late violation severity
  - restorative brake context

### 9. Short governance-facing conclusion

The current issue should be read as a mechanism-variable misread problem.

More concretely:

- `engagement_geometry_active_current` is the wrong owner for maturity-release
- `precontact_nocrossing_permission` is an overloaded mixed-permission variable,
  not a true no-crossing state
- `near_contact_gate` still has too much direct authority
- the `battle_relation_gap_current` family is overburdened across too many jobs
- `battle_brake_drive_current` / `battle_hold_weight_current` remain useful as
  restorative context, but they arrive too late to be the first guard

So the next discussion should not be framed mainly as:

- "which HUD indicator is misleading?"

It should be framed as:

- "which variables are allowed to own early local maneuver release, and which
  variables are only allowed to provide later restorative context?"
