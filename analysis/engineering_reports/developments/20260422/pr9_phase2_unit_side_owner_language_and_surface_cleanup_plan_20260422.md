## PR9 Phase II - Unit-Side Owner Language and Settings-Surface Cleanup Plan

Date: 2026-04-22  
Scope: document-first owner-language / settings-surface cleanup plan for Human + Governance  
Status: no runtime wiring change in this note

**Line classification:** Owner-language / surface-cleanup line  
**Owner classification:** mixed-layer map clarification; no runtime rewiring proposed in this note  
**Honest claim boundary:** this note may clarify active owner language and settings/surface classification; it may not claim runtime rewiring, module split, or new mechanism ownership already exists beyond the verified active path

### 1. Battle read first

This cleanup plan is not about naming for its own sake.

It matters because the battle picture has already changed:

- some things Human sees on screen are now clearly Unit-local:
  - which enemy a Unit is actually working on
  - whether that Unit peels out a little
  - whether it brakes
  - whether it returns toward the line
- other things still clearly belong above the Unit:
  - where the fleet front is
  - how much space there is between fronts
  - whether the fleet should still hold, press, or give ground

If those two layers keep sharing old `formation` / `v4a` labels without
cleanup, Human, Engineering, and Governance start reading the same battle
behavior through different mental models.

That is how we end up arguing about the wrong thing:

- a Unit-side maneuver seam gets mistaken for fleet doctrine
- or a fleet-side standoff variable gets mistaken for a local dog-fight knob

So the practical goal of this cleanup plan is:

- make the battle picture easier to read correctly
- without opening a wiring rewrite
- without physically splitting modules yet

### 2. One-sentence conclusion

The current active path already has real Unit-side owners for same-tick target,
same-tick maneuver ask, and low-level locomotion realization; the next minimal
cleanup is therefore mostly:

- owner-language correction for transitional items
- settings/surface reclassification where current labels mislead Human about
  which layer is really doing the work
- explicit confirmation that runtime wiring stays unchanged for now

### 3. Mechanisms that are already honest Unit-side owners

These should now be spoken about plainly as Unit-side or Unit-local owners.

#### 3.1 Same-tick target identity

Active path:

- `_compute_unit_intent_target_by_unit(...)`
- `_select_targets_same_tick(...)`

Battle read:

- this is already the answer to:
  - "which enemy is this Unit actually working on right now?"

Owner judgment:

- honest Unit-side owner

Why:

- it is per Unit
- it is same tick
- it directly feeds Unit-side maneuver and then combat execution

#### 3.2 Same-tick unit desire / maneuver ask

Active path:

- `_compute_unit_desire_by_unit(...)`
- carrier:
  - `desired_heading_xy`
  - `desired_speed_scale`

Battle read:

- this is already the Unit's local ask:
  - "which way should I bias?"
  - "how much should I restrain?"

Owner judgment:

- honest Unit-side owner

#### 3.3 Low-level locomotion realization

Active path:

- `integrate_movement(...)`

Battle read:

- this is where the Unit actually turns, moves, slows, and ends the tick with a
  realized facing and realized velocity

Owner judgment:

- honest Unit-side owner

#### 3.4 Per-Unit engaged maneuver-speed shaping

Active path:

- `_apply_v4a_transition_speed_realization(...)`
- `_compute_attack_direction_speed_scale(...)`

Battle read:

- even though the naming still sounds like old `v4a transition`, this logic is
  already deciding how much speed a specific Unit is allowed to keep in local
  combat geometry

Owner judgment:

- practical Unit-side owner with transitional naming

### 4. Mechanisms that must remain fleet / reference side

These should stay clearly above the Unit layer.

#### 4.1 Fleet front axis / coarse-body heading

Battle read:

- this is what keeps the fleet readable as a fleet front instead of many
  unrelated duelists

Owner judgment:

- fleet/reference side

#### 4.2 Reference surface / expected slot world

Battle read:

- this is still the higher-level answer to:
  - where the fleet body expects Units to belong
  - what overall shape the fleet is trying to preserve

Owner judgment:

- fleet/reference side

#### 4.3 Standoff relation / hold / terminal surface

Active examples:

- `battle_relation_gap_raw`
- `battle_relation_gap_current`
- `battle_brake_drive_current`
- `battle_hold_weight_current`
- hold / terminal surfaces

Battle read:

- these answer fleet-vs-fleet questions:
  - are the fronts too close
  - should the fleet still press
  - should it hold
  - should it start giving ground

Owner judgment:

- fleet/reference side

#### 4.4 Back-off / retreat authorization

Battle read:

- whether the fleet is allowed to reopen space or disengage is not a free
  local Unit choice

Owner judgment:

- fleet/reference side

### 5. Transitional items that need owner-language correction only

These items already behave differently from what their names suggest, but they
do not yet require wiring change.

#### 5.1 `_apply_v4a_transition_speed_realization(...)`

Current problem:

- the function name still frames it as a fleet-transition helper
- but its live job is per-Unit maneuver-speed realization under local geometry

Needed cleanup:

- owner-language correction

Recommended wording:

- describe it as a transitional bridge that now performs Unit-side
  locomotion-speed shaping

What stays unchanged:

- current runtime wiring

