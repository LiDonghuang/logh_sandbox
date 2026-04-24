# step3_3d_pr6_old_family_retirement_round9_entry_reroot_and_2d_artifact_removal_20260409

## Scope
- `test_run` active entry reroot
- removal of retired 2D visualization and battle-report surfaces
- removal of old 2D `test_run_entry` launchers

## What changed
- rerooted `test_run/test_run_entry.py` to a headless/mainline entry:
  - removed 2D animation path
  - removed 2D map-export path
  - removed BRF battle-report export path
- deleted:
  - `test_run/test_run_v1_0_viz.py`
  - `test_run/test_run_v1_0.viz.settings.json`
  - `test_run/battle_report_builder.py`
  - `test_run/brf_narrative_messages.py`
- removed the three legacy `test_run_entry` launchers from `.vscode/launch.json`
- narrowed `test_run/test_run_v1_0.settings.json` and its truth surfaces so only `visualization.print_tick_summary` remains live

## Why this counts as real subtraction
- active entrypoint is materially smaller
- dead visualization/report/export surfaces are deleted, not hidden
- old launcher surface is smaller
- comments/reference no longer claim those 2D files are part of the maintained active path

## Explicit boundary
- this round does not touch Panda3D `viz3d_panda/*`
- this round does not delete the top-level `launch_dev_v2_0_*.bat` files
- this round does not remove `symmetric_movement_sync_enabled`

## Follow-up
- the next larger deletion round can target the remaining maintained legacy `v3a` execution path and any residual support seams such as `symmetric_movement_sync_enabled`
