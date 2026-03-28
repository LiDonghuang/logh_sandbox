# Step 3 3D Legality Minimum Contract Structural Draft Note (2026-03-28)

Engine Version: `dev_v2.0`
Modified Layer: Step 3 legality line second-carrier structural-draft-only minimum-contract opening
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: narrows the minimum contract surface for legality downstream of mapping without opening runtime integration, hook design, movement semantics, or viewer ownership
Mapping Impact: preserves mapping ownership by keeping legality contract downstream of the mapping output surface and upstream of any implementation path
Governance Impact: advances legality beyond pure scope confirmation while keeping minimum-contract drafting smaller than implementation design
Backward Compatible: yes

Summary
- This turn advances legality from opening scope confirmation to a minimum-contract structural draft.
- The safest bounded result is still a very small contract-question set with field-equivalent anchors, not a frozen runtime field table.
- The minimum legality contract must express downstream feasibility ownership, weak projection/collision/boundary ownership, and a weak downstream feasible-outcome surface.
- Projection, collision, and boundary handling remain contract-level ownership language only, not algorithm design.
- Implementation, runtime hooks, runtime touchpoints, mapping redesign, movement semantics, and viewer ownership remain explicitly closed.

## 1. Minimum Legality Contract Surface

The minimum legality contract surface should express only the following:

- that legality owns downstream feasibility resolution after mapping
- that projection belongs to legality only as a downstream feasibility class
- that collision / overlap and boundary constraint handling belong to legality only as downstream feasibility classes
- what downstream feasible outcome surface legality exposes
- what remains explicitly outside legality

This is the smallest contract surface that still makes legality readable as a layer distinct from both mapping and implementation.

It stays smaller than implementation because it does not choose:

- algorithms
- runtime hooks
- runtime touchpoints
- execution order
- performance strategy

## 2. Candidate Minimum Fields Or Equivalent Contract-Question Set

The cleanest bounded result for this turn is a very small contract-question set:

- feasibility ownership question
  - does legality own downstream feasibility resolution for the mapping-produced reference outcome

- projection ownership question
  - does legality own downstream projection as part of feasibility resolution

- collision / boundary ownership question
  - does legality own downstream overlap, collision, and boundary constraint resolution

- output-surface question
  - what legality exposes as the downstream feasible outcome surface

If a field-equivalent surface is needed for later discussion, it should remain no larger than:

- one downstream feasibility ownership field
- one projection-scope field
- one collision / boundary-scope field
- one downstream feasible-outcome surface field

This note intentionally does not freeze exact field names.

That keeps the contract legible without prematurely freezing runtime-facing identifiers.

## 3. Weak Reading Of Projection / Collision / Boundary Handling

Projection / collision / boundary handling must remain weakly read at this turn.

The bounded intended reading is:

- these downstream question classes belong to legality in principle
- legality may transform a mapping-produced reference outcome into a feasible downstream outcome

The bounded reading is not:

- projection algorithm design
- collision-resolution algorithm design
- boundary-clamp algorithm design
- fallback-placement rule design
- solver heuristic design
- runtime trigger design
- execution-order design

This minimum contract therefore answers ownership only, not behavioral implementation shape.

## 4. Weak Reading Of Downstream Feasible Outcome Surface

The minimum legality contract should expose only a weak output-surface anchor:

- legality-resolved feasible positions
- or equivalent downstream feasibility-resolved outcome

This should remain implementation-neutral.

It means only:

- the legality layer receives a mapping-produced reference outcome downstream
- the legality layer may emit a downstream feasible outcome surface
- that downstream surface remains after mapping and before any implementation-specific execution path

It does not mean:

- the exact surface name is frozen
- the exact runtime type is frozen
- the exact hook location is chosen
- the exact storage site is chosen
- the exact call path is chosen
- implementation is authorized

## 5. Explicit Exclusions

This minimum-contract opening does not open:

- implementation-path commitment
- runtime hooks
- runtime touchpoints
- projection algorithm design
- collision algorithm design
- boundary algorithm design
- mapping redesign
- movement semantics
- viewer ownership semantics

More specifically, this note does not authorize:

- stable identity-to-slot assignment redesign
- remapping / reflow redesign
- `expected_position_map` ownership redesign
- feasibility heuristics implementation
- projection heuristic implementation
- collision-resolution heuristic implementation
- boundary-clamp implementation
- fallback-placement logic
- steering behavior
- temporal response
- turning dynamics
- inertia semantics
- doctrine / posture movement reading
- rendering ownership
- `viz3d_panda/` semantic authority
- camera/display attributes
- glyph/display/layout visualization semantics
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

- mapping stays the assignment-structure contract layer
- legality stays the downstream feasibility contract layer
- legality minimum contract may express weak projection / collision / boundary ownership only
- legality minimum contract may express only a weak downstream feasible-outcome surface
- implementation remains closed

That is sufficient for this turn.

No runtime integration design, hook placement, algorithm freeze, or viewer-semantic expansion is confirmed here.
