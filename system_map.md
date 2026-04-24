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
- the current working branch is a PR#9 Phase II consolidation carrier for:
  - Formation coarse-body/reference ownership
  - Unit-layer target/intent/desire seams
  - bounded low-level locomotion realization
  - test-only Unit-local maneuver / behavior-line `back_off_keep_front` experimentation
  - first bounded `signed_longitudinal_backpedal` locomotion capability implementation
  - bounded `signed_longitudinal_facing_axis_guard` correction
  - paired comparison against Phase II baseline anchors
- current branch-local runtime slices include:
  - same-tick target selection before combat execution
  - `resolve_combat(...)` consuming the selected-target carrier for re-check / fire / damage
  - Unit intent and Unit desire tick-local carriers
  - test-only local maneuver / bounded give-ground response behind explicit enablement
  - low-level locomotion realization limits in `integrate_movement()`
  - default-off signed longitudinal backpedal realization through the Unit desire seam
  - default-off facing-axis guard that keeps signed-longitudinal gate-on facing tied to `desired_heading_xy`
  - runtime-owned fleet heading memory in `coarse_body_heading_current`
- active `v4a` no longer depends on:
  - maintained `v3a` movement branch body
  - `cohesion_decision_source`
  - `collapse_signal.v3_*`
  - FSR in the active `v4a` path
- `engaged_target_id` remains post-resolution engagement writeback, not the target-selection owner
- current locomotion capability line blocks gate-on fake backpedal through turned-away forward motion
- literal keep-front backward motion exists only through the explicit signed longitudinal carrier and remains experimental
- the structural-cleanup line is paused after the post-cleanup structural anchor / subtraction ledger wave

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
- harness also carries test-only local maneuver / back-off enablement and tuning surfaces
- baseline/replay captures preserve per-tick frames, target lines, fleet body summaries, runtime debug, telemetry, and configs for paired comparison

### 4. Settings Layer

- `test_run/test_run_v1_0.settings.json`
- `test_run/test_run_v1_0.runtime.settings.json`
- `test_run/test_run_v1_0.testonly.settings.json`
- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`

Current maintained settings read:

- runtime selector is `v4a` only
- test-only hostile-contact selector is `off | hybrid_v2`
- test-only local maneuver / behavior-line `back_off_keep_front` family is explicitly switch-gated
- `runtime.metatype.*` remains a scenario-level Yang/personality sampling interface only
- `run_control.symmetric_movement_sync_enabled` owns symmetric merge control
- `runtime.observer` has been narrowed to still-active maintained keys
- runtime now also exposes:
  - fire-control cone width
  - fire angle quality alpha
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
- current local viewer work also supports inspection of PR#9 contact / locomotion behavior through replay-path additions:
  - default `heading` direction mode reads runtime facing
  - `movement` mode remains available for travel read
  - current focus HUD reads `raw_gap`, `embg`, `reopen`, and `brk`
  - playback uses fixed TPS levels rather than FPS labels
  - camera takes include direction-stabilization and skybox path context
- no old 2D viz / BRF surface remains in the active mainline

### 6. Documentation / Records Layer

- `README.md`
  - top-level repo overview and active mainline summary
- `AGENTS.md`
  - root AI execution contract
- `test_run/AGENTS.md`
  - `test_run` local execution contract
- `viz3d_panda/AGENTS.md`
  - viewer-local execution contract
- `docs/governance/PR9_Phase2_Unit_Solving_Layer_Governance_Direction_20260419.md`
  - PR9 Phase II governance direction export for the Unit-solving layer carrier
- `analysis/engineering_reports/developments/20260423/pr9_phase2_signed_longitudinal_backpedal_bounded_implementation_proposal_20260423.md`
  - first bounded proposal for the signed longitudinal backpedal locomotion capability gate
- `analysis/engineering_reports/developments/20260423/pr9_phase2_signed_longitudinal_backpedal_bounded_implementation_report_20260423.md`
  - implementation and validation report for the first bounded signed longitudinal backpedal slice
- `analysis/engineering_reports/developments/20260423/pr9_phase2_signed_longitudinal_backpedal_facing_coupling_followup_proposal_20260423.md`
  - follow-up proposal for correcting facing-axis coupling after the first signed backpedal slice
- `analysis/engineering_reports/developments/20260423/pr9_phase2_signed_longitudinal_facing_axis_guard_bounded_implementation_report_20260423.md`
  - implementation and validation report for the bounded facing-axis guard correction
- `analysis/engineering_reports/developments/20260404/step3_3d_pr6_old_family_retirement_policy_note_20260409.md`
  - active old-family retirement policy
- `analysis/engineering_reports/developments/20260404/step3_3d_pr6_cleanup_methodology_and_lessons_20260409.md`
  - cleanup-stage methodology/lessons reference
- `docs/archive/ts_handoff_archive/`
  - TS handoff archive root
- `analysis/engineering_reports/developments/20260419/` through `20260423/`
  - current PR9 Phase II engineering reports, proposals, implementation records, and pause notes
- `analysis/reference_notes/`
  - Phase II baseline and temporary-anchor capture records

## Maintained Structural Read

Read the current maintained path as:

schema -> runtime -> maintained test harness -> replay/view consumer

Do **not** read the active tree as still owning:

- 2D viz launcher logic
- BRF report-builder logic
- maintained `v3a` execution
- selector-driven `v2/v3_test` runtime switching

## Active Debts Still Worth Watching

- large maintained files still need careful boundary discipline; do not chase LOC reduction as a standalone goal
- current Unit-local maneuver / behavior-line family remains test-only / experimental
- current locomotion capability line has a first bounded default-off implementation:
  - `desired_longitudinal_travel_scale` is the explicit signed Unit desire carrier
  - signed longitudinal velocity is realized only when the experimental gate is enabled
  - gate-on facing-axis guard prevents turn-away forward motion from substituting for the signed carrier
  - this is not retreat, lateral strafe, or broad facing/translation decoupling
- retreat implementation remains separate and closed

## Interpretation Guardrails

- Historical names do not prove active ownership.
- Archived scripts and `retired/` references are history, not active semantics.
- Test-only settings are harness surfaces, not canonical ontology.
- Viewer consumes runtime output; it does not own simulation semantics.
