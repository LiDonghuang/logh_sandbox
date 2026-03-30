# Step 3 3D PR6 Hold-Await + Reference Mode Local Note

Date: 2026-03-30
Scope: local engineering note only
Layer read: `test_run/` bounded PR `#6` carrier iteration

## What changed

This local iteration introduces three bounded changes on the active PR `#6` line:

1. `neutral_transit_v1` now uses a real `v4a` fixture bridge during movement integration, not only battle-side bridge semantics.
2. `hold/latch` now acts as true morphology-level `hold-await` for the neutral fixture path:
   - morphology state is latched
   - fleet movement stops chasing the point-anchor objective while held
   - this remains a fleet-level hold, not exact per-unit freeze
3. `runtime.movement.v4a.test_only.reference_layout_mode` now carries explicit reference aspect options:
   - `rect_centered_1.0`
   - `rect_centered_4.0`

The initial spawned fleet aspect remains separate from the reference aspect.

## Structural carrier correction

This iteration also replaces the current band actuation read from:

- live group-mean recentre
- live within-band reorder

to:

- stable reference-slot residuals
- shared band-anchor lattice state
- hold-time anchor latching

The aim is to stop a few edge units from oscillating because band ownership is too explicitly driven by current member means.

## Current local read

The new carrier fixes one real problem and exposes another:

- it suppresses the previous edge-unit swing / swirl source driven by live band recentering
- but matched initial/reference cases now read too close to perfect rigid lock

Focused neutral-transit validation currently reads as:

- `aspect_ratio=1.0`, `reference=rect_centered_1.0`
  - reaches objective
  - RMS error remains `0.0`
  - front extent ratio remains `1.0`
  - visually/structurally this is too hard-locked

- `aspect_ratio=4.0`, `reference=rect_centered_4.0`
  - does not reach objective within the bounded `520`-tick run
  - RMS error remains `0.0`
  - front extent ratio remains `1.0`
  - this indicates a stronger rigid-lock / overconstraint failure

- mismatch cases now visibly express reference-vs-initial distinction:
  - `1.0 -> 4.0` and `4.0 -> 1.0` no longer collapse to the same read

## Current conclusion

This iteration successfully establishes:

- true hold-await semantics for the neutral fixture path
- true distinction between initial fleet aspect and reference aspect
- stronger separation between stable reference ownership and live band-member centroids

But it also overshoots into a new failure mode:

- matched aspect/reference cases are now too rigid

So the next correction should not roll back:

- hold-await semantics
- reference aspect separation
- stable band-anchor ownership

Instead, the next correction should focus on reintroducing bounded internal softness without returning to live mean-driven band oscillation.
