# dev_v2.0 Visual Refinement V1 Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: additive `viz3d_panda/` viewer-local display layer only
Affected Parameters: viewer-local token alpha, viewer-local fixed fleet base colors, viewer-local fire-link display mode/style
New Variables Introduced: `fire_link_mode` (`minimal` / `full`)
Cross-Dimension Coupling: none; consumes existing replay/target data only
Mapping Impact: none; no battle or targeting semantics changed
Governance Impact: executes Round V1 of the limited visual refinement window only
Backward Compatible: yes; runtime/replay ownership unchanged

Summary
- Round V1 keeps the semi-transparent cluster token and retunes its base colors for better stability under alpha.
- Viewer fleet colors remain fixed `blue vs red`, but move to deeper, more saturated base colors.
- Token alpha is reduced from the earlier heavier transparency setting to a steadier `0.72`.
- Fire-links remain present, but are demoted into a thinner, lower-alpha subordinate layer.
- The earlier raised two-segment arc is removed; fire-links now render as straight, laser-like links.
- A minimal viewer-local display mode surface is added: `minimal` and `full`.
- Default mode is `minimal`, so links stay visible without dominating the frame.
- This round does not alter target ownership, stop semantics, replay format, or Step 3 objective draft identity.

## Scope

This note records Round V1 only.

It does not authorize or imply:

- battle / combat semantics change
- targeting semantics change
- stop semantics change
- replay ownership change
- viewer framework expansion

## Round V1 Changes

### 1. Token color retune under transparency

The viewer keeps fixed fleet-side colors, but changes them to deeper base colors so the semi-transparent wedge token stays readable on the dark scene background:

- fleet `A`: `#2a63b8`
- fleet `B`: `#b6404a`

The goal is not stylistic variety. The goal is simply to avoid the earlier washed-out pale red / pale blue look when alpha blending is active.

### 2. Token alpha retune

Token alpha is now tuned to `0.72`.

This keeps the token clearly semi-transparent without drifting toward a chalky or gray result.

### 3. Fire-link visual demotion

Fire-links are retained, but their visual role is reduced:

- thinner line treatment
- much lower alpha than token bodies
- no raised pseudo-parabolic midpoint
- straight source-to-target beam cue instead of a dominant arc

This makes the token remain the primary object, while the link stays a light combat-relation hint only.

### 4. Viewer-local fire-link mode support

Two viewer-local display modes now exist:

- `minimal`
- `full`

Default is `minimal`.

`minimal` is intended for ordinary viewing.
`full` is retained for closer inspection when the human wants the link cue to read a little stronger.

## Boundary Check

Round V1 remains within viewer-local display only.

It does not:

- reinterpret combat ownership
- reinterpret target meaning
- add a new replay protocol
- add a new simulation settings stack
- alter Step 3 objective contract documents
