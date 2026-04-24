## eng/dev-v2.1-formation-only Phase II Primary Baseline Capture Index

Baseline anchor:
- Branch: `eng/dev-v2.1-formation-only`
- Commit: `a4b5ce2b7dba`
- Workspace dirty: `true`

Purpose:
- Preserve the current accepted Phase II working baseline after the first target-owner reroot slice.
- Provide full per-tick capture facts for later paired comparison review after major runtime behavior changes.

Capture source:
- Active owner path: [runtime/engine_skeleton.py](e:/logh_sandbox/runtime/engine_skeleton.py:1)
- Harness capture surface: [test_run/test_run_execution.py](e:/logh_sandbox/test_run/test_run_execution.py:1414)
- Entry/orchestration surface: [test_run/test_run_entry.py](e:/logh_sandbox/test_run/test_run_entry.py:40)

Files:
- [eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_battle_36v36_baseline_20260419.json](e:/logh_sandbox/analysis/reference_notes/eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_battle_36v36_baseline_20260419.json)
- [eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_battle_100v100_baseline_20260419.json](e:/logh_sandbox/analysis/reference_notes/eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_battle_100v100_baseline_20260419.json)
- [eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_neutral_36_baseline_20260419.json](e:/logh_sandbox/analysis/reference_notes/eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_neutral_36_baseline_20260419.json)
- [eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_neutral_100_baseline_20260419.json](e:/logh_sandbox/analysis/reference_notes/eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_neutral_100_baseline_20260419.json)
- [eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_baseline_capture_manifest_20260419.json](e:/logh_sandbox/analysis/reference_notes/eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_baseline_capture_manifest_20260419.json)

Each scenario JSON contains:
- `initial_state`
- `execution_cfg`
- `runtime_cfg`
- `observer_cfg`
- `observer_telemetry`
- `combat_telemetry`
- `position_frames`
- `fleet_labels`
- `fleet_colors`

Important notes:
- These four captures are the current Phase II primary baseline set for paired comparison review.
- `analysis/reference_notes/dev_v2_1_a0d0b46_*.json` remains a historical anchor, not the current primary baseline.
- `position_frames` starts at tick `1`; `initial_state` preserves tick `0` facts.
- `position_frames` includes the maintained viewer-facing frame facts: per-unit position, orientation, velocity, hit-point values, `targets`, `fleet_body_summary`, and `runtime_debug`.
- This capture reflects the accepted working tree state on top of the listed HEAD commit, not a clean-HEAD snapshot.
