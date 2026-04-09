# LOGH Sandbox Repository Context

Status: Working Context File  
Purpose: High-level repository index for fast engineering/governance orientation
Authority: Reference only, not canonical semantics authority

## Repository Identity

- Repository: `LiDonghuang/logh_sandbox`
- Active cleanup branch: `eng/dev-v2.1-targeting-restore-cleanup`
- Maintained movement baseline: `v4a`

## Current Phase Focus

- The current mainline is **post-incident cleanup and old-family retirement** on top of the recovered `dev_v2.1` anchor.
- Active work has moved from restore/targeting repair into **subtraction-first cleanup**:
  - `v4a.restore_strength` is now a direct runtime seam
  - `battle` and `neutral` share the maintained `v4a` movement family, differing only by objective source
  - maintained battle gap now uses `fire_optimal_range` rather than raw `attack_range`
  - old 2D viz / BRF / maintained `v3a` execution surfaces have been removed from the active mainline
- Current emphasis is:
  - active-owner truth
  - old-family retirement in bounded slices
  - continued shrinkage of settings / runtime / harness surfaces

## Key Entry Documents

- `README.md`
  - top-level project identity, repo layout, active mainline summary, and current launch guidance
- `AGENTS.md`
  - root AI execution contract: frozen layers, subtraction-first cleanup, no-silent-fallback, TS handoff, and commit discipline
- `test_run/AGENTS.md`
  - local `test_run` rules, including the shared `battle` / `neutral` movement-family principle

## Key Governance / Cleanup Documents

- `docs/governance/Baseline_Replacement_Protocol_v1.0.md`
  - experiment vs baseline-replacement boundary and paired-comparison expectations
- `analysis/engineering_reports/developments/20260404/step3_3d_pr6_formal_failure_audit_20260404.md`
  - formal failure audit for the local `v4a` incident
- `analysis/engineering_reports/developments/20260404/step3_3d_pr6_old_family_retirement_policy_note_20260409.md`
  - active retirement policy for cold-path / old-family cleanup
- `analysis/engineering_reports/developments/20260404/step3_3d_pr6_cleanup_methodology_and_lessons_20260409.md`
  - methodology summary from the largest cleanup stage so far
- `docs/archive/ts_handoff_archive/`
  - long-term home for TS handoff packages

## Runtime Core Paths

- `runtime/runtime_v0_1.py`
  - runtime schema and immutable state types
- `runtime/engine_skeleton.py`
  - maintained runtime tick pipeline
  - maintained runtime movement now accepts only `v4a`
  - active `v4a` restore is direct:
    - `restore_term = restore_strength * normalize(restore_vector)`
  - active `v4a` no longer consumes:
    - legacy `v3a` movement branch body
    - `cohesion_decision_source`
    - `collapse_signal.v3_*`
    - FSR in the active `v4a` path
  - current targeting line remains bounded inside `resolve_combat()`

## Maintained Harness Paths

- `test_run/test_run_entry.py`
  - maintained headless `test_run` entrypoint
- `test_run/test_run_scenario.py`
  - settings resolution, effective-surface preparation, and scenario build
- `test_run/test_run_execution.py`
  - maintained battle / neutral harness execution host
  - shared `v4a` movement-family host for both `battle` and `neutral`
- `test_run/test_run_telemetry.py`
  - narrowed maintained telemetry helpers:
    - hostile intermix metrics
    - runtime debug payload extraction
- `test_run/settings_accessor.py`
  - layered settings access

## Active Viewer Paths

- `viz3d_panda/app.py`
  - Panda3D viewer entrypoint
- `viz3d_panda/replay_source.py`
  - replay bundle construction from `test_run` output
- `viz3d_panda/unit_renderer.py`
  - unit rendering, labels, and language-aware viewer text
- `viz3d_panda/scene_builder.py`
  - viewer scene bootstrap
- `viz3d_panda/camera_controller.py`
  - viewer camera controls
- `.vscode/launch.json`
  - current local launch entries, including the Panda3D viewer

Current viewer read:

- 3D viewer remains replay/view only
- 3D still consumes `visualization.display_language`
- old 2D viz / BRF launcher surfaces are no longer part of the active mainline

## Settings Paths

- `test_run/test_run_v1_0.settings.json`
  - thin entry settings / layer pointer
- `test_run/test_run_v1_0.runtime.settings.json`
  - maintained runtime values
  - `run_control.symmetric_movement_sync_enabled` is now the honest owner of symmetric merge control
  - `runtime.observer` is now narrowed to still-active maintained keys
- `test_run/test_run_v1_0.testonly.settings.json`
  - maintained test-only harness controls
  - `fixture.neutral.stop_radius` is the neutral-only objective termination radius
- `test_run/test_run_v1_0.settings.comments.json`
  - current comments aligned to active settings truth
- `test_run/test_run_v1_0.settings.reference.md`
  - current settings structure notes

## Current Truth Surface

- `battle` and `neutral` share the maintained `v4a` movement mechanism family
- the only intended semantic difference between them is objective source
- `stop_radius` is neutral-only termination semantics, not battle hold semantics
- maintained public settings/runtime surfaces no longer expose:
  - active `v3a` movement selectors
  - `cohesion_decision_source`
  - `collapse_signal.v3_*`
  - old 2D viz / BRF entry surfaces

## Practical Reading Order

1. `runtime/runtime_v0_1.py`
2. `runtime/engine_skeleton.py`
3. `test_run/test_run_entry.py`
4. `test_run/test_run_scenario.py`
5. `test_run/test_run_execution.py`
6. `test_run/test_run_telemetry.py`
7. `viz3d_panda/replay_source.py`
8. `viz3d_panda/app.py`

## Interpretation Guardrails

- Do not read historical names as proof that a mechanism family is still active.
- Do not read archived 2D / BRF assets as active mainline owners.
- Do not read test-only surfaces as canonical semantics.
- Do not read the Panda3D viewer as simulation owner; viewer consumes, runtime owns.
