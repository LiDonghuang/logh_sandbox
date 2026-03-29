# test_run Post-Resolution Hold Steps Runtime Surface Note

Engine Version
- dev_v2.0 test_run harness

Modified Layer
- test_run launcher / scenario / settings surface only

Affected Parameters
- `run_control.post_resolution_hold_steps`
- removal of duplicate `test_run_v1_0.viz.settings.json::post_elimination_extra_ticks`

New Variables Introduced
- none in runtime core

Cross-Dimension Coupling
- none

Mapping Impact
- none

Governance Impact
- small public `test_run` configuration-surface expansion
- no runtime mechanism redesign

Backward Compatible
- yes
- default remains `10`

Summary
- `run_control.post_resolution_hold_steps` is now the authoritative launcher-consumed hold window after the first resolved stop condition.
- It applies to both battle winner hold and `neutral_transit_v1` objective-arrival hold.
- The setting is validated as `>= 0`.
- `test_run_entry.py` now prefers the prepared execution value so visual launch no longer silently reinterprets this hold window through the viz layer.
- `neutral_transit_v1` now accepts an objective point that is strictly coincident with the initial fleet centroid; in that harness-only case, the expected-position reference falls back to the initial fleet forward orientation instead of failing fast.
