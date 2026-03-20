# `test_run_v1_0.py` Exit Report (2026-03-20)

Status: exit report  
Scope: maintained helper-surface migration / old launcher retirement  
Classification: harness-only structural follow-up / non-runtime-semantic

## 1. Outcome

This round achieved the preferred end condition:

- `test_run/test_run_v1_0.py` was physically deleted

Additional retirement result:

- `test_run/test_run_experiments.py` was also physically deleted

`test_run/test_run_main.py` had already been deleted in an earlier round.

## 2. What Was Migrated Out Of `test_run_v1_0.py`

### A. Scenario / Build / Archetype Helper Surface

Moved into `test_run/test_run_scenario.py`:

- `load_metatype_settings(...)`
- `resolve_archetype(...)`
- `resolve_fleet_archetype_data(...)`
- `generate_yang_parameters(...)`
- `to_personality_parameters(...)`
- fleet display/color/avatar helper family
- `parse_test_mode(...)`
- `test_mode_label(...)`
- `resolve_runtime_decision_source(...)`
- `resolve_movement_model(...)`
- project/archetype helper constants used by maintained scenario preparation

### B. Execution / Engine-Adjacent Helper Surface

Moved into `test_run/test_run_execution.py`:

- `FormationRigidityFirstReadProxy`
- `TestModeEngineTickSkeleton`
- engine-adjacent movement/contact/bridge/collapse default constants still required by maintained runtime handoff

### C. Launcher / Export / Plot Helper Surface

Moved into `test_run/test_run_entry.py`:

- env flag parsing for video export
- timestamped video output path resolution
- plot-profile resolution for maintained launcher use
- launcher-local export constants

## 3. Unique Final Ownership

Final canonical ownership after migration:

- scenario/build helper ownership: `test_run/test_run_scenario.py`
- engine-adjacent harness skeleton ownership: `test_run/test_run_execution.py`
- launcher/export/viz orchestration ownership: `test_run/test_run_entry.py`
- BRF assembly ownership: `test_run/battle_report_builder.py`

No maintained code path should now import `test_run/test_run_v1_0.py`.

## 4. Deletion Status

Deletion status after migration:

- `test_run/test_run_v1_0.py`: deleted
- `test_run/test_run_experiments.py`: deleted

Code-path verification:

- no active code imports of `test_run_v1_0` remained under `test_run/` or `.vscode/`
- no active code imports of `test_run_experiments` remained under `test_run/` or `.vscode/`

Historical `analysis/...` scripts were not treated as maintained compatibility constraints in this round.

## 5. Remaining Blockers

There is no remaining blocker preventing deletion of the old launcher files above.

The current remaining heavy files in `test_run/` are no longer old launcher shells.

They are active auxiliary surface:

- `test_run/battle_report_builder.py`
- `test_run/brf_narrative_messages.py`
- `test_run/test_run_v1_0_viz.py`

## 6. Validation

Validation run after deletion:

- `python -m py_compile test_run/test_run_entry.py test_run/test_run_scenario.py test_run/test_run_execution.py test_run/battle_report_builder.py test_run/test_run_anchor_regression.py`
- `python test_run/test_run_anchor_regression.py`
- maintained launcher smoke through `test_run/test_run_entry.py`

Observed state:

- routine anchor remained `mismatch_count=0`
- maintained launcher still ran
- maintained launcher still exported BRF
- maintained launcher still called the existing renderer

No runtime semantics changed in this turn.
