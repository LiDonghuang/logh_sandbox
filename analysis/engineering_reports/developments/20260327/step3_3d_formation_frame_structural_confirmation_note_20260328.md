# Step 3 3D FormationFrameSpec3D v0.1 Structural Confirmation Note (2026-03-28)

Engine Version: `dev_v2.0`
Modified Layer: Step 3 second-topic structural-draft-only formation-frame confirmation
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: confirms the minimum 3D frame language needed for reference geometry without opening movement, mapping, legality, or viewer ownership
Mapping Impact: none; mapping remains closed in this turn
Governance Impact: confirms that the current opening stays bounded to `FormationFrameSpec3D v0.1` only
Backward Compatible: yes

Summary
- This turn confirms only the minimum field set for `FormationFrameSpec3D v0.1`.
- The current bounded reading remains: fleet-centroid anchor, objective-derived primary axis, fixed global up, explicit handedness, and explicit deterministic degeneracy handling.
- `fixed global up` is sufficient for this opening turn, but it is not declared here as permanent universal doctrine.
- `frame_smoothing` may remain only as an optional weak stability field and must not become pseudo-movement or temporal response semantics.
- Movement, mapping, legality/projection, and viewer ownership remain explicitly closed.

## 1. Confirmed Minimum Field Set

The minimum field set confirmed for `FormationFrameSpec3D v0.1` is:

- `anchor_mode`
- `primary_axis_source`
- `up_reference_mode`
- `frame_handedness`
- `degeneracy_policy`

Optional only:

- `frame_smoothing`

This is the smallest useful 3D frame expression currently supported by the repo-side formation draft and frame minimalization read.

## 2. Current Minimal Accepted Reading

The current bounded reading is confirmed as:

- `anchor_mode = fleet-centroid anchored`
- `primary_axis_source = objective-derived forward/reference axis`
- `up_reference_mode = fixed global up only`
- `frame_handedness = explicit and deterministic`
- `degeneracy_policy = explicit, bounded, deterministic`

This reading is intentionally narrow.

It confirms only how the reference frame is derived for formation geometry.

It does not authorize authored roll, bank, full attitude packages, independently authored secondary/tertiary axes, or downstream feasibility behavior.

## 3. Why Fixed Global Up Is Sufficient In This Opening

`fixed global up` is sufficient for this opening turn because it provides:

- the minimum extra ingredient needed to disambiguate a 3D frame beyond the 2D case
- stable derivation of the lateral/depth frame
- deterministic handedness support
- clean separation from later legality or movement-facing questions

This note does not declare `fixed global up` to be permanent universal doctrine.

It is confirmed here only as the current minimum accepted read for the opening `FormationFrameSpec3D v0.1` turn.

## 4. Weak Optional Reading Of Frame Smoothing

`frame_smoothing` may remain as an optional field only under a weak bounded reading:

- stability-only
- bounded
- reference-frame-local
- non-movement-facing

`frame_smoothing` must not be read as:

- pseudo-inertia
- axis-rotation behavior
- temporal controller behavior
- steering semantics
- movement response policy

If `frame_smoothing` starts answering how the fleet turns rather than how the reference frame stays locally stable, it has already exceeded the allowed scope of this opening turn.

## 5. Explicit Exclusion Statement

This structural confirmation does not open:

- movement semantics
- mapping semantics
- legality / projection semantics
- viewer ownership semantics

More specifically, this note does not authorize:

- steering behavior
- axis rotation dynamics
- inertia semantics
- bank / roll response
- slot assignment execution
- reflow policy
- mapping mode
- `expected_position_map` production logic
- feasibility
- projection
- collision handling
- boundary clipping
- legality override
- replay protocol ownership
- formation semantics inside `viz3d_panda/`

## 6. Boundary Bottom Line

The correct bounded reading remains:

- objective stays upstream and already answers where to go
- `FormationFrameSpec3D v0.1` answers only minimum 3D reference-frame language
- mapping remains closed
- legality remains closed

That is sufficient for this turn.

No broader formation, runtime, or viewer-semantic opening is confirmed here.
