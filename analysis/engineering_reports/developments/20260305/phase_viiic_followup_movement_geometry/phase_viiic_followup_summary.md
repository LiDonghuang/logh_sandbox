# Phase VIII-C Follow-up Summary

## Scope
- FR x MB interaction maps from B3.
- Movement geometry diagnostics (v1 vs v3a).
- High-FR stray diagnostics (observer-only).
- First-six archetype anchor drift review.

## Outputs
- `fr_mb_interaction_maps.md`
- `movement_v1_vs_v3a_geometry_comparison.csv`
- `high_fr_stray_diagnostics.csv`
- `anchor_drift_review_first6.md`

## Run Notes
- Replayed runs: 108
- Replay mode: observer-enabled, frame_stride=10, no BRF export.
- Runtime baseline settings source: `E:/logh_sandbox/analysis/test_run_v1_0.settings.json`
- Plot backend note: `matplotlib` unavailable in this environment; heatmaps exported as `*.matrix.csv`.

## Key quick read
- Use `movement_v1_vs_v3a_geometry_comparison.csv` for cell-level v1/v3a geometry means.
- Use `high_fr_stray_diagnostics.csv` for FR=8 outlier proxies (distance/neighbor/connectivity).
- Use heatmap PNGs for FR x MB structural interaction visualization.
