# Step 3 3D Legality Contract Stabilization Note (2026-03-28)

Engine Version: `dev_v2.0`
Modified Layer: Step 3 legality line third-carrier structural-draft-only contract stabilization
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: stabilizes a very small legality contract surface downstream of mapping without opening runtime integration, hook design, movement semantics, or viewer ownership
Mapping Impact: preserves mapping ownership by keeping legality contract consumption downstream of the mapping-produced reference outcome and by excluding mapping redesign
Governance Impact: converts the accepted legality minimum-contract question set into a small stable contract-level field-equivalent surface while remaining smaller than implementation design
Backward Compatible: yes

Summary
- This turn stabilizes the legality contract at contract level only.
- The stabilized surface is intentionally small: one feasibility-ownership anchor, one projection-scope anchor, one collision/boundary-scope anchor, and one downstream feasible-outcome surface anchor.
- These anchors are field-equivalent contract names only, not frozen runtime-facing identifiers.
- Projection, collision, and boundary handling remain ownership/scope language only, not algorithm design.
- Implementation, runtime hooks, runtime touchpoints, mapping redesign, and viewer ownership remain explicitly closed.

## 1. Stable Contract-Level Surface

The smallest stable legality contract surface can now be expressed as the following field-equivalent anchors:

- `feasibility_ownership`
- `projection_scope`
- `collision_boundary_scope`
- `feasible_outcome_surface`

This is a contract-level surface only.

These anchor names should be read as:

- semantic placeholders for the stabilized legality contract
- implementation-neutral contract language
- replaceable by equivalent later wording if the semantics stay unchanged

These anchor names should not be read as:

- frozen runtime keys
- fixed storage identifiers
- hook names
- code-path names

## 2. Bounded Reading Of Each Stable Anchor

`feasibility_ownership`

- declares that legality owns downstream feasibility resolution after mapping
- does not reopen mapping ownership
- does not choose how feasibility is computed at runtime

`projection_scope`

- declares that projection belongs to legality only as a downstream feasibility class
- does not define projection algorithm shape
- does not define fallback or trigger behavior

`collision_boundary_scope`

- declares that collision / overlap and boundary constraint handling belong to legality only as downstream feasibility classes
- does not define collision-resolution procedure
- does not define boundary-clamp procedure

`feasible_outcome_surface`

- declares that legality may expose a downstream feasible-outcome surface after consuming the mapping-produced reference outcome
- does not freeze the exact surface name, runtime type, storage site, or call path

## 3. Weak Reading Of Projection / Collision / Boundary Scope

The stabilized contract keeps projection / collision / boundary handling under a weak reading:

- legality owns these downstream question classes in principle
- legality may resolve them at contract level only as downstream feasibility ownership

The stabilized contract does not authorize:

- projection algorithm design
- collision algorithm design
- boundary algorithm design
- fallback-placement rule design
- solver heuristic design
- runtime trigger design
- execution-order design

This stabilization therefore freezes only ownership scope, not implementation behavior.

## 4. Weak Reading Of Downstream Feasible-Outcome Surface

`feasible_outcome_surface` remains weak by design.

Its bounded meaning is only:

- legality consumes a mapping-produced reference outcome downstream
- legality may emit a downstream feasibility-resolved outcome surface
- that downstream outcome remains contract-level and implementation-neutral

It does not mean:

- the exact output identifier is frozen
- the exact runtime type is frozen
- the exact storage site is chosen
- the exact hook location is chosen
- the exact code path is chosen
- implementation is authorized

## 5. Explicit Exclusions

This contract stabilization does not open:

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

The correct bounded reading is now:

- mapping remains the assignment-structure contract layer
- legality remains the downstream feasibility contract layer
- the stabilized legality contract surface is limited to:
  - `feasibility_ownership`
  - `projection_scope`
  - `collision_boundary_scope`
  - `feasible_outcome_surface`
- those anchors remain implementation-neutral and may not be misread as frozen runtime-facing identifiers
- implementation remains closed

That is sufficient for this turn.

No runtime integration design, hook placement, storage-site choice, algorithm freeze, or viewer-semantic expansion is confirmed here.
