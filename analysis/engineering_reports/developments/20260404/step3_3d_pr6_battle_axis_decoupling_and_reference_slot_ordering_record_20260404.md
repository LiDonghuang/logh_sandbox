Scope: test-only / harness-only

Summary
- Removed the direct battle-only `front_reorientation_weight -> desired_axis_hat` injection from the active `v4a` reference-surface path in `test_run/test_run_execution.py`.
- Retained battle engagement-geometry signal computation and telemetry (`effective_fire_axis`, `engagement_geometry_active`, `front_reorientation_weight`) for observation, but they no longer directly own the morphology axis on the current line.

Why this was recorded
- This is a major item under R-11 because it materially changes active mechanism availability in the current `v4a` harness line.
- The battle-only fire-plane/front reorientation signal remains observable but is no longer an active direct morphology-axis owner.

Code touchpoint
- `test_run/test_run_execution.py`

Operational read
- Battle arc/curvature should no longer be driven by the previous direct fire-plane-to-morphology-axis coupling.
