# VIZ Settings Truthfulness Cleanup 20260321

Status: Major item record  
Scope: `test_run` viz-only / maintained auxiliary surface  
Identity: public VIZ settings truthfulness cleanup, not runtime semantics change

## Summary

This turn aligned `test_run/test_run_v1_0.viz.settings.json` with the maintained VIZ execution path.

The work was limited to:

- restoring `background_asteroids.gas_giant_ring` to a true ring-band render instead of a line-only ellipse
- wiring `layout_height_ratios` into the maintained plot-column layout
- wiring `background_orbits.orbit_count_range` into the shared orbit-slot generation path
- unifying `vector_display_mode` handling across `test_run_entry.py` and `test_run_v1_0_viz.py`
- retiring the stale `shape_metric_*` settings block that was no longer consumed by the maintained renderer

## Retired Settings Surface

The following VIZ settings were removed because they were no longer executed by the maintained renderer:

- `shape_metric_alive_floor`
- `shape_metric_clip_enabled`
- `shape_metric_clip_bounds`
- `shape_metric_axis_quantiles`

These were historical plot-surface settings tied to older AR / WedgeRatio handling and no longer matched the current maintained plot slot map.

## Current Status

- `battle_report_builder.py`, `brf_narrative_messages.py`, and `test_run_v1_0_viz.py` remain active auxiliary surface.
- This turn did not change runtime semantics.
- This turn did not change battle-report semantics.
- This turn did not reopen old launcher paths.

## Validation

Scoped validation for this VIZ-only change:

- `python -m py_compile test_run/test_run_v1_0_viz.py test_run/test_run_entry.py`
- Agg renderer smoke image export
