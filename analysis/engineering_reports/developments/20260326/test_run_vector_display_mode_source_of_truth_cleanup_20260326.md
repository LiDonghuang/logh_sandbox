# test_run Vector Display Mode Source-of-Truth Cleanup (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: test harness configuration surface / viewer alignment record
Affected Parameters: `visualization.vector_display_mode`
New Variables Introduced: none
Cross-Dimension Coupling: 2D `test_run` and 3D `viz3d_panda` now read the same layered visualization source without a duplicate `.viz.settings` copy
Mapping Impact: no change to mode meaning; ownership only
Governance Impact: narrows a public `test_run` configuration surface and removes a misleading duplicate path
Backward Compatible: behavior remains the same for valid layered settings; duplicate `.viz.settings` ownership is retired

Summary
- The authoritative source for unit-direction display mode is now only `test_run/test_run_v1_0.settings.json` under `visualization.vector_display_mode`.
- The duplicate `vector_display_mode` entry in `test_run/test_run_v1_0.viz.settings.json` was removed.
- 2D maintained launch continues to resolve mode from layered settings.
- 3D viewer continues to resolve mode from the same layered settings.
- A map-export-only hard-coded `"effective"` callsite was replaced with the same layered source.
- This is a settings ownership cleanup, not a display-mechanism redesign.
