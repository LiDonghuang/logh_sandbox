## PR9 Phase II - Temporary Working Anchor Baseline Refresh Record

Date: 2026-04-20  
Scope: baseline refresh only  
Status: completed

### 1. Exact anchor state used

Current refreshed anchor was captured on top of:

- branch: `eng/dev-v2.1-formation-only`
- commit: `a4b5ce2b7dba`
- workspace: `dirty`

Behavior-bearing dirty paths carried into this refresh:

- `runtime/engine_skeleton.py`
- `test_run/settings_accessor.py`
- `test_run/test_run_execution.py`
- `test_run/test_run_scenario.py`
- `test_run/test_run_v1_0.runtime.settings.json`

Temporary working-anchor read:

- `coupling=1.0` is accepted here only as a temporary working anchor for
  isolation and comparison
- it is **not** being recorded as the final maintained combat-model doctrine

### 2. Refreshed baseline file paths

- [eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_battle_36v36_baseline_20260420.json](<E:/logh_sandbox/analysis/reference_notes/eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_battle_36v36_baseline_20260420.json:1>)
- [eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_battle_100v100_baseline_20260420.json](<E:/logh_sandbox/analysis/reference_notes/eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_battle_100v100_baseline_20260420.json:1>)
- [eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_neutral_36_baseline_20260420.json](<E:/logh_sandbox/analysis/reference_notes/eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_neutral_36_baseline_20260420.json:1>)
- [eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_neutral_100_baseline_20260420.json](<E:/logh_sandbox/analysis/reference_notes/eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_neutral_100_baseline_20260420.json:1>)

### 3. Battle / neutral refresh summary

Battle refresh:

- `battle_36v36`
  - frames: `500`
  - first tick / last tick: `1 / 500`
  - first contact / first damage: `61 / 61`
- `battle_100v100`
  - frames: `500`
  - first tick / last tick: `1 / 500`
  - first contact / first damage: `58 / 58`

Neutral refresh:

- `neutral_36`
  - frames: `447`
  - first tick / last tick: `1 / 447`
  - objective reached tick: `427`
  - final centroid-to-objective distance: `1.537790319789565`
- `neutral_100`
  - frames: `448`
  - first tick / last tick: `1 / 448`
  - objective reached tick: `428`
  - final centroid-to-objective distance: `1.112345481882812`

Capture surface preserved in all four refreshed anchors:

- `initial_state`
- `execution_cfg`
- `runtime_cfg`
- `observer_cfg`
- `fleet_labels`
- `fleet_colors`
- `observer_telemetry`
- `combat_telemetry`
- `position_frames`

### 4. Temporary-anchor note

This refresh should be read as:

- the current approved working anchor set for the next bounded isolation step

This refresh should **not** be read as:

- a declaration that the temporary `coupling=1.0` anchor is now final
  maintained combat doctrine
