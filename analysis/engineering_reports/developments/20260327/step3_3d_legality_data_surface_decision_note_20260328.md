# Step 3 3D Legality Data Surface Decision Note (2026-03-28)

Engine Version: `dev_v2.0`
Modified Layer: Step 3 legality line local pre-implementation data-surface decision
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: fixes the minimum runtime-side shape of legality intake and legality-resolved output surfaces without freezing implementation containers, hook locations, or viewer ownership
Mapping Impact: preserves mapping ownership by treating the legality input only as a mapping-produced reference-position surface and by excluding any mapping redesign
Governance Impact: advances legality from placement decision to a bounded data-surface decision that is concrete enough for bounded implementation planning while remaining smaller than implementation
Backward Compatible: yes

Summary
- This turn fixes the minimum runtime-side shape for legality intake and legality-resolved output.
- The core upstream shape should be a stable-unit-identity keyed reference-position surface only.
- The core downstream shape should be the same identity-preserving map-like shape, but feasibility-resolved.
- Non-core frame axes, diagnostics, projection metrics, boundary counters, and observer/report echo stay outside the core surfaces.
- Exact container type, storage site, hook location, and call path remain undecided.

## 1. Decision Scope

This carrier decides only:

- the minimum runtime-side shape of the legality input surface
- the minimum runtime-side shape of the legality-resolved output surface

It does not decide:

- exact Python/container type
- exact field/variable name
- exact storage site
- exact hook location
- exact call path
- exact telemetry payload shape

## 2. Core Data-Surface Decision

The minimum core runtime-side surfaces should now be read as:

- one stable-unit-identity keyed reference-position surface for legality intake
- one stable-unit-identity keyed feasible-position surface for legality output

The cleanest bounded surface labels are:

- `reference_positions_by_unit`
- `feasible_positions_by_unit`

These labels should be read as:

- surface-level semantic anchors only
- map-like unit-addressable position surfaces
- replaceable by equivalent later wording if semantics stay unchanged

They should not be read as:

- frozen runtime identifiers
- fixed storage keys
- fixed API names

## 3. Upstream Input Surface Shape

The minimum legality input surface should contain only:

- stable unit identity
- corresponding reference position

The current repo-side bounded precedent is:

- `runtime/engine_skeleton.py` `_build_fixture_expected_position_map()`
- its core `expected_positions` map-like surface

That precedent is useful because it already shows the smallest viable intake shape:

- unit-addressable
- position-only at the core

The following should stay outside the core upstream shape for now:

- `primary_axis_xy`
- `secondary_axis_xy`
- any diagnostic sideband
- any observer/report payload

Those may remain adjacent context later if needed, but they are not part of the minimum core legality input surface.

## 4. Downstream Feasible-Outcome Surface Shape

The minimum legality output surface should mirror the upstream core shape as closely as possible.

That means:

- the same unit-identity domain
- the same position-oriented map-like shape
- a different semantic meaning: feasibility-resolved rather than reference-intent

The downstream core should therefore be read only as:

- unit-addressable feasible positions
- post-legality feasible-outcome surface

This is the smallest downstream shape that stays useful without prematurely expanding into richer payloads.

## 5. Shape Rules That Should Stay Fixed

The following bounded shape rules are now the useful minimum:

- identity-preserving between upstream and downstream core surfaces
- position-centered rather than metadata-heavy
- map-like rather than telemetry-bundled
- core surface separated from observer/report echo

This means the core legality surfaces should not embed:

- projection metrics
- boundary counters
- diagnostic traces
- rendering/readout fields
- downstream consumer policy

## 6. What Remains Outside The Core Surfaces

The following remain outside the minimum core legality surfaces:

- axis/frame sideband context
- diagnostic and telemetry payloads
- observer/report echo payloads
- rendering/viewer fields
- algorithm settings or procedure state

Those may exist later as adjacent sidebands if needed, but they do not belong in the core intake/output surfaces.

## 7. Bottom Line

The minimum useful runtime-side data-surface decision is:

- intake as a stable-unit-identity keyed reference-position surface
- output as a stable-unit-identity keyed feasible-position surface
- keep both surfaces identity-preserving and position-centered
- keep axes, diagnostics, and observer/report payloads outside the core surfaces

That is sufficient for this carrier.
