# LOGH Sandbox System Map

Status: Working System Map  
Purpose: Fast structural orientation for engineering/governance reading
Authority: Reference only, not canonical semantics authority

## Layer Map

### 1. Schema Layer

- `runtime/runtime_v0_1.py`
- Defines the maintained runtime state/data contracts:
  - `PersonalityParameters` (high-level metadata contract only; not attached to `FleetState`)
  - `Vec2`
  - `UnitState`
  - `FleetState`
  - `BattleState`

### 2. Runtime Layer

- `runtime/engine_skeleton.py`
- Maintained tick pipeline:
  - `evaluate_cohesion`
  - `evaluate_target`
  - `evaluate_utility`
  - `integrate_movement`
  - `resolve_combat`

Current maintained runtime read:

- maintained movement model is `v4a` only
- maintained tick-stage ownership is runtime-owned again:
  - `step`
  - `evaluate_target`
  - `integrate_movement`
  - `resolve_combat`
- active `v4a` restore is direct:
  - `restore_term = restore_strength * normalize(restore_vector)`
- the current working branch is a PR#9 continuation carrier for:
  - Formation coarse-body/reference ownership
  - bounded low-level locomotion realization
  - paired comparison against `dev_v2.1 / a0d0b46`
- current branch-local runtime slices include:
  - forward fire-cone target selection in `resolve_combat()`
  - low-level locomotion realization limits in `integrate_movement()`
  - split retreat carriers:
    - `last_target_direction` as reference axis
    - `movement_command_direction` as signed movement command
- active `v4a` no longer depends on:
  - maintained `v3a` movement branch body
  - `cohesion_decision_source`
  - `collapse_signal.v3_*`
  - FSR in the active `v4a` path
- targeting is opened in bounded form inside `resolve_combat()`
- the merged cleanup/structural-tightening wave is complete on `dev_v2.1`

### 3. Maintained Harness Spine

- `test_run/test_run_entry.py`
  - maintained headless entrypoint
- `test_run/test_run_scenario.py`
  - settings resolution and scenario/effective-surface build
- `test_run/test_run_execution.py`
  - maintained execution/orchestration host
  - shared `v4a` movement-family host for `battle` and `neutral`
  - battle/fixture bundles remain as carriers, while maintained tick semantics are back in runtime
  - replay/baseline capture path is also used for paired comparison against `dev_v2.1`
- `test_run/test_run_telemetry.py`
  - narrowed maintained telemetry helpers only
- `test_run/settings_accessor.py`
  - layered settings access

Current maintained harness read:

- `battle` and `neutral` share one `v4a` movement family
- only objective source should differ
- `stop_radius` is neutral-only objective termination semantics
- battle gap base now uses `fire_optimal_range`
- `test_mode` is retired from the maintained public surface
- harness-side bundle state is being narrowed where runtime/observer already own the active path
- harness currently wires two new maintained runtime surfaces:
  - `runtime.physical.fire_control.fire_cone_half_angle_deg`
  - `runtime.physical.movement_low_level.*`

### 4. Settings Layer

- `test_run/test_run_v1_0.settings.json`
- `test_run/test_run_v1_0.runtime.settings.json`
- `test_run/test_run_v1_0.testonly.settings.json`
- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`

Current maintained settings read:

- runtime selector is `v4a` only
- test-only hostile-contact selector is `off | hybrid_v2`
- `runtime.metatype.*` remains a scenario-level Yang/personality sampling interface only
- `run_control.symmetric_movement_sync_enabled` owns symmetric merge control
- `runtime.observer` has been narrowed to still-active maintained keys
- runtime now also exposes:
  - fire-control cone width
  - low-level locomotion realization limits
- old public `v3a` selector surfaces are no longer part of the maintained mainline
- `testonly.runtime.movement.v4a.*` is now structured by candidate-owned groups:
  - `restore`
  - `reference`
  - `transition`
  - `battle`
  - `engagement`

### 5. Viewer / Replay Layer

- `viz3d_panda/app.py`
- `viz3d_panda/replay_source.py`
- `viz3d_panda/unit_renderer.py`
- `viz3d_panda/scene_builder.py`
- `viz3d_panda/camera_controller.py`
- `.vscode/launch.json`

Current viewer read:

- Panda3D viewer is replay/view only
- viewer still consumes `visualization.display_language`
- viewer-facing fleet geometry now consumes the maintained `fleet_body_summary` replay contract
- `app.py` owns viewer orchestration / playback / HUD cadence
- `unit_renderer.py` owns bounded rendering carriers
- viewer-local cluster sway can now be toggled from `app.py` while sway realization remains inside `unit_renderer.py`
- current local viewer work also supports inspection of PR#9 contact / locomotion behavior through replay-path additions
- no old 2D viz / BRF surface remains in the active mainline

### 6. Documentation / Records Layer

- `README.md`
  - top-level repo overview and active mainline summary
- `AGENTS.md`
  - root AI execution contract
- `test_run/AGENTS.md`
  - `test_run` local execution contract
- `analysis/engineering_reports/developments/20260404/step3_3d_pr6_old_family_retirement_policy_note_20260409.md`
  - active old-family retirement policy
- `analysis/engineering_reports/developments/20260404/step3_3d_pr6_cleanup_methodology_and_lessons_20260409.md`
  - cleanup-stage methodology/lessons reference
- `docs/archive/ts_handoff_archive/`
  - TS handoff archive root

## Maintained Structural Read

Read the current maintained path as:

schema -> runtime -> maintained test harness -> replay/view consumer

Do **not** read the active tree as still owning:

- 2D viz launcher logic
- BRF report-builder logic
- maintained `v3a` execution
- selector-driven `v2/v3_test` runtime switching

## Active Debts Still Worth Watching

- large maintained files that may still benefit from bounded same-file layering review
- remaining legacy wording in comments/reference surfaces
- retreat-policy follow-up:
  - current runtime has no dedicated `back_off_keep_front` realization family
  - sustained disengagement vs short-range sternway is not yet explicitly split

## Interpretation Guardrails

- Historical names do not prove active ownership.
- Archived scripts and `retired/` references are history, not active semantics.
- Test-only settings are harness surfaces, not canonical ontology.
- Viewer consumes runtime output; it does not own simulation semantics.
