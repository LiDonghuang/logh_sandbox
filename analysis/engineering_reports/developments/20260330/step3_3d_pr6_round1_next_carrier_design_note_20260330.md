# Step 3 3D PR #6 Round 1 Next Carrier Design Note

Status: round-1 carrier design note  
Scope: PR `#6` next bounded carrier definition only  
Authority: engineering design note for governance/human review; not implementation approval  
Non-scope: merge approval, default switch, runtime-core rewrite, hostile-contact redesign, personality reintegration

---

## I. Purpose

This note defines the smallest honest next carrier on PR `#6` after the latest governance read.

The note accepts as fixed background:

- formation geometry must remain emergent from the movement vector field
- no direct parameter -> formation mapping is allowed
- PR `#6` has reached the limit of the reference-only carrier method
- bands remain meaningful as topology membership, but must not remain the first geometry-owning object
- movement realization is now part of the main problem, not a later optional realism pass

The purpose is therefore not to describe a better reference surface.

The purpose is to define the smallest honest **formation-transition carrier** that still fits inside the current frozen-runtime discipline.

---

## II. The Next Carrier Read

The next carrier should explicitly co-own three coupled layers:

### 1. Target morphology

What morphology the fleet is trying to become.

### 2. Transport / topology continuity

How units and substructures move from current shape toward target shape without:

- lateral rupture
- shell-only success with chaotic interior
- isolated subformation compression
- late forced regularization replacing real transition

### 3. Movement realization

How turning, slowing, approach, arrival, engagement, and hold make the transition read plausibly in motion.

This is the smallest honest redefinition that still preserves the useful bounded work already accumulated on PR `#6`.

---

## III. Continuous Morphology Semantics

The next carrier should continue to use the same first continuous morphology quantities that governance recommended, but it must read them more cleanly.

### A. `morphology_axis`

Meaning:

- the fleet-owned principal transition axis
- the direction in which the current morphology is organized

It should be read as:

- a weakly owned morphology reference frame
- not raw target direction
- not a disguised steering command

Its job is to give the transition carrier a stable directional frame in which morphology and transport can be expressed.

### B. `extent_state`

Minimum fields:

- `forward_extent`
- `lateral_extent`

Meaning:

- the current fleet-level morphology extents
- not slot counts
- not band-center spans
- not an exact template envelope

These are continuous morphology semantics:

- how long / deep the body currently is
- how wide it currently is

Their target values define the intended transition.
Their current values define where the body is now.

### C. `center_wing_differential`

Meaning:

- a continuous center-vs-wing morphology bias
- the degree to which the center projects or recedes relative to the wings

This quantity is useful because it can support:

- flat-front tendencies
- mild spindle / diamond tendencies
- center-led or wing-led pressure

without turning band identity into a hard geometry authority.

It must remain continuous and weakly owned.
It must not become a disguised set of band-center offsets.

---

## IV. Target Morphology Layer

The target morphology layer should be read as:

- the fleet's intended continuous body state
- not a set of per-unit target slots

For the next bounded carrier, target morphology should therefore be represented minimally by:

- `morphology_axis_target`
- `forward_extent_target`
- `lateral_extent_target`
- `center_wing_differential_target`

These should be enough to express the first honest transition problem:

- `1 -> 1`
- `4 -> 4`
- `1 -> 4`
- `4 -> 1`

without pretending that full 3D ownership already exists.

Bands may still be derived later as topology memberships in this morphology field.
They should not be the primary geometry definition.

---

## V. Transport / Topology Continuity Layer

The next carrier must stop behaving like:

- reference target exists
- units individually restore toward it

and instead behave like:

- the fleet body changes continuously
- units move through that change continuously
- topology is preserved as much as possible

### A. First transport read

The next carrier should keep:

- broad topology continuity
- relative ordering continuity
- local transport continuity

before attempting any better exact reference realization.

That means the first transport object is not a slot map.
It is a continuous material-position read inside the fleet body.

### B. Role of bands in transport

Bands may remain:

- as stable topology membership
- as broad location class

for example:

- front / middle / rear
- left / center / right

But they should only act as:

- topology guards
- continuity constraints
- spillover boundaries when needed

They should not be:

- the first geometry-owning object
- the first transport-driving object

### C. Human-critical requirement

The transport layer must be judged against the Human-critical mismatched cases:

- `1 -> 4`
- `4 -> 1`

The next carrier should explicitly try to achieve:

- real forward-axis shortening + lateral reorganization in `1 -> 4`
- real orderly compression in `4 -> 1`

not just external-shell correctness.

---

## VI. Movement Realization Layer

The next carrier must now explicitly treat movement realization as part of formation transition, not as a later realism add-on.

This layer has three required parts.

### A. Shape-vs-advance budgeting

The current branch has already opened a useful bounded seam here.

That seam remains valid.

Meaning:

- when transition need is large, the fleet should not spend full authority on raw advance
- when transition need is small, the fleet may spend more authority on advance or pressure

This should remain bounded and continuous.

### B. Heading realization

The current `heading_relaxation` seam also remains valid.

Meaning:

- desired movement direction and realized heading should not be identical by default

