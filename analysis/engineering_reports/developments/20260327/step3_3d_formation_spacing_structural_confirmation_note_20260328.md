# Step 3 3D FormationSpacingSpec3D v0.1 Structural Confirmation Note (2026-03-28)

Engine Version: `dev_v2.0`
Modified Layer: Step 3 second-topic structural-draft-only formation-spacing confirmation
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: confirms the minimum 3D spacing language needed for reference geometry without opening legality, collision resolution, mapping, movement, extents, or viewer ownership
Mapping Impact: none; mapping remains closed in this turn
Governance Impact: confirms that the current opening stays bounded to `FormationSpacingSpec3D v0.1` only
Backward Compatible: yes

Summary
- This turn confirms only the minimum field set for `FormationSpacingSpec3D v0.1`.
- Each confirmed field remains declarative, deterministic, and upstream.
- `slot_fill_order` remains a weak reference-traversal declaration only and does not become assignment execution or remapping policy.
- Spacing remains reference intent only and does not open legality, collision resolution, mapping, movement, extents, or viewer ownership.
- No implementation path, runtime touchpoint, or viewer-semantic expansion is authorized by this note.

## 1. Confirmed Minimum Field Set

The minimum field set confirmed for `FormationSpacingSpec3D v0.1` is:

- `expected_axis_spacings_xyz`
- `spacing_mode`
- `slot_fill_order`

This is the minimum declarative spacing surface currently supported by the repo-side formation draft.

## 2. Bounded Intended Reading

The current bounded intended reading is:

- `expected_axis_spacings_xyz`
  - intended spacing along the reference axes only
  - reference-intent language only
  - not feasibility enforcement
  - not an extents solver
  - not a collision-resolution package

- `spacing_mode`
  - spacing interpretation mode only
  - declarative only
  - not legality policy
  - not projection or fallback policy

- `slot_fill_order`
  - deterministic traversal order for reference slots only
  - upstream-only
  - not unit-to-slot assignment execution
  - not remapping or reflow control

Each field remains declarative and upstream.

None of these fields authorizes downstream legality, mapping, runtime steering, or viewer ownership.

## 3. Weak Reading Of `slot_fill_order`

`slot_fill_order` is confirmed only under a weak reference-order reading:

- deterministic reference traversal order only
- upstream-only
- reference-slot-local only

It must not be read as:

- assignment execution
- mapping policy
- reflow logic
- remapping trigger logic
- `expected_position_map` production logic

If `slot_fill_order` begins answering which unit takes which slot or when reassignment occurs, it has already crossed into mapping scope.

## 4. Explicit Exclusion Statement

This structural confirmation does not open:

- legality / projection semantics
- collision-resolution semantics
- mapping semantics
- movement semantics
- viewer ownership semantics
- extents package semantics

More specifically, this note does not authorize:

- feasibility
- projection
- collision handling
- boundary clipping
- legality override
- fallback placement logic
- mapping mode
- allow_reflow policy
- unit-to-slot assignment execution
- remapping trigger logic
- steering behavior
- turning dynamics
- temporal response
- inertia semantics
- doctrine / posture movement reading
- rendering ownership
- `viz3d_panda/` semantic authority
- camera/display attributes
- glyph/display/layout visualization semantics
- principal extents targets
- anisotropy ratio packages
- volume semantics

The following also remain out of scope for this spacing opening:

- legality / feasibility fields
- collision / boundary fields
- doctrine / posture semantics
- target preference semantics
- viewer rendering fields
- camera hints
- glyph / display attributes

## 5. Boundary Bottom Line

The correct bounded reading remains:

- objective stays upstream and already answers where to go
- frame is already confirmed separately
- layout is already confirmed separately
- spacing answers only minimum declarative reference intent
- mapping remains closed
- legality remains closed
- implementation remains closed

That is sufficient for this turn.

No downstream ownership is opened here.

No runtime positioning design, implementation path, or viewer-semantic expansion is confirmed by this note.
