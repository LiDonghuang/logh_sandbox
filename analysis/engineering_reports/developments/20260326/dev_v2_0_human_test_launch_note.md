# dev_v2.0 Human Test Launch Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: additive 3D viewer bootstrap / human test surface
Affected Parameters: none beyond viewer `--steps` launch override
New Variables Introduced: none
Cross-Dimension Coupling: existing 2D output is replayed in the 3D viewer bootstrap path
Mapping Impact: none
Governance Impact: supports bounded human review of readability and launch semantics
Backward Compatible: yes

Summary
- Default viewer launch now respects the current layered `max_time_steps` contract.
- Explicit `--steps` override still works and uses the same tick meaning.
- Human review should check the new wedge token, HP bucket size differences, and overlay semantics label.
- This note stays at the viewer/bootstrap layer and does not claim any 3D mechanism progress.

## Default Human Launch

From repo root:

```powershell
.\launch_dev_v2_0_viewer.bat
```

Expected behavior:

- viewer uses the current layered settings stop semantics
- on the current repo settings, that means the launch should no longer be silently capped at `240`
- overlay should show `sim_limit=settings:<value>`

## Explicit Override Launch

Example:

```powershell
.\launch_dev_v2_0_viewer.bat --steps 180
```

Expected behavior:

- simulation is explicitly capped at `180` ticks
- overlay should show `sim_limit=override:180`
- replay generation should stop according to that same tick override, not a viewer-only reinterpretation

## Glyph Readability Check

During human inspection, verify:

- units read as semi-transparent cluster tokens, not thin wire arrows
- heading is still obvious from wedge direction
- large-HP tokens are visibly larger than low-HP tokens
- fleet color remains readable
- glyphs have body volume rather than nearly-flat line identity

Reference artifact generated in this turn:

- `analysis/engineering_reports/developments/20260326/dev_v2_0_viewer_readability_pass1_offscreen.png`

## Recommended Review Lens

This pass should be judged as:

- readability improvement
- human launch semantics correction

It should not be judged as:

- 3D combat progress
- 3D movement semantics progress
- new replay protocol progress
