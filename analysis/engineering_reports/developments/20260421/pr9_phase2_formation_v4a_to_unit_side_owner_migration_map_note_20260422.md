## PR9 Phase II - Formation / v4a to Unit-Side Owner Migration Map Note

Date: 2026-04-22  
Scope: document-only owner-map clarification for Human + Governance  
Status: no implementation in this note

### 1. Battle read first

Before talking about owner language, the practical question is:

- when we watch the battle, which things are still "the fleet deciding the
  battle picture"
- and which things are already "each Unit locally realizing that picture"

This matters because the battle problems Human is watching are visible ones:

- do front-rank Units cross too early
- do Units actively make space when the line is too tight
- does the fleet still read like a readable front
- does recovery unavoidably look like rotation, pullback, and partial collapse

If we call something "formation" or "v4a" when it is already mostly a Unit-side
decision, we start misreading where the battle behavior is really coming from.

If we call something "unit-local" when it still owns fleet-front shape or
standoff truth, we lose the higher-level battle discipline that keeps the fleet
readable.

### 2. One-sentence conclusion

The current active path already has real Unit-side owners for:

- same-tick target identity
- same-tick unit desire
- low-level per-unit maneuver realization

But the fleet/reference side must still own:

- front axis
- standoff relation
- hold / terminal reference surface
- higher-level movement envelope

The main current migration issue is not that the runtime still lacks Unit-side
owners.
It is that several active per-unit mechanisms still live under older
`formation` / `v4a` names and surfaces even though their practical job has
shifted toward unit-local maneuver realization.

### 3. Mechanisms that already behave like Unit-side owners

These mechanisms are already functionally Unit-side in the active path.

#### 3.1 Same-tick target identity

Active path:

- `runtime/engine_skeleton.py`
- `_compute_unit_intent_target_by_unit(...)`
- `_select_targets_same_tick(...)`
- `resolve_combat(...)`

Battle read:

- this is already "which enemy this Unit is working on right now"
- not a fleet-front reference-surface question

Owner judgment:

- already Unit-side owner

Why:

- it is per attacker
- it exists same tick
- it feeds Unit-local maneuver and then combat execution

#### 3.2 Same-tick unit desire

Active path:

- `runtime/engine_skeleton.py`
- `_compute_unit_desire_by_unit(...)`
- carrier:
  - `desired_heading_xy`
  - `desired_speed_scale`

Battle read:

- this is already the Unit's local maneuver ask:
  - "which way should I bias now"
  - "how much should I restrain speed now"

Owner judgment:

- already Unit-side owner

Why:

- it is computed per Unit
- it is consumed per Unit
- it directly affects local peel-out, space-making, and return-to-line behavior

#### 3.3 Low-level locomotion realization

Active path:

- `runtime/engine_skeleton.py`
- `integrate_movement(...)`

Battle read:

- this is where each Unit actually turns, accelerates, decelerates, separates,
  and moves

Owner judgment:

- already Unit-side owner

Why:

- final `orientation_vector`
- final `velocity`
- final per-Unit displacement
  are all realized here per Unit

#### 3.4 Attack-direction-aware per-unit speed budgeting

Active path:

- `runtime/engine_skeleton.py`
- `_apply_v4a_transition_speed_realization(...)`

Battle read:

- even though this still sits under a `v4a transition` function name, it is
  already deciding a per-Unit locomotion budget based on:
  - selected target
  - current Unit facing
  - attack direction

Owner judgment:

- functionally Unit-side owner

Why:

- it writes per-Unit `max_speed`
- the read is local to each Unit's target / facing geometry

### 4. Mechanisms that must stay fleet/reference side

These should **not** be migrated into Unit-side ownership on the current line.

#### 4.1 Fleet front axis / coarse-body heading

Active path:

- `state.coarse_body_heading_current`
- `runtime/engine_skeleton.py`
- `_prepare_v4a_bridge_state(...)`

Battle read:

- this is still what lets the fleet read like one fleet front rather than many
  unrelated dog-fighters

Owner judgment:

- must remain fleet/reference side

#### 4.2 Reference surface / expected slot world

Active path:

- `_resolve_v4a_reference_surface(...)`
- `expected_slot_offsets_local`
- morphology axis / center / extent state

Battle read:

- this is still the higher-level answer to:
  - what shape the fleet is trying to preserve
  - where Units are expected to sit relative to the fleet body

Owner judgment:

- must remain fleet/reference side

#### 4.3 Battle relation / standoff envelope

Active path:

- `battle_relation_gap_raw`
- `battle_relation_gap_current`
- `battle_brake_drive_current`
- `battle_hold_weight_current`
- `battle_approach_drive_current`

Battle read:

- these are still fleet-vs-fleet battle-context answers:
  - is there still room between the fronts
  - is the line too compressed
  - should the fleet still push, hold, or brake

Owner judgment:

- must remain fleet/reference side

#### 4.4 Hold / terminal surface