#### 5.2 Bridge-side near-contact stability scalars

Examples:

- `battle_near_contact_internal_stability_blend`
- `battle_near_contact_speed_relaxation`

Current problem:

- these still look purely fleet/battle-side in name
- but their practical effect reaches into per-Unit speed budgeting

Needed cleanup:

- owner-language correction

Recommended wording:

- describe them as bridge-side fleet-context carriers that influence Unit-side
  speed realization

What stays unchanged:

- current runtime wiring

#### 5.3 Carrier maps that are not themselves new owners

Examples:

- `formation_hold_reference_max_speed_by_unit`
- `transition_reference_max_speed_by_unit`

Current problem:

- their names tempt readers to over-interpret them as behavior owners

Needed cleanup:

- owner-language correction

Recommended wording:

- describe them as carriers or cached reference surfaces, not as Unit doctrine
  owners

### 6. Transitional items that need settings / surface reclassification

These are the cases where owner-language cleanup alone is probably not enough,
because the public-facing surface itself points Human toward the wrong layer.

#### 6.1 `runtime.movement.v4a.engagement.engaged_speed_scale`

Current practical job:

- overall engaged Unit movement-speed reduction

Why the current surface is misleading:

- it still sounds like a fleet-side `v4a engagement` doctrine surface
- but the live effect is already per-Unit maneuver-speed permission

Needed cleanup:

- settings/surface reclassification

Recommended read:

- transitional engaged Unit maneuver-speed envelope

#### 6.2 `runtime.movement.v4a.engagement.attack_speed_lateral_scale`

Current practical job:

- per-Unit lateral attack-direction movement allowance

Why the current surface is misleading:

- it belongs much more to Unit-side maneuver realization than to fleet
  reference shaping

Needed cleanup:

- settings/surface reclassification

#### 6.3 `runtime.movement.v4a.engagement.attack_speed_backward_scale`

Current practical job:

- per-Unit movement allowance when attack direction lies behind current facing

Why the current surface is especially misleading:

- the name easily over-suggests literal backward-motion capability
- but the runtime still moves along realized heading, not independent reverse
  translation

Needed cleanup:

- settings/surface reclassification
- plus explicit owner-language note that this is a bounded speed-allowance
  surface, not a true backward-motion capability surface

### 7. Items that should not yet trigger wiring change

The following should stay out of wiring change for now.

#### 7.1 Same-tick target source

Keep:

- one target source
- no second guide target

Reason:

- the current cleanup task is naming / surface honesty, not target-owner
  redesign

#### 7.2 Current carrier shape

Keep:

- `desired_heading_xy`
- `desired_speed_scale`

Reason:

- the carrier is already honest enough for the current bounded behavior line

#### 7.3 Fleet battle bundle wiring

Keep:

- current battle-gap / hold / brake bundle path

Reason:

- those scalars still belong fleet/reference side
- the immediate issue is clearer reading of their role, not a fresh bundle
  rewrite

#### 7.4 Physical module split

Keep unchanged:

- no skeleton/unit file split in this step

Reason:

- naming and settings honesty should come first
- physical separation can wait for a later explicitly authorized line

### 8. Recommended cleanup sequence

The next minimal cleanup order should be:

1. owner language first

- fix descriptions so Human can tell:
  - what is Unit-side realization
  - what is fleet-side authorization
  - what is only a carrier

2. settings/surface classification second

- reclassify the misleading `runtime.movement.v4a.engagement.*` family in human
  reference surfaces and comments
- do not over-claim them as fleet doctrine surfaces

3. wiring later only if explicitly justified

- only after Human + Governance conclude that the language cleanup is no longer
  enough

### 9. How this keeps Human / Engineering / Governance aligned

This cleanup plan is meant to reduce three recurring reading errors.

#### 9.1 Misreading Unit-local maneuver as formation doctrine

What the cleanup fixes:

- if a surface already governs per-Unit speed or same-tick desire, it should
  stop being discussed as though the fleet front directly owns every detail of
  it

#### 9.2 Misreading fleet authorization as a local dog-fight knob

What the cleanup fixes:

- standoff / hold / back-off authorization stays clearly fleet/reference side
- Human can keep reasoning in battle-language terms:
  - "the fleet is too compressed"
  - "the fleet should hold"
  - "the fleet may reopen space"

#### 9.3 Misreading old names as proof of current ownership

What the cleanup fixes:

- older `formation` / `v4a` names stop acting like false evidence that
  everything under them is still a fleet-side owner

### 10. What remains explicitly unchanged

This plan does **not** propose:

- runtime rewiring
- file/module split
- target-owner redesign
- locomotion redesign
- retreat implementation
- maintained promotion of experimental behavior

It is a reading / classification cleanup only.

### 11. Shortest conclusion

The active runtime already has real Unit-side owners for:

- same-tick target identity
- same-tick maneuver ask
- low-level locomotion realization
- per-Unit engaged speed shaping

The fleet/reference side must still own:

- fleet front
- reference surface
- standoff / hold / terminal truth
- back-off / retreat authorization

So the next minimal cleanup is:

- fix owner language first
- reclassify misleading settings surfaces second
- and keep runtime wiring unchanged until a later explicitly authorized line
