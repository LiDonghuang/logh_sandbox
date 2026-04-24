# LOGH Sandbox Repository Context

Status: Working Context File  
Purpose: High-level repository index for fast engineering/governance orientation
Authority: Reference only, not canonical semantics authority

## Repository Identity

- Repository: `LiDonghuang/logh_sandbox`
- Current PR#9 working branch: `eng/dev-v2.1-formation-only`
- Maintained movement baseline: `v4a`

## Current Phase Focus

- Current PR#9 Phase II branch state is a phase-boundary consolidation for:
  - Unit-layer target/intent/desire owner-path clarification
  - test-only Unit-local maneuver / behavior-line `back_off_keep_front` experimentation
  - structural cleanup / subtraction ledger / reader-facing debug-surface alignment
  - first bounded `signed_longitudinal_backpedal` locomotion capability implementation
- Current accepted structural posture:
  - structural cleanup line is paused
  - Behavior line remains experimental and test-only
  - locomotion capability line has a first bounded implementation slice for `signed_longitudinal_backpedal`
  - the new capability is experimental, explicit-gated, and default-off
- Current comparison anchors include:
  - Phase II primary baseline captures under `analysis/reference_notes/`
  - temporary working-anchor and post-subtraction dual-posture anchors for paired comparison

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
- `docs/governance/PR9_Phase2_Unit_Solving_Layer_Governance_Direction_20260419.md`
  - repo-side PR9 Phase II governance direction export for the Unit-solving layer carrier
- `analysis/engineering_reports/developments/20260423/pr9_phase2_signed_longitudinal_backpedal_bounded_implementation_proposal_20260423.md`
  - document-first bounded proposal for the first signed longitudinal backpedal capability gate
- `analysis/engineering_reports/developments/20260423/pr9_phase2_signed_longitudinal_backpedal_bounded_implementation_report_20260423.md`
  - implementation and validation report for the first bounded signed longitudinal backpedal slice
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
  - maintained `integrate_movement()` hot path is again runtime-owned
  - maintained runtime movement now accepts only `v4a`
  - active `v4a` restore is direct:
    - `restore_term = restore_strength * normalize(restore_vector)`
  - current PR#9 slices now include:
    - same-tick target selection before combat execution
    - Unit intent and Unit desire tick-local carriers
    - test-only local maneuver / behavior-line `back_off_keep_front` response
    - combat damage scalar cleanup to the current no-coupling working anchor
    - low-level locomotion realization limits for heading change and speed change
    - default-off experimental `signed_longitudinal_backpedal` realization through `desired_longitudinal_travel_scale`
    - runtime-owned fleet heading memory in `coarse_body_heading_current`
  - active `v4a` no longer consumes:
    - legacy `v3a` movement branch body
    - `cohesion_decision_source`
    - `collapse_signal.v3_*`
    - FSR in the active `v4a` path
  - current combat execution consumes the same-tick target carrier and no longer owns target choice
  - current locomotion still couples facing and translation:
    - no literal keep-front backward-motion capability exists yet

## Maintained Harness Paths

- `test_run/test_run_entry.py`
  - maintained headless `test_run` entrypoint
- `test_run/test_run_scenario.py`
  - settings resolution, effective-surface preparation, and scenario build
- `test_run/test_run_execution.py`
  - maintained battle / neutral harness execution host
  - maintained execution/orchestration owner
  - shared `v4a` movement-family host for both `battle` and `neutral`
  - runtime owns the maintained tick hot path; harness supplies preparation, bundle carriers, and observation packaging
  - current harness also hosts:
    - baseline capture / replay-friendly per-tick recording used for paired comparison
    - layered settings plumbing for fire-control and low-level locomotion parameters
    - test-only local maneuver / back-off enablement and tuning surfaces
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
- viewer-facing fleet geometry now reads the maintained `fleet_body_summary` export produced by `test_run`
- `app.py` owns viewer orchestration / playback / camera / HUD cadence
- `unit_renderer.py` owns bounded rendering carriers
- viewer now includes an app-facing toggle for cluster sway, while sway realization remains renderer-local
- current local viewer work also includes:
  - heading-based direction mode as the default visual facing read
  - replay-path support for target lines / local maneuver debug review
  - playback TPS and camera-take surface updates
  - random skybox selection / camera-take skybox persistence
- old 2D viz / BRF launcher surfaces are no longer part of the active mainline

## Settings Paths

- `test_run/test_run_v1_0.settings.json`
  - thin entry settings / layer pointer
- `test_run/test_run_v1_0.runtime.settings.json`
  - maintained runtime values
  - `run_control.symmetric_movement_sync_enabled` is now the honest owner of symmetric merge control
  - `runtime.metatype.*` remains a scenario-level high-level interface for Yang/personality sampling only
  - `runtime.observer` is now narrowed to still-active maintained keys
  - current runtime public additions include:
    - `runtime.physical.fire_control.fire_cone_half_angle_deg`
    - `runtime.physical.movement_low_level.*`
  - current fire-control surface uses `fire_angle_quality_alpha` to distinguish angle quality from range quality
- `test_run/test_run_v1_0.testonly.settings.json`
  - maintained test-only harness controls
  - `fixture.neutral.stop_radius` is the neutral-only objective termination radius
  - `runtime.physical.local_desire.experimental_signal_read_realignment_enabled` is the explicit test-only switch for the current local maneuver / back-off family
  - current `v4a` candidate parameters are structured under:
    - `restore`
    - `reference`
    - `transition`
    - `battle`
    - `engagement`
- `test_run/test_run_v1_0.settings.comments.json`
  - current comments aligned to active settings truth
- `test_run/test_run_v1_0.settings.reference.md`
  - current settings structure notes

## Current Truth Surface

- `battle` and `neutral` share the maintained `v4a` movement mechanism family
- the only intended semantic difference between them is objective source
- the maintained public movement selector is now `v4a` only
- the maintained test-only hostile-contact selector is now `off | hybrid_v2`
- active runtime state no longer carries `PersonalityParameters`
- scenario-prepared high-level payloads still expose sampled `PersonalityParameters` and `effective_metatype_random_seed`
- `stop_radius` is neutral-only termination semantics, not battle hold semantics
- `fleet_body_summary` is the maintained viewer-facing fleet-body geometry contract
- `fire_cone_half_angle_deg` is the maintained combat target-selection cone control
- same-tick target identity is owned before combat execution; `resolve_combat()` re-checks and resolves fire/damage
- `engaged_target_id` remains post-resolution engagement writeback, not target-selection owner
- `local_desire` / Unit-local maneuver behavior is test-only and explicitly switch-gated
- low-level locomotion realization is now an explicit runtime surface below Formation:
  - accel limit
  - decel limit
  - turn-rate limit
  - turn-speed floor
- fleet heading memory is now runtime-owned in `coarse_body_heading_current`
- `signed_longitudinal_backpedal` is implemented as a first bounded experimental slice:
  - default-off gate: `runtime.physical.locomotion.experimental_signed_longitudinal_backpedal_enabled`
  - explicit Unit desire carrier: `desired_longitudinal_travel_scale`
  - reverse authority limiter: `runtime.physical.locomotion.signed_longitudinal_backpedal_reverse_authority_scale`
- current `attack_speed_backward_scale` is a speed allowance surface, not literal backward-motion capability
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