Active path:

- `formation_hold_*`
- `formation_terminal_*`

Battle read:

- these still decide whether the fleet is holding shape, freezing advance, or
  entering a terminal surface condition

Owner judgment:

- must remain fleet/reference side

### 5. Mechanisms in transitional state

These are the important "name still looks formation/v4a, but the practical job
has shifted" cases.

#### 5.1 `_apply_v4a_transition_speed_realization(...)`

Current name:

- sounds like a fleet-transition helper

Current practical job:

- per-Unit speed shaping
- per-Unit selected-target read
- per-Unit facing-vs-attack-direction read

Battle consequence:

- this function materially affects whether Units press in, hesitate, or open
  space in local contact geometry

Current owner judgment:

- transitional

Why transitional:

- the logic is already unit-local in behavior
- but the naming still frames it as a `v4a transition` subfunction

Recommended next minimal action:

- **change owner language**

Why not wiring first:

- the active wiring is already truthful enough for the current slice
- the main mismatch is conceptual labeling

#### 5.2 `runtime.movement.v4a.engagement.*` speed surfaces

Current surfaces:

- `engaged_speed_scale`
- `attack_speed_lateral_scale`
- `attack_speed_backward_scale`

Current practical job:

- per-Unit maneuver-speed permission in local combat geometry

Battle consequence:

- these directly influence whether Units keep pressing, slide laterally, or
  reduce forward aggression under local attack geometry

Current owner judgment:

- transitional

Why transitional:

- the setting family still sits under `runtime.movement.v4a.engagement`
- but the behavior it owns is already closer to unit-local maneuver /
  locomotion realization than to fleet reference shaping

Recommended next minimal action:

- **settings/surface classification change**

Why:

- owner language alone is probably not enough here
- the setting surface itself now points Human toward the wrong layer
- but the wiring can stay as-is for now

#### 5.3 Near-contact speed stabilization inside the bridge line

Current surfaces:

- `battle_near_contact_internal_stability_blend`
- `battle_near_contact_speed_relaxation`

Current practical job:

- they still read fleet battle context
- but they end up smoothing per-Unit speed budgets

Battle consequence:

- they shape how strongly Units keep individual speed freedom once contact is
  active

Current owner judgment:

- transitional bridge

Why transitional:

- they are not purely fleet-side doctrine anymore
- but they are also not standalone Unit-side decision owners
- they are bridge-side fleet-context-to-unit-speed carriers

Recommended next minimal action:

- **change owner language**

Why:

- calling them pure battle/fleet logic now is misleading
- but moving them physically or rewiring them would be too large for the
  present phase

### 6. Mechanisms that look formation-like but should stay as carriers, not be "migrated"

These are worth naming so they are not over-migrated by accident.

#### 6.1 `formation_hold_reference_max_speed_by_unit`

Current practical job:

- stores per-Unit reference speeds while fleet hold is active

Owner judgment:

- carrier only

Why:

- it supports a fleet hold state
- it is not itself a new Unit-side behavior owner

Recommended next minimal action:

- **owner language only**
  - call it a hold-state carrier, not a Unit-side doctrine owner

#### 6.2 `transition_reference_max_speed_by_unit`

Current practical job:

- stores per-Unit reference max-speed values used by transition realization

Owner judgment:

- carrier only

Why:

- it supports a now-unit-local speed-shaping path
- but it is not itself the thing deciding battle behavior

Recommended next minimal action:

- **owner language only**
  - describe it as a transition carrier

### 7. Recommended next-action map

#### 7.1 Only change owner language

Recommended for:

- `_apply_v4a_transition_speed_realization(...)`
- near-contact speed-stability bridge scalars
- `formation_hold_reference_max_speed_by_unit`
- `transition_reference_max_speed_by_unit`

Reason:

- the active runtime wiring is already basically correct
- the current main problem is conceptual mislabeling

#### 7.2 Change settings/surface classification

Recommended for:

- `runtime.movement.v4a.engagement.*`

Reason:

- these settings now guide per-Unit maneuver-speed realization more than fleet
  reference shaping
- the surface category itself is now misleading

#### 7.3 Wiring change is **not yet** the smallest next move

Current engineering judgment:

- no immediate wiring migration is required for the items above
- the current Phase II mainline still benefits from keeping the active path
  stable while clarifying owner language first

### 8. Shortest conclusion

The current active path already has real Unit-side owners for:

- target identity
- unit desire
- low-level locomotion realization

The fleet/reference side still must own:

- fleet front
- reference surface
- standoff relation
- hold / terminal states

The main migration problem now is transitional labeling:

- some per-Unit maneuver mechanisms still live under older `formation` / `v4a`
  names and settings even though their practical battle job has already become
  unit-local or bridge-local

So the next minimal move is mostly:

- clarify owner language first
- selectively reclassify misleading settings surfaces
- and avoid opening broad rewiring until Governance explicitly asks for it
