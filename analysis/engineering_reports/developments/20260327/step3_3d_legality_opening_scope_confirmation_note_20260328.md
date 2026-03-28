# Step 3 3D Legality Opening Scope Confirmation Note (2026-03-28)

Engine Version: `dev_v2.0`
Modified Layer: Step 3 next-carrier structural-draft-only legality opening scope confirmation
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: confirms the structural role of legality downstream of mapping without opening runtime integration, hook design, movement semantics, or viewer ownership
Mapping Impact: preserves mapping ownership by keeping legality downstream of the mapping output surface
Governance Impact: opens the legality layer only as a bounded scope-confirmation carrier
Backward Compatible: yes

Summary
- This turn confirms legality as the downstream feasibility / projection layer after mapping.
- The opening is scope confirmation only, not a legality implementation design.
- The minimum legality question set is limited to downstream feasibility ownership, projection/collision/boundary ownership, and the boundary against mapping ownership.
- Any discussion of projection or collision remains scope-definition language only, not algorithm, hook, or runtime-path design.
- Movement semantics, viewer ownership, runtime touchpoints, and implementation remain explicitly closed.

## 1. Legality Ownership

The legality layer is confirmed as owning the downstream feasibility question after mapping.

Within the established layer order:

- objective
- formation reference
- mapping
- legality

the legality layer is the first layer allowed to answer:

- whether a reference-assignment outcome is feasible
- how downstream projection / boundary / collision constraints are enforced in principle

The legality layer does not own:

- objective meaning
- formation reference geometry
- mapping ownership of stable identity-to-slot assignment

## 2. Minimum Legality Question Set

At this opening, the minimum structural question set for legality is:

- whether the mapping-produced reference outcome is feasible
- what classes of downstream constraints legality is responsible for
- what legality may alter downstream of mapping
- what legality must not reinterpret upstream

Under the current bounded reading, legality may answer:

- feasibility in principle
- projection as a downstream feasibility operation
- boundary constraint enforcement
- collision / overlap conflict resolution

This turn does not freeze a stable minimum field table.

It only confirms that these are the correct structural questions for the legality layer.

## 3. Weak Reading Of Projection / Collision / Boundary Handling

At this turn, projection / collision / boundary handling must be read only as scope-definition language:

- these classes of downstream feasibility questions belong to legality
- they do not yet define implementation shape

That means this opening does not authorize:

- projection algorithm design
- collision-resolution algorithm design
- fallback-placement rule design
- boundary-clamp algorithm design
- runtime trigger design
- execution-order design

The weak reading is:

- legality owns these downstream question classes in principle
- not that their runtime behavior is now specified

## 4. Candidate Output-Surface Reading

The candidate output-surface reading for this opening is:

- legality-resolved feasible positions or equivalent downstream feasibility-resolved outcome

This should remain implementation-neutral.

It means only:

- legality may transform a mapping-produced reference outcome into a downstream feasible outcome
- that result remains downstream of mapping ownership

It does not mean:

- the exact runtime type is frozen
- the exact hook location is chosen
- the exact code path is chosen
- implementation is authorized

## 5. Explicit Exclusions

This legality-opening scope confirmation does not open:

- mapping redesign
- movement semantics
- viewer ownership semantics
- runtime touchpoints
- implementation-path commitment

More specifically, this note does not authorize:

- stable identity-to-slot assignment redesign
- remapping / reflow trigger design
- `expected_position_map` ownership redesign
- steering behavior
- temporal response
- turning dynamics
- inertia semantics
- doctrine / posture movement reading
- rendering ownership
- `viz3d_panda/` semantic authority
- camera/display attributes
- glyph/display/layout visualization semantics
- runtime touchpoint inventory
- runtime integration sketch
- code path proposal
- hook design
- execution algorithm
- performance strategy
- target preference semantics
- doctrine / posture semantics
- tactic language
- combat meaning

## 6. Boundary Bottom Line

The correct bounded reading remains:

- mapping remains the assignment-structure layer
- legality remains the downstream feasibility layer
- legality may answer projection / boundary / collision questions only in structural scope
- implementation remains closed

That is sufficient for this turn.

No runtime integration design, hook placement, or viewer-semantic expansion is confirmed here.
