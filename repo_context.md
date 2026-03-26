# LOGH Sandbox Repository Context

Status: Working Context File  
Purpose: High-level repository index for governance-side reading and fast navigation  
Authority: Reference only, not canonical semantics authority

## Repository Identity

- Repository: `LiDonghuang/logh_sandbox`
- Primary development branch: `dev_v2.0`

## Current Phase Focus

- 2D mainline functionally closed out with note
- first bounded 3D viewer bootstrap active on `dev_v2.0`
- Step 1 viewer readability / launch semantics alignment completed in the additive 3D viewer layer
- Step 2 container boundary / anti-fat guardrail documentation now defines `viz3d_panda/` as a replay/view bootstrap container only
- Step 3 opening review is active at structural-draft-only level for a minimum 3D objective contract and bounded neutral-transit first carrier
- A1 hostile penetration line freeze completed as working/stopped/failed status separation
- A3 settings layering completed
- A5 `test_run` structural reset functionally completed; residual maintained-path weight now sits in post-closeout engineering debt
- APP-side governance mirror intentionally reduced to an 11-file active working set

Current emphasis is bounded 3D viewer bootstrap rather than personality expansion or 3D runtime semantics.

## Key Entry Documents

- `README.md`
  - top-level project identity, repo layout, baseline/runtime status, and practical entry guidance
- `AGENTS.md`
  - execution contract for scoped AI assistance, frozen layers, TS migration, no-silent-fallback, and commit discipline

## Key Governance / Architecture Documents

- `docs/README.md`
  - repo-side documentation layer entry: canonical / context / reference / archive separation
- `docs/APP_Files_Prefix_Mapping_v1.0.md`
  - APP mirror scope and active flat-file set policy
- `docs/governance/Baseline_Replacement_Protocol_v1.0.md`
  - governs experiment vs baseline-replacement boundary and replacement recording discipline
- `docs/governance/Phase_Transition_Governance_Playbook_v1_0.md`
  - phase activation / expansion governance framework and gate structure
- `docs/architecture/Canonical_Authority_Alignment_v1.2.md`
  - engineering reference priority and canonical authority alignment guidance
- `docs/architecture/LOGH_Analytical_Stack_Architecture_v1.0.md`
  - observer/report analytical stack layers and L0-L3 boundary map
- `docs/governance/Global_Road_Map_Engagement_to_Personality_20260318.md`
  - top-level phase ordering and current Phase A positioning

## Runtime Core Paths

- `runtime/runtime_v0_1.py`
  - runtime schema and immutable state types
- `runtime/engine_skeleton.py`
  - tick pipeline and core runtime behavior; maintained cohesion path now runs a single selected source inside runtime
  - current hot-path cleanup includes local spatial-hash use for combat candidate generation, movement pair pruning with preserved pair order, and cohesion connectivity search

## Test Harness Paths

- `test_run/test_run_entry.py`
  - maintained 2D launcher ground truth for routine run, daily animation, video export, and BRF handoff
- `test_run/test_run_scenario.py`
  - scenario build, archetype resolution, and maintained harness helper surface
- `test_run/test_run_execution.py`
  - maintained battle execution host and engine-adjacent test harness skeleton host
- `test_run/test_run_telemetry.py`
  - observer / bridge / collapse-shadow collection
- `test_run/test_run_anchor_regression.py`
  - fixed routine 3-run anchor regression on the maintained spine
- `test_run/settings_accessor.py`
  - layered settings loading/access

## Report / Viz Paths

- `test_run/battle_report_builder.py`
  - active auxiliary BRF markdown assembly used by the maintained launcher path
- `test_run/brf_narrative_messages.py`
  - active auxiliary BRF narrative message library
- `test_run/test_run_v1_0_viz.py`
  - active auxiliary renderer, plots, and animation/export display layer

## 3D Viewer Bootstrap Paths

- `viz3d_panda/app.py`
  - additive Panda3D viewer entrypoint for the `dev_v2.0` bootstrap container; owns launch/playback wiring only
- `viz3d_panda/replay_source.py`
  - consumes existing `test_run` active-surface output, inherits layered settings by default, and normalizes in-memory `position_frames` for viewer use
- `viz3d_panda/scene_builder.py`
  - viewer-local scene/grid/light bootstrap only
- `viz3d_panda/unit_renderer.py`
  - wedge-token unit rendering with viewer-local HP size buckets and frame-to-frame updates only
- `viz3d_panda/camera_controller.py`
  - bounded camera orbit/pan/zoom controls only
- `launch_dev_v2_0_viewer.bat`
  - thin human-facing launcher for the Panda3D viewer bootstrap

Current availability status:

- Panda3D is active as the first candidate viewer bootstrap container on `dev_v2.0`
- current 3D surface is replay/viewer only
- it consumes existing 2D `position_frames` in memory
- default launch now inherits the maintained 2D stop contract unless `--steps` is explicitly passed
- current readability pass uses a single semi-transparent wedge token rather than the earlier thin line-arrow marker
- current guardrail rule is `viewer consumes, runtime owns`
- no parallel simulation settings surface is owned by `viz3d_panda/`
- no 3D runtime combat/movement baseline is established by this surface

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

## Key Current Records

- `analysis/engineering_reports/developments/20260325/2d_phase_closeout_and_3d_transition_memo_20260326.md`
- `analysis/engineering_reports/developments/20260325/3d_transition_packet_20260326.md`
- `analysis/engineering_reports/developments/20260326/dev_v2_0_panda3d_bootstrap_note.md`
- `analysis/engineering_reports/developments/20260326/dev_v2_0_first_demo_note.md`
- `analysis/engineering_reports/developments/20260326/dev_v2_0_viewer_readability_pass1_note.md`
- `analysis/engineering_reports/developments/20260326/dev_v2_0_launch_semantics_alignment_note.md`
- `analysis/engineering_reports/developments/20260326/dev_v2_0_settings_mapping_directory.md`
- `analysis/engineering_reports/developments/20260326/dev_v2_0_human_test_launch_note.md`
- `analysis/engineering_reports/developments/20260326/dev_v2_0_container_boundary_note.md`
- `analysis/engineering_reports/developments/20260326/dev_v2_0_anti_fat_guardrail_note.md`
- `analysis/engineering_reports/developments/20260326/dev_v2_0_structure_hygiene_note.md`
- `analysis/specs/objective/objective_location_spec_v0_1_3d_draft.md`
- `analysis/engineering_reports/developments/20260326/step3_3d_neutral_transit_fixture_boundary_note.md`
- `analysis/engineering_reports/developments/20260326/step3_3d_objective_ownership_and_layering_note.md`
- `analysis/engineering_reports/developments/20260326/test_run_vector_display_mode_source_of_truth_cleanup_20260326.md`
- `docs/governance/Global_Road_Map_Engagement_to_Personality_20260318.md`
- `analysis/engineering_reports/developments/20260318/structural_cleanup/a5_iteration0_baseline_anchor_20260318.md`
- `analysis/engineering_reports/developments/20260318/structural_cleanup/a5_iteration0_baseline_anchor_20260318.json`
- `analysis/engineering_reports/developments/20260318/structural_cleanup/test_run_harness_cleanup_record_20260319.md`
- `analysis/engineering_reports/developments/20260318/structural_cleanup/phase_a_governance_update_20260319.md`
- `analysis/engineering_reports/developments/20260318/structural_cleanup/test_run_anchor_regression_policy_20260319.md`
- `analysis/engineering_reports/developments/20260318/structural_cleanup/test_run_structural_reset_preparation_20260320.md`
- `analysis/engineering_reports/developments/20260318/structural_cleanup/test_run_active_surface_reset_round1_20260320.md`
- `analysis/engineering_reports/developments/20260318/structural_cleanup/test_run_governance_followup_20260320.md`
- `analysis/engineering_reports/developments/20260318/structural_cleanup/test_run_governance_request_brf_and_runtime_followup_20260320.md`
- `analysis/engineering_reports/developments/20260318/structural_cleanup/brf_internal_subtraction_followup_20260320.md`
- `analysis/engineering_reports/developments/20260318/structural_cleanup/test_run_v1_0_exit_report_20260320.md`
- `analysis/engineering_reports/developments/20260318/structural_cleanup/test_run_split_validation_20260320.md`
- `analysis/engineering_reports/developments/20260318/structural_cleanup/runtime_engine_skeleton_burden_inventory_20260320.md`
- `analysis/engineering_reports/developments/20260318/structural_cleanup/documentation_hygiene_update_20260321.md`
- `analysis/engineering_reports/developments/20260318/structural_cleanup/engine_skeleton_cohesion_selection_and_outlier_retirement_20260321.md`
- `analysis/engineering_reports/developments/20260318/structural_cleanup/engine_skeleton_diag4_outlier_family_retirement_20260321.md`
- `analysis/engineering_reports/developments/20260318/structural_cleanup/phase_a_closeout_matrix_20260321.md`
- `analysis/engineering_reports/developments/20260318/structural_cleanup/phase_a_accept_closeout_with_note_20260321.md`

## Reading Order

1. `runtime/runtime_v0_1.py`
2. `runtime/engine_skeleton.py`
3. `test_run/test_run_entry.py`
4. `test_run/test_run_scenario.py`
5. `test_run/test_run_execution.py`
6. `test_run/test_run_telemetry.py`
7. `viz3d_panda/replay_source.py`
8. `viz3d_panda/app.py`
9. `test_run/battle_report_builder.py`
10. `test_run/test_run_v1_0_viz.py`
