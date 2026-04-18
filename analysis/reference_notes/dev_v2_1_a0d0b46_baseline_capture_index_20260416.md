## dev_v2.1 Baseline Capture Index

Baseline anchor:
- Branch: `dev_v2.1`
- Commit: `a0d0b46`

Purpose:
- Preserve a directly runnable/reference baseline before returning to the frozen investigation branch.
- Provide per-tick facts for human comparison against later formation/locomotion variants.

Capture source:
- Active owner path: [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1)
- Harness capture surface: [test_run/test_run_execution.py](E:/logh_sandbox/test_run/test_run_execution.py:1423)
- Entry/orchestration surface: [test_run/test_run_entry.py](E:/logh_sandbox/test_run/test_run_entry.py:40)

Files:
- [dev_v2_1_a0d0b46_battle_100v100_baseline_20260416.json](E:/logh_sandbox/analysis/reference_notes/dev_v2_1_a0d0b46_battle_100v100_baseline_20260416.json)
- [dev_v2_1_a0d0b46_battle_36v36_baseline_20260416.json](E:/logh_sandbox/analysis/reference_notes/dev_v2_1_a0d0b46_battle_36v36_baseline_20260416.json)
- [dev_v2_1_a0d0b46_neutral_100_baseline_20260416.json](E:/logh_sandbox/analysis/reference_notes/dev_v2_1_a0d0b46_neutral_100_baseline_20260416.json)
- [dev_v2_1_a0d0b46_neutral_36_baseline_20260416.json](E:/logh_sandbox/analysis/reference_notes/dev_v2_1_a0d0b46_neutral_36_baseline_20260416.json)
- [dev_v2_1_a0d0b46_baseline_capture_manifest_20260416.json](E:/logh_sandbox/analysis/reference_notes/dev_v2_1_a0d0b46_baseline_capture_manifest_20260416.json)

Each scenario JSON contains:
- `prepared_summary`
- `execution_cfg`
- `runtime_cfg`
- `observer_cfg`
- `initial_state`
- `observer_telemetry`
- `combat_telemetry`
- `position_frames`
- `fleet_labels`
- `fleet_colors`

Important notes:
- `position_frames` starts at tick `1`, matching the maintained harness capture surface.
- To compensate for the missing tick `0` replay frame, each JSON also includes `initial_state`.
- `position_frames` includes the maintained viewer-facing frame facts: per-unit position, orientation, velocity, hit-point values, `targets`, `fleet_body_summary`, and `runtime_debug`.
- I did not duplicate the entire `runtime/` source tree into `reference_notes` because the baseline git anchor `a0d0b46` is already stable and directly queryable. If you want literal source snapshots copied into `reference_notes`, that can be done as a separate bounded step.
