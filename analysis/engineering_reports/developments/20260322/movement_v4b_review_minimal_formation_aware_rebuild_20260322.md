# Movement v4b Review - Minimal Formation-Aware Rebuild (2026-03-22)

Status: Limited Authorization  
Scope: bounded `v4b` review on the first minimal formation-aware rebuild move after `v4a` subtraction; review only

## 1. Why v4a Necessarily Leads to v4b

`v4a` already answered the subtraction question.

It showed that cutting the old shaping family was worthwhile:

- `mean_corrected_unit_ratio` fell from `0.899` to `0.774`
- `peak_projection_pairs` fell from `147` to `119`
- `final_rms_radius_ratio` moved from `0.684` to `1.017`

At the same time, `v4a` also showed that subtraction alone does not solve the remaining local correction problem:

- arrival slowed slightly: `445 -> 451`
- `peak_projection_mean_displacement` rose: `0.285 -> 0.354`
- `peak_projection_max_displacement` rose: `0.863 -> 0.944`

So the correct next question is no longer whether subtraction helps.
It does.
The next question is what minimal formation-aware rebuild move should be reviewed first on top of the cleaner `v4a` substrate.

## 2. Remaining Issue After Subtraction

After `v4a`, the surviving neutral-transit movement path is dominated by:

- direct cohesion toward fleet centroid
- direct objective-forward maneuver term
- local separation response
- final projection / feasibility correction

In `runtime/engine_skeleton.py:971-1112`, the surviving local structure is still:

- `cohesion_vector = centroid - unit.position`
- plus objective-forward maneuver
- plus separation
- then projection resolves remaining local conflicts

The most likely source of the remaining local correction intensity is therefore:

- centroid-directed restoration continuing to pull units inward without reference to their expected local role in the formation
- combined with forward transport and separation, this creates local competition that projection must still resolve

This matches the `v4a` paired result:

- broad projection burden went down
- but local correction intensity per active correction rose

That is exactly what would be expected if the main surviving issue is not old shaping family noise, but an insufficient restoration object.

## 3. Why Centroid-Restoration Is Now the Primary Review Target

Centroid restoration is now the primary review target because it is the deepest surviving structural issue that remained untouched by `v4a`.

Current behavior:

- every unit is restored toward the same centroid object
- units are not restored toward an expected slot, expected flank role, expected depth band, or expected shape surface

Why that matters in neutral transit:

- front units, wing units, and center units are all judged against the same centroid object
- this promotes inward recovery even when a unit may still be locally compatible with the intended overall formation
- projection then inherits the burden of resolving local crowding or overlap that the upstream restoration object failed to organize cleanly

This is consistent with the doctrine record:

- `FR = resistance to formation deformation`
- geometry should emerge from the vector field
- centroid-only stray reading is structurally limited
- the more appropriate future direction is closer to `distance_from_expected formation surface`

So the issue is not "FR needs more tuning."
The issue is that the current upstream restoration object is too centroid-centric.

## 4. Candidate A - Minimal Expected-Position Anchor

### Concept

For the single-fleet neutral-transit fixture only, preserve each unit's initial formation slot as a minimal expected-position anchor.

Expected position would be derived from:

- initial formation geometry
- initial unit-to-slot identity
- a simple fleet frame carried forward through neutral transit

The cohesion/reference layer would then restore units toward expected slot positions rather than directly toward fleet centroid.

### What this answers well

- gives each unit a local restoration object
- makes "formation resistance" more interpretable than centroid pull alone
- is easy to read in the current single-fleet / no-enemy fixture because no unit death, no slot reassignment, and no adversarial battle geometry are involved

### Structural cost

- introduces unit-level expected anchors
- requires a minimal fleet frame definition
- requires careful scope fencing so it does not silently become a general reference-formation system

### Canonical-discipline risk

Medium.

It is more concrete and interpretable than centroid restoration, but it can easily expand into:

- slot reassignment
- role systems
- full reference-formation tracking

