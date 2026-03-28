# Step 3 3D FormationLayoutSpec3D v0.1 Structural Confirmation Note (2026-03-28)

Engine Version: `dev_v2.0`
Modified Layer: Step 3 second-topic structural-draft-only formation-layout confirmation
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: confirms the minimum 3D layout language needed for reference geometry without opening mapping, legality, movement, spacing, or viewer ownership
Mapping Impact: none; mapping remains closed in this turn
Governance Impact: confirms that the current opening stays bounded to `FormationLayoutSpec3D v0.1` only
Backward Compatible: yes

Summary
- This turn confirms only the minimum field set for `FormationLayoutSpec3D v0.1`.
- Each confirmed field remains declarative and reference-only.
- `slot_identity_policy` remains a weak upstream identity-stability expectation only and does not become assignment execution or reflow policy.
- Layout remains reference geometry language only and does not open mapping, legality/projection, movement, spacing, or viewer ownership.
- No implementation path, runtime touchpoint, or viewer-semantic expansion is authorized by this note.

## 1. Confirmed Minimum Field Set

The minimum field set confirmed for `FormationLayoutSpec3D v0.1` is:

- `layout_family`
- `aspect_ratio_target`
- `depth_layer_policy`
- `rotation_policy`
- `centering_policy`
- `slot_identity_policy`

This is the minimum declarative layout surface currently supported by the repo-side formation draft.

## 2. Bounded Intended Reading

The current bounded intended reading is:

- `layout_family`
  - reference family only
  - not a runtime generator
  - not a family-registry opening

- `aspect_ratio_target`
  - coarse and declarative only
  - not an extents solver
  - not a volume/anisotropy package

- `depth_layer_policy`
  - allowed only because 3D needs a depth reading
  - declares whether and how depth layering is represented in the reference layout
  - does not open extents, volume, or legality semantics

- `rotation_policy`
  - aligns the layout to the already-defined frame
  - does not define turning behavior
  - does not define temporal rotation response

- `centering_policy`
  - declares how the layout is centered around the chosen anchor
  - does not open projection fallback
  - does not open legality override

- `slot_identity_policy`
  - deterministic and conservative upstream identity expectation only
  - does not define assignment execution logic

Each field remains declarative.

None of these fields authorizes downstream runtime, mapping, or viewer ownership.

## 3. Weak Reading Of `slot_identity_policy`

`slot_identity_policy` is confirmed only under a weak upstream reading:

- identity-stability expectation only
- deterministic and conservative only
- upstream-only

It must not be read as:

- mapping implementation
- reflow policy
- unit-to-slot assignment execution
- remapping trigger logic
- `expected_position_map` production logic

If `slot_identity_policy` begins answering who goes to which slot or when reassignment occurs, it has already crossed into mapping scope.

## 4. Explicit Exclusion Statement

This structural confirmation does not open:

- mapping semantics
- legality / projection semantics
- movement semantics
- viewer ownership semantics
- spacing confirmation

More specifically, this note does not authorize:

- mapping mode
- allow_reflow policy
- unit-to-slot assignment execution
- remapping trigger logic
- feasibility
- projection
- collision handling
- boundary clipping
- legality override
- fallback placement logic
- steering behavior
- temporal rotation response
- turning dynamics
- inertia semantics
- doctrine / posture movement reading
- rendering ownership
- `viz3d_panda/` semantic authority
- camera/display attributes
- glyph/display/layout visualization semantics

The following also remain out of scope for this layout opening:

- principal extents targets
- anisotropy ratio packages
- target preference semantics
- doctrine / posture semantics
- viewer rendering fields
- camera hints
- glyph / display attributes

## 5. Boundary Bottom Line

The correct bounded reading remains:

- objective stays upstream and already answers where to go
- frame is already confirmed separately
- layout answers only minimum declarative reference-geometry language
- spacing remains closed
- mapping remains closed
- legality remains closed

That is sufficient for this turn.

No downstream ownership is opened here.

No runtime positioning design, implementation path, or viewer-semantic expansion is confirmed by this note.
