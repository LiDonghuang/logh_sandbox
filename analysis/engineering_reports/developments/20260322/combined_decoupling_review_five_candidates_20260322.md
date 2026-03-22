# Combined Decoupling Review - Five Candidate Mechanisms (2026-03-22)

Status: Limited Authorization  
Scope: combined bounded review memo for five neutral-transit-exposed decoupling candidates; review/documentation only

## 1. Governance Decision Background

This memo follows the stop-decision recorded in:

- [neutral_transit_decoupling_decision_20260322.md](e:/logh_sandbox/analysis/engineering_reports/developments/20260322/neutral_transit_decoupling_decision_20260322.md)

That decision already established three points:

- `neutral_transit_v1` has done enough to expose shared-path burden clearly
- old-factor `FR x MB x ODW` interaction DOE should stop here
- the next engineering question is mechanism decoupling review, not more tuning inside the current polluted path

This memo does **not** authorize implementation.
It consolidates five linked review targets into one bounded note for context efficiency.

## 2. Why One Combined Review Is Used Now

One combined review is preferable here because:

- the five items are structurally coupled inside the same movement path
- the neutral-transit evidence already exposed them as one review family
- repeating five separate packets would mostly duplicate canonical background and DOE interpretation

This is therefore a context-minimizing review step, not a bundled implementation proposal.

## 3. Review Target A - Centroid Restoration vs Expected-Position Restoration

### What the current code path does

In `runtime/engine_skeleton.py:964-1036`, the cohesion term is still built directly from:

- `centroid_x - unit.position.x`
- `centroid_y - unit.position.y`

That means the active restoration object is the current fleet centroid.
`formation_rigidity (FR)` then scales that restoration term through `kappa`, so the code path currently couples FR directly to centroid-directed pull.

### What neutral-transit evidence makes it problematic

Neutral-transit evidence from the FR-only DOE and the long-diagonal `FR x MB x ODW` DOE shows:

- higher FR increases projection breadth and burden
- higher FR increases final compaction
- higher FR does not read primarily as a clean transit-speed control

That pattern is consistent with centroid restoration dominating the geometry response.

### Why this is a substrate issue rather than a tuning issue

`Formation_Geometry_Doctrine_v1.0.md` says:

- `FR = resistance to formation deformation`
- formation geometry should emerge from the vector field
- centroid-only stray reading is structurally limited

So the issue is not simply "FR tuned too high or too low."
The issue is that the restoration object itself appears mislocated or underspecified for a neutral baseline.

### Classification

Likely migrate-upward candidate

### Most appropriate destination if migrated upward

An upstream cohesion / formation-reference layer that defines expected-position or expected-surface restoration before movement integration.

### What is explicitly not being proposed yet

- no automatic replacement with a new reference-formation mechanism in code
- no broad cohesion redesign
- no silent reinterpretation of FR mapping

## 4. Review Target B - MB Movement-Layer Injection

### What the current code path does

In `runtime/engine_skeleton.py:895-902`, MB is mapped to `mb`.
In `runtime/engine_skeleton.py:1056-1092`, that value is then used to reshape the maneuver vector directly:

- `m_parallel` is scaled by `(1.0 - mb)`
- `m_tangent` is scaled by `1.0 + mb`

So MB is not only constraining mobility; it is directly reshaping the low-level direction composition of movement intent.

### What neutral-transit evidence makes it problematic

The long-diagonal DOE shows:

- MB has little effect on pair count
- MB clearly increases arrival delay
- MB clearly increases correction displacement intensity

That is not the footprint of a narrow mobility-limit control.
It reads more like a low-level vector-shaping lever.

### Why this is a substrate issue rather than a tuning issue

`canonical/Engine_v2.0_Skeleton_Canonical.md` freezes `MobilityBias` as a mobility-constraint parameter only.

So the core problem is not just whether the current MB slope is too strong.
The problem is that MB is currently operating in the wrong role inside the movement substrate.

### Classification

Likely cut candidate for the current movement-layer reshaping branch

### Most appropriate destination if migrated upward

Primary recommendation is not migration upward.
If any MB behavior is retained, it should remain only within explicit mobility-constraint governance inside the movement interface, not as a maneuver-vector reshaper.

### What is explicitly not being proposed yet

- no removal of canonical `mobility_bias` as a public parameter
- no immediate replacement with a new mobility model
- no broad rewrite of movement constraints

## 5. Review Target C - ODW Movement-Layer Injection

### What the current code path does

In `runtime/engine_skeleton.py:1062-1085`, ODW is converted into `odw_parallel_scale` based on lateral position across the fleet width.
That scale is then multiplied into the parallel component of the maneuver vector in `runtime/engine_skeleton.py:1091-1092`.

So ODW is currently acting as an in-movement forward-pressure redistribution rule:

- center-heavy when offensive
- wing-heavy when defensive

### What neutral-transit evidence makes it problematic

The long-diagonal DOE shows:

- low ODW is systematically slower
- low ODW carries heavier projection burden
- higher ODW reduces burden and preserves larger final RMS radius ratio

In neutral transit, that means ODW is not reading like a clean battle preference waiting for enemy context.
It is shaping the baseline substrate of single-fleet travel.

### Why this is a substrate issue rather than a tuning issue