unless its boundary is kept extremely narrow.

### Best layer if ever implemented

Upstream cohesion/reference layer or movement input preparation layer.

Not inside the movement loop itself.

## 5. Candidate B - Expected-Surface / Shape-Envelope Restoration

### Concept

Do not assign each unit a fixed slot.
Instead define a weaker expected formation object, such as:

- expected width/depth envelope
- expected formation surface
- expected band relative to a fleet frame

The restoration term would then pull units back toward compatible surface/envelope occupancy instead of one exact slot.

### What this answers well

- respects the doctrine direction toward expected surface rather than centroid distance
- avoids immediate commitment to a full slot system
- may fit the long-term idea that geometry should remain emergent rather than rigidly prescribed

### Structural cost

- weaker and more ambiguous than slot anchors
- harder to make diagnostic in the current fixture
- may still leave uncertainty about which local correction problems are truly resolved

### Canonical-discipline risk

Medium-low conceptually, but medium-high interpretability-wise.

It is doctrinally attractive, but less concrete.
That makes it easier to discuss cleanly than to validate cleanly.

### Best layer if ever implemented

Upstream cohesion/reference layer.

It should remain an input-shaping object, not a movement-loop-internal geometry generator.

## 6. Comparative Assessment

### Boundedness

- Candidate A is more bounded for the current fixture because the single-fleet neutral path already supplies stable initial geometry and stable unit identity.
- Candidate B is broader conceptually because an envelope/surface object needs more interpretation before it becomes testable.

### Interpretability

- Candidate A is easier to pair against `v4a` because it gives a direct answer to "what should this unit roughly return toward?"
- Candidate B is easier to justify doctrinally, but harder to turn into a crisp minimal confirmation experiment.

### Implementation-risk drift

- Candidate A risks scope creep into full slot/reference machinery.
- Candidate B risks ambiguity and under-specification, which can invite broad exploratory redesign.

### Current engineering reading

For this repo state and this fixture, Candidate A is the better first bounded review target.
It is not necessarily the final architecture direction.
It is simply the smallest formation-aware rebuild move that can be reviewed concretely and later tested narrowly.

## 7. Recommended First Bounded Implementation Target

Recommended first bounded implementation target for future Governance selection:

`Candidate A - Minimal Expected-Position Anchor`

But only with the following hard boundary:

- single-fleet neutral-transit fixture only
- no battle-path activation
- no slot reassignment
- no role system
- no generalized reference-formation framework
- no FR semantic rewrite
- no movement-loop-internal geometry generation

In that bounded form, the move is best described as:

- a minimal upstream restoration-object replacement for the neutral fixture
- not a full reference-formation system

## 8. Minimal Implementation Boundary If Ever Authorized

To avoid sliding into broad rewrite, the smallest implementation boundary should be:

1. keep `v4a` as the base substrate
2. restrict the move to `neutral_transit_v1`
3. define one stable fleet frame for the fixture
4. reuse initial unit ordering as fixed slot identity
5. produce expected positions upstream of movement
6. replace centroid-directed restoration input with expected-position-directed restoration input only in that bounded path
7. validate only with very small paired neutral checks

This keeps the move inside an inspectable container and prevents it from silently becoming:

- a general battle formation engine
- a new FR mechanism
- a baseline replacement

## 9. Explicit Non-Authorizations

This review does **not** authorize:

- full expected-position / reference-formation implementation
- FR canonical reinterpretation
- broad cohesion redesign
- broad movement rewrite
- 3D work
- reintroduction of MB / ODW / stray shaping
- baseline replacement
- large DOE

## 10. Next-Step Request to Governance

Recommended next Governance question:

- whether to authorize one inspect/plan-only round for `Candidate A - Minimal Expected-Position Anchor`, with the boundary fixed to single-fleet neutral transit and no generalized slot/reference framework

That is the narrowest next step that can convert the current `v4b` review into a concrete engineering proposal without prematurely opening broad rebuild work.
