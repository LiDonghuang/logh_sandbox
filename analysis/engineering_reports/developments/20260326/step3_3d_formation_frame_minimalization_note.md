# Step 3 3D Formation Frame Minimalization Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: Step 3 structural-draft-only formation-frame note
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: clarifies the minimum 3D frame language without opening movement or legality ownership
Mapping Impact: frame minimalization only
Governance Impact: keeps the second Step 3 topic bounded to formation-reference draft work
Backward Compatible: yes

Summary
- A 3D formation frame needs one extra ingredient beyond 2D: a minimal up-reference.
- That does not justify opening roll, bank, or a full authored attitude package.
- The minimum useful frame is still anchor + primary axis + fixed up reference + explicit degeneracy policy.
- This keeps formation reference readable without letting it turn into movement or legality.

## 1. Why 3D Needs One More Piece Than 2D

In 2D, a primary axis plus its perpendicular is enough to define the reference frame.

In 3D, that is no longer sufficient.

At minimum, a 3D formation frame needs:

- an anchor
- a primary axis
- one minimal up reference

Without that third ingredient, the frame is under-defined.

## 2. Minimum 3D Frame Expression

The minimum 3D formation frame should be expressed as:

- `anchor_mode`
- `primary_axis_source`
- `up_reference_mode`
- `frame_handedness`
- `degeneracy_policy`

Optional:

- `frame_smoothing`

This is intentionally smaller than a full attitude package.

## 3. Why This Should Not Become Full Roll / Bank / Axis Authorship

The current draft should not immediately grow into:

- authored roll
- authored bank
- second-axis intent fields
- third-axis intent fields
- full quaternion / attitude package

Reasons:

1. There is no authorized 3D movement substrate yet.
2. There is no authorized 3D legality/projection layer yet.
3. There is no need to claim aircraft-like or spacecraft-like attitude semantics at this stage.
4. A full-axis package would quietly smuggle movement and feasibility assumptions into the formation layer.

## 4. Why A Fixed Up Reference Is Enough For Now

A fixed up reference is currently enough because it allows:

- stable derivation of the lateral/depth frame
- deterministic handedness
- clear separation between reference geometry and later legality

It does **not** claim:

- full attitude authority
- bank semantics
- dynamic roll response
- final feasible orientation under all downstream constraints

## 5. How To Avoid Turning Frame Into Movement

The formation frame should answer:

- how the reference geometry is oriented

It should not answer:

- how units physically steer toward that geometry
- how quickly axes rotate
- how inertia or banking behaves

Those belong to movement integration, which is not opened in this turn.

## 6. How To Avoid Turning Frame Into Legality

The formation frame should not absorb:

- boundary clipping
- collision resolution
- projection fallback
- feasibility overrides

If those start appearing in frame language, then formation and legality have already been mixed.

## 7. Bottom Line

The minimum useful 3D formation frame is:

- anchor
- primary axis
- one minimal up reference
- deterministic handedness / degeneracy handling

Anything beyond that in this turn would be early growth toward movement or legality rather than a clean formation-reference draft.
