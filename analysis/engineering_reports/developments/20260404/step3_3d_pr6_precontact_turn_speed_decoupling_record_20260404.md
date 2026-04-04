Scope: test-only / harness-only

Summary
- Reduced pre-contact battle movement asymmetry by removing direct unit heading-alignment speed penalty from the inactive-engagement stage of the active `v4a` line.
- `turn_speed_scale` still exists, but it is now blended in by `engagement_geometry_active_current` rather than owning unit speed equally in pre-contact and contact phases.

Why this was recorded
- This is a major item under R-11 because it materially changes active battle motion behavior on the current harness line.
- The intent is subtraction-first: remove a battle-only pre-contact movement owner that was likely pushing center units forward faster than wings during early formation transition.

Code touchpoint
- `test_run/test_run_execution.py`

Operational read
- Before engagement geometry becomes active, unit transition speed should no longer be materially reduced by per-unit heading misalignment.
- This should reduce the early center-ahead arc without introducing a new public parameter surface.
