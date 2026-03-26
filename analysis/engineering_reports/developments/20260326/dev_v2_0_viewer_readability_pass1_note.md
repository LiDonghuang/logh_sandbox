# dev_v2.0 Viewer Readability Pass 1 Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: additive 3D viewer scaffold / viewer rendering layer
Affected Parameters: viewer-local glyph shape, viewer-local HP size buckets, viewer-local token alpha
New Variables Introduced: viewer-only `capture_hit_points` execution override, five discrete HP size buckets
Cross-Dimension Coupling: existing 2D active-surface output is still the source; viewer consumes an enriched in-memory replay bundle only
Mapping Impact: none on canonical mapping; HP is mapped to token size only inside viewer rendering
Governance Impact: remains inside authorized 3D Viewer Readability Pass 1 scope
Backward Compatible: yes; default 2D harness behavior is unchanged

Summary
- Thin `LineSegs` arrow glyphs were removed as the viewer's primary unit identity.
- Each unit is now rendered as a single semi-transparent 3D wedge cluster token.
- Heading remains readable through wedge orientation instead of line-arrow identity.
- HP is expressed only through five discrete size buckets.
- Fleet color is retained; HP does not alter color or alpha.
- The helper touch in `test_run/test_run_execution.py` is viewer-only and opt-in.

## Glyph Change

The previous token was a thin line-arrow template updated every frame via direct transform. It carried heading, but it still read as a restless wireframe marker rather than a fleet cluster token.

This pass replaces that with a single solid wedge token:

- one token per unit
- no body+nose split
- no multi-part glyph family
- no single-ship model identity

The wedge is tapered along heading, has visible height, and sits slightly above the scene plane so it reads as a volumetric cluster marker rather than a line sketch.

## HP Mapping

HP is now mapped only to token size, using five discrete buckets:

- 81-100%
- 61-80%
- 41-60%
- 21-40%
- 1-20%

No HP mapping was added to:

- color
- alpha
- outline
- brightness

This keeps the readability change narrow and prevents the token from becoming a multi-channel status display too early.

## Transparency And Heading

Token alpha is fixed at approximately `0.8`.

Heading is still preserved, but the wedge geometry itself now carries that direction. The viewer no longer relies on a thin arrow line to communicate orientation.

## Helper Boundary

Current `position_frames` did not already carry per-unit HP. To satisfy the authorized HP size mapping without redesigning the persisted replay contract, this turn adds one viewer-only execution override:

- `capture_hit_points`

It is:

- default `False`
- used only by `viz3d_panda/replay_source.py`
- not part of the default 2D launcher surface
- not a battle-semantics change