This branch lives below target/posture interpretation and directly rewrites maneuver composition.
That is why the issue is structural:

- it puts posture-like logic into the movement substrate
- it affects neutral baseline behavior even when battle semantics are absent

### Classification

Likely migrate-upward candidate

### Most appropriate destination if migrated upward

A higher tactical-posture or target-decomposition layer upstream of movement, where forward-pressure distribution can be expressed as doctrine/posture semantics rather than low-level movement reshaping.

### What is explicitly not being proposed yet

- no removal of ODW as a canonical battle-facing parameter
- no new posture framework
- no generalized battle/transit unification layer

## 6. Review Target D - Stray-Dependent Attract

### What the current code path does

In `runtime/engine_skeleton.py:1017-1043`, the code computes:

- `stray_ratio_raw = cohesion_norm / fleet_rms_radius`
- `stray_factor`
- `attract_gain`
- `enemy_pull_gain`

Under no-enemy neutral transit, the enemy centroid falls back to own-centroid geometry, so for off-centroid units the attract path can become an extra centripetal recovery term blended with target direction.

### What neutral-transit evidence makes it problematic

Neutral transit is intentionally single-fleet and no-enemy.
In that environment, this branch still participates materially in movement shaping.

That is problematic because the fixture is supposed to expose neutral baseline travel, and the stray-dependent attract path still adds recovery behavior tied to centroid distance rather than clean objective transit alone.

### Why this is a substrate issue rather than a tuning issue

`Formation_Geometry_Doctrine_v1.0.md` already flags centroid-distance-based stray reading as structurally limited.
So this is not simply a threshold problem.
It is a problem with the meaning of the signal being injected into the movement substrate.

### Classification

Likely cut candidate for the current centroid-based neutral-baseline path

### Most appropriate destination if migrated upward

If a future version exists at all, it belongs in a role-aware cohesion / formation-diagnostics layer, not as a centroid-triggered attract term inside baseline movement composition.

### What is explicitly not being proposed yet

- no new stray-detection architecture
- no role-aware formation-surface implementation
- no immediate deletion without Governance selecting the cut

## 7. Review Target E - FSR

### What the current code path does

In `runtime/engine_skeleton.py:1140-1225`, FSR computes one centroid, one RMS radius, one equilibrium radius, and one isotropic scale per fleet per tick before projection.
It then rewrites all alive positions around the centroid using `lambda_f`.

So FSR is currently a pre-projection fleet-scale correction layer that directly modifies positions.

### What neutral-transit evidence makes it problematic

Neutral transit shows strong compaction behavior and broad projection involvement, especially in high-FR regions.
FSR is part of the correction family that sits between movement intent and projection observation.

That is enough to put FSR under review, but the current neutral-transit evidence does **not** isolate FSR cleanly enough to claim it is the first cut.

### Why this is a substrate issue rather than a tuning issue

FSR is not just another scalar on top of the same meaning.
It is an explicit positional rewrite layer inside the movement-to-projection path.
That makes its role architectural, not just parametric.

### Classification

Hold / unclear

### Most appropriate destination if migrated upward

No clear upward destination is justified yet.
If retained at all, it should remain an explicitly named correction layer with isolated confirmation, not be silently absorbed into baseline movement semantics.

### What is explicitly not being proposed yet

- no immediate FSR cut
- no claim that FSR is the primary root cause of neutral-transit burden
- no new replacement correction family

## 8. Comparative Priority Ranking

Recommended review priority order:

1. centroid-restoration vs expected-position restoration
2. ODW movement-layer injection
3. MB movement-layer injection
4. stray-dependent attract
5. FSR

Reading:

- item 1 is the most important conceptual root issue
- items 2 and 3 are the clearest low-level posture/constraint-role violations
- item 4 is strongly implicated but tied to the centroid-restoration problem
- item 5 is clearly review-worthy but not yet the cleanest first cut target

## 9. Recommended First Very Small Cut Candidate

Recommended first very small cut candidate for Governance selection:

`ODW movement-layer injection`

Reason:

- it is a narrow, well-localized branch inside `runtime/engine_skeleton.py:1062-1092`
- it reads as posture-like redistribution, not neutral-baseline substrate
- the neutral-transit DOE shows a clear adverse surface tied to this branch
- cutting or bypassing this branch is more bounded than trying to replace centroid restoration
- it is cleaner than using FSR as the first cut because its current role is easier to separate from the rest of the correction stack

This recommendation does **not** mean ODW is the deepest conceptual issue.
It means ODW movement-layer injection is the best first *small* cut candidate.

## 10. Explicit Non-Authorizations

This memo does **not** authorize:

- simultaneous implementation of all five changes
- broad movement rewrite
- silent runtime baseline change
- silent semantic reinterpretation of canonical parameters
- reopening old-factor interaction DOE on the current polluted path
- automatic code replacement of centroid restoration with a new reference-formation mechanism

## 11. Next Bounded Step

Recommended next step:

1. Governance selects one first very small cut candidate
2. Engineering performs one inspect/plan round only for that candidate
3. Engineering proposes one bounded behavior-preserving or behavior-narrowing cut
4. After approval, Engineering runs only very small confirmation checks

This preserves the current decision discipline:

- review first
- one cut at a time
- no silent architecture drift
