# LOGH Sandbox Repository Context

Status: Working Context File  
Purpose: High-level repository index for governance-side reading and fast navigation  
Authority: Reference only, not canonical semantics authority

## Repository Identity

- Repository: `LiDonghuang/logh_sandbox`
- Primary development branch: `dev_v1.1`

## Current Phase Focus

- Phase A: cleanup and structural simplification
- A1 hostile penetration line freeze completed as working/stopped/failed status separation
- A3 settings layering completed
- A5 `test_run` harness simplification in progress

Current emphasis is not personality expansion.

## Runtime Core Paths

- `runtime/runtime_v0_1.py`
  - runtime schema and immutable state types
- `runtime/engine_skeleton.py`
  - tick pipeline and core runtime behavior

## Test Harness Paths

- `test_run/test_run_v1_0.py`
  - engine-facing harness core and shared helper surface
- `test_run/test_run_main.py`
  - launcher / orchestration entry
- `test_run/test_run_experiments.py`
  - simulation execution and telemetry collection
- `test_run/settings_accessor.py`
  - layered settings loading/access

## Settings Paths

- `test_run/test_run_v1_0.settings.json`
  - thin entry settings / layer pointer
- `test_run/test_run_v1_0.runtime.settings.json`
  - runtime values
- `test_run/test_run_v1_0.testonly.settings.json`
  - test-only harness controls
- `test_run/test_run_v1_0.viz.settings.json`
  - visualization values
- `test_run/test_run_v1_0.settings.comments.json`
  - comments aligned to active settings
- `test_run/test_run_v1_0.settings.reference.md`
  - settings structure notes

## Visualization Path

- `test_run/test_run_v1_0_viz.py`
  - rendering, plots, animation/export display layer

## Key Current Records

- `docs/Global_Road_Map_Engagement_to_Personality_20260318.md`
- `docs/a5_iteration0_baseline_anchor_20260318.md`
- `docs/a5_iteration0_baseline_anchor_20260318.json`
- `docs/test_run_harness_cleanup_record_20260319.md`
- `docs/phase_a_governance_update_20260319.md`
- `docs/test_run_anchor_regression_policy_20260319.md`

## Reading Order

1. `runtime/runtime_v0_1.py`
2. `runtime/engine_skeleton.py`
3. `test_run/test_run_v1_0.py`
4. `test_run/test_run_main.py`
5. `test_run/test_run_experiments.py`
6. `test_run/test_run_v1_0_viz.py`