This remains part of the new carrier, not a discarded side experiment.

### C. Arrival / hold realization

Terminal/hold semantics now also belong explicitly inside the same layer.

Meaning:

- terminal capture
- arrival slowing
- morphology-level hold-await

must be treated as part of how the transition is physically realized.

The current terminal fix showed this is an independent real bug surface.

---

## VII. New Battle Read: Fleet-Level Relative Standoff

Governance approved adding battle standoff into the carrier.

The current next-carrier read is:

- battle target should stop being mainly "go to enemy centroid"
- battle should instead own a bounded fleet-level desired engagement distance `d*`

### A. Smallest honest first `d*`

The smallest honest first read can stay bounded to existing quantities:

- `attack_range`
- own current formation scale
- enemy current formation scale

A minimal first bounded function can be:

```text
d* = attack_range
   + k_self * own_forward_extent
   + k_enemy * enemy_forward_extent
```

where:

- `k_self`
- `k_enemy`

are small bounded coefficients, likely test-only in the first implementation round.

This is not a doctrine claim.
It is only a bounded first honest read that says:

- larger bodies do not truthfully behave like point masses pursuing another point mass

### B. How `d*` enters the carrier

The battle carrier should then use:

- current fleet-to-fleet distance vs `d*`

to derive:

- approach pressure
- hold pressure
- overshoot suppression

This means:

- enemy centroid may remain a fallback geometric reference
- but it should no longer remain the final honest target semantics

### C. Why this belongs in the same carrier

Battle standoff is not separate from formation transition.

It matters because:

- morphology transition needs approach space
- approach pace should depend on whether the fleet is still outside, near, or inside its intended engagement distance
- final battle plausibility depends on approach / hold / pressure being relative to formation scale, not just point pursuit

---

## VIII. New Unit-Level Attack-Direction-Aware Speed Envelope

Governance also approved adding a unit-level attack-direction-aware speed envelope into the carrier read.

This should be read as:

- a movement-realization seam
- not only a combat add-on

### A. Required logic

Each unit's allowed movement speed should depend on:

- whether it is currently engaged
- direction to its currently engaged target
- relation between its movement/heading and that attack direction

### B. Minimum speed-envelope read

The smallest honest first read is:

```text
speed_allowance
= base_transition_speed
  * engagement_factor
  * directional_factor
```

where:

- `engagement_factor`
  reduces speed when actively engaged
- `directional_factor`
  depends on attack-direction alignment

Minimum directional buckets for first implementation:

- forward attack: highest allowed
- lateral attack: reduced
- backward attack: strongly reduced

This does not require a complicated physics model.
It only requires accepting that attack direction and movement freedom are coupled.

### C. Why this belongs to formation transition

This is important because transition quality currently fails partly from:

- units moving as if attack direction does not constrain local motion plausibility

The next carrier should therefore treat the envelope as part of:

- orderly transition
- battle-plausible movement

not only as a combat micro-detail.

---

## IX. Coupling to the Existing Combat-Angle Mechanism

The repo already has an older combat-quality line in `runtime/engine_skeleton.py`:

- fire-quality scales with the cosine between attacker orientation and attacker-to-target direction
- current shape:
  - `q = 1 + alpha * cos(theta)`

The next carrier should not invent a disconnected directional semantics.

### A. Accepted coupling read

The new speed-envelope semantics should be explicitly read as parallel to the existing combat-angle quality line:

- the same directional relation matters for both
  - combat quality
  - movement freedom while attacking

### B. But the two lines should remain distinct in role

They should not be collapsed into one scalar.

Instead:

- combat-angle quality line:
  - modulates attack quality / damage effectiveness
- attack-direction-aware speed envelope:
  - modulates movement freedom / speed allowance

This keeps the semantics aligned without making them identical.

### C. Smallest honest shared directional source

The clean first coupling is:

- use the same cosine-style orientation-to-target directional read
- but feed it into:
  - one combat-quality function
  - one movement-speed-envelope function

This preserves interpretive coherence:

- one directional relation
- two different mechanism effects

---

## X. Smallest Bounded Implementation Direction

Without touching the frozen runtime core, the next bounded implementation round should stay in `test_run/` and add only the smallest carrier advance needed to express this design.

Minimum preferred files:

- `test_run/settings_accessor.py`
- `test_run/test_run_scenario.py`
- `test_run/test_run_execution.py`
- `test_run/test_run_v1_0.testonly.settings.json`
- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`

The first implementation should therefore aim to add only:

1. a bounded test-only fleet-level standoff function
2. a bounded test-only unit-level attack-direction-aware speed envelope
3. a clearer continuous ownership path for:
   - `morphology_axis`
   - `extent_state`
   - `center_wing_differential`

No full 3D claim is needed.
No runtime-core rewrite is needed in this round.

---

## XI. Bottom Line

The next carrier on PR `#6` should now be read as:

> a bounded formation-transition carrier that co-owns continuous target morphology, topology-preserving transport, and movement realization, while adding a fleet-level battle standoff read and a unit-level attack-direction-aware speed envelope aligned with the existing combat-angle quality semantics.

That is the smallest honest next carrier definition under the current governance read.
