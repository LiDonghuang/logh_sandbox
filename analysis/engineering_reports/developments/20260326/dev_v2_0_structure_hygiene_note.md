# dev_v2.0 Structure Hygiene Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: bounded structure-hygiene record
Affected Parameters: `visualization.vector_display_mode` ownership only
New Variables Introduced: none
Cross-Dimension Coupling: keeps 2D and 3D direction-mode resolution on the same layered source
Mapping Impact: none on mode meaning; duplicate ownership path retired
Governance Impact: records the only behavior-preserving structural cleanup adjacent to Step 2
Backward Compatible: yes; behavior remains aligned to the existing layered `composite` setting

Summary
- No broad refactor was performed for Step 2.
- No `viz3d_panda/` module was moved, renamed, or split.
- The only adjacent behavior-preserving structural cleanup was retiring the duplicate `vector_display_mode` surface from `test_run_v1_0.viz.settings.json`.
- 2D maintained launch and 3D viewer continue to resolve mode from the same layered settings source.
- Detailed record is kept in `test_run_vector_display_mode_source_of_truth_cleanup_20260326.md`.

## What Changed

- Removed the duplicate `vector_display_mode` entry from `test_run/test_run_v1_0.viz.settings.json`
- Kept `test_run/test_run_v1_0.settings.json` as the single source of truth
- Removed old duplicate-reader paths that could make `.viz.settings.json` look authoritative

## What Did Not Change

- Viewer launch semantics
- Viewer rendering responsibilities
- 3D container identity
- 2D maintained battle semantics
- Step 1 readability / launch alignment outcomes
