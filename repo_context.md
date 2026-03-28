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
- Step 3 objective line is now sufficiently established in bounded scope: opening review, first carrier, harness-side validation, and very small viewer-consumption hookup are all in place
- Step 3 next unopened mainline is now the structural-draft-only opening review for `3D Formation Contract v0.1`
- bounded `neutral_transit_v1` corrections now read as: first-turn `A1 + B1` remain active; the later early-side `E2` candidate regressed locally and was withdrawn during subtraction-first cleanup; the current post-cleanup bounded turn adds a late-only terminal non-overshoot clamp inside the existing stop-radius window without adding new parameters or settings
- Panda3D viewer now has a very small viewer-consumption hookup for the bounded neutral-transit first carrier while remaining a pure consumer of runtime-owned results
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
  - additive Panda3D viewer entrypoint for the `dev_v2.0` bootstrap container; owns launch/playback wiring, low-speed smoothing, and fixed-size screen-space avatar overlay only
- `viz3d_panda/replay_source.py`
  - consumes existing `test_run` active-surface output, inherits layered settings by default, and normalizes in-memory `position_frames` for viewer use
- `viz3d_panda/scene_builder.py`
  - viewer-local scene/grid/light bootstrap only
- `viz3d_panda/unit_renderer.py`
  - wedge-token unit rendering with viewer-local HP size buckets, minimal objective marker support, lighter two-ring fleet halos, and a distance-driven dual-layer close-range cluster view
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
- current viewer-local visual pass now uses only `enabled` / `disabled` fire-link modes; active fire links are a corrected-center pulse-train multi-beam cue rather than the old `minimal` / `full` straight-beam family
- current unit rendering can now cross-fade from far-range wedge readability into a near-range fixed 10-cuboid metallic-gray cluster without widening runtime or replay semantics
- current unit root origin now matches the rendered geometry center in `x / y / z`; no separate viewer-local "visual center" helper is active
- current inner cluster keeps cuboid size fixed and expresses HP loss by count reduction, not by shrinking the cuboids with the outer token
- current close-range cluster uses a trapezoid-friendly non-uniform `2/3/5` row layout with margin inside the outer token; the outer token has also been pulled back from an over-sharp dart profile toward a broader trapezoid-like read, and the inner cuboids are currently slightly larger, more spread toward the frame outline, and visibly staggered in `z`
- current viewer-local direction readout modes include `realistic`; its current local shape is a short-window travel-posture read, and low-speed playback now uses transform-only smoothing rather than building a synthetic smoothed frame
- current fire-link eye-load reduction uses endpoint smoothing at low speed, viewer-time-driven `sqrt(gear)` pulse motion, deterministic outer-beam alternation on a slower independent clock, and near/mid-only rendering with far-range suppression
- debug-only objective-area `realistic` investigation records now exist for `neutral_transit_v1` around `objective_reached_tick +/- 5`; current read is that effective flips far more than realistic in that window, candidate choice is almost entirely the widest centered source, and smoothing is not the primary cause
- debug-only late-terminal residual decomposition records now also exist for `neutral_transit_v1`; current read is that once centroid-level arrival is reached, moving expected-position restore becomes the strongest surviving driver, with separation/projection reshaping the residual unit motion
- the prior bounded late-terminal whole-frame freeze first cut is now superseded locally on the candidate-active `neutral_transit_v1` path by a narrower split cut: terminal reference orientation is latched, but expected-position center continues to follow the live centroid
- the current best local late-terminal candidate now layers two further bounded cuts on top of that split cut: terminal step magnitude is reduced inside the existing stop-radius window, and only backward axial restore is softened; current local read is that this is the best candidate so far, while a stricter no-net-backward follow-up was locally rejected after it created a new rotational side effect
- current engineering read is that this late-terminal result may also matter for the unresolved early restoration problem: the useful correction turned out to be component-wise and one-sided, which suggests early restore compatibility may also be more directional than scalar
- current guardrail rule is `viewer consumes, runtime owns`
- current neutral-transit first-carrier validation still lives in `test_run` launcher / fixture telemetry, and `viz3d_panda/` can now consume that same bounded fixture path through a very small viewer-side source hookup plus minimal consumer-side objective marker / fleet halo overlays
- current viewer-local fleet avatar overlay is fixed-size, screen-space, `4:5`, supports a local `P` show/hide toggle, uses per-fleet grouped layering, falls back to a midpoint-based side-by-side layout when two battle fleets project too close, re-solves during paused camera movement, and now uses a small gear-aware anti-jitter profile during playback
- current dual-layer unit view includes a minimal transparency-order correction to reduce inner-cluster occlusion by the transparent outer shell, near/mid/far cluster fading, and cleaner low-speed transform-only smoothing of motion-facing elements
- current tracked fleet camera now uses a small gear-aware playback stabilizer on focus motion only; pause/step inspection remains exact
- a future simplified warship proxy path is currently proposal-only; no ship-proxy implementation is active in the viewer
- a viewer-local governance query is now recorded for whether HP may reduce the close-range inner cluster cuboid count while keeping per-cuboid size fixed; query-only, not active
- current viewer-local input/camera refinements include hold-to-repeat `N/B` stepping, backquote/tilde direct reset, fleet `1/2` centroid tracking with manual angle retention after initialization, a right-drag-safe track lock path, a small gear-aware playback stabilizer on tracked focus motion, and broader zoom/pitch comfort limits
- current Step 3 formation work is draft-only and document-only; no formation runtime/mapping/legality implementation is active
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
- `analysis/engineering_reports/developments/20260326/dev_v2_0_visual_refinement_v1_note.md`
- `analysis/engineering_reports/developments/20260326/dev_v2_0_visual_refinement_v1_human_test_note.md`
- `analysis/engineering_reports/developments/20260326/dev_v2_0_container_boundary_note.md`
- `analysis/engineering_reports/developments/20260326/dev_v2_0_anti_fat_guardrail_note.md`
- `analysis/engineering_reports/developments/20260326/dev_v2_0_structure_hygiene_note.md`
- `analysis/specs/objective/objective_location_spec_v0_1_3d_draft.md`
- `analysis/engineering_reports/developments/20260326/step3_3d_neutral_transit_fixture_boundary_note.md`
- `analysis/engineering_reports/developments/20260326/step3_3d_objective_ownership_and_layering_note.md`
- `analysis/engineering_reports/developments/20260326/step3_3d_objective_impl_bounded_structural_draft.md`
- `analysis/engineering_reports/developments/20260326/step3_3d_objective_touchpoint_inventory.md`
- `analysis/engineering_reports/developments/20260326/step3_3d_objective_first_validation_note.md`
- `analysis/engineering_reports/developments/20260326/step3_3d_objective_first_impl_note.md`
- `analysis/engineering_reports/developments/20260326/step3_3d_objective_first_validation_report.md`
- `analysis/engineering_reports/developments/20260326/step3_3d_objective_fixture_readout_note.md`
- `analysis/engineering_reports/developments/20260326/step3_3d_objective_viewer_consumption_hookup_note.md`
- `analysis/engineering_reports/developments/20260326/neutral_transit_tick1_effective_direction_read_note_20260326.md`
- `analysis/engineering_reports/developments/20260326/neutral_transit_bounded_corrections_note_20260326.md`
- `analysis/engineering_reports/developments/20260326/neutral_transit_bounded_corrections_validation_note_20260326.md`
- `analysis/engineering_reports/developments/20260326/neutral_transit_bounded_corrections_metric_delta_note_20260326.md`
- `analysis/engineering_reports/developments/20260326/neutral_transit_bounded_corrections_governance_feedback_20260326.md`
- `analysis/engineering_reports/developments/20260326/neutral_transit_second_bounded_corrections_note_20260326.md`
- `analysis/engineering_reports/developments/20260326/neutral_transit_second_bounded_corrections_validation_note_20260326.md`
- `analysis/engineering_reports/developments/20260326/neutral_transit_second_bounded_corrections_metric_delta_note_20260326.md`
- `analysis/engineering_reports/developments/20260326/neutral_transit_second_bounded_corrections_governance_feedback_20260326.md`
- `analysis/engineering_reports/developments/20260326/dev_v2_0_viewer_input_camera_refinement_note.md`
- `analysis/engineering_reports/developments/20260326/dev_v2_0_realistic_direction_mode_note.md`
- `analysis/engineering_reports/developments/20260326/dev_v2_0_realistic_direction_mode_human_test_note.md`
- `analysis/engineering_reports/developments/20260326/neutral_transit_post_cleanup_late_arrival_and_overlays_note_20260326.md`
- `analysis/engineering_reports/developments/20260326/neutral_transit_post_cleanup_late_arrival_and_overlays_validation_note_20260326.md`
- `analysis/engineering_reports/developments/20260327/dev_v2_0_preformation_visual_pass2_note_20260327.md`
- `analysis/engineering_reports/developments/20260327/dev_v2_0_preformation_visual_pass2_governance_addendum_20260327.md`
- `analysis/engineering_reports/developments/20260327/dev_v2_0_visual_improvement_reflection_20260327.md`
- `analysis/engineering_reports/developments/20260326/dev_v2_0_dual_layer_unit_representation_note.md`
- `analysis/engineering_reports/developments/20260326/dev_v2_0_dual_layer_unit_representation_human_test_note.md`
- `analysis/engineering_reports/developments/20260326/dev_v2_0_simplified_warship_proxy_proposal.md`
- `analysis/engineering_reports/developments/20260327/objective_area_realistic_debug_note_20260327.md`
- `analysis/engineering_reports/developments/20260327/objective_area_realistic_debug_window_dump_20260327.csv`
- `analysis/engineering_reports/developments/20260327/objective_area_realistic_candidate_trace_20260327.csv`
- `analysis/engineering_reports/developments/20260327/objective_area_realistic_smoothing_split_note_20260327.md`
- `analysis/engineering_reports/developments/20260327/objective_area_realistic_governance_feedback_20260327.md`
- `analysis/engineering_reports/developments/20260327/late_terminal_residual_decomposition_note_20260327.md`
- `analysis/engineering_reports/developments/20260327/late_terminal_residual_decomposition_window_dump_20260327.csv`
- `analysis/engineering_reports/developments/20260327/late_terminal_residual_component_summary_20260327.csv`
- `analysis/engineering_reports/developments/20260327/late_terminal_residual_governance_feedback_20260327.md`
- `analysis/engineering_reports/developments/20260327/late_terminal_frozen_expected_position_first_cut_note_20260327.md`
- `analysis/engineering_reports/developments/20260327/late_terminal_frozen_expected_position_first_cut_validation_note_20260327.md`
- `analysis/engineering_reports/developments/20260327/late_terminal_frozen_expected_position_window_dump_20260327.csv`
- `analysis/engineering_reports/developments/20260327/late_terminal_frozen_expected_position_component_summary_20260327.csv`
- `analysis/engineering_reports/developments/20260327/late_terminal_frozen_expected_position_engineering_read_20260327.md`
- `analysis/engineering_reports/developments/20260327/late_terminal_orientation_freeze_live_centroid_note_20260327.md`
- `analysis/engineering_reports/developments/20260327/late_terminal_orientation_freeze_live_centroid_validation_note_20260327.md`
- `analysis/engineering_reports/developments/20260327/late_terminal_orientation_freeze_live_centroid_window_dump_20260327.csv`
- `analysis/engineering_reports/developments/20260327/late_terminal_orientation_freeze_live_centroid_component_summary_20260327.csv`
- `analysis/engineering_reports/developments/20260327/late_terminal_orientation_freeze_live_centroid_engineering_read_20260327.md`
- `analysis/engineering_reports/developments/20260327/late_terminal_step_magnitude_one_sided_restore_note_20260327.md`
- `analysis/engineering_reports/developments/20260327/late_terminal_step_magnitude_one_sided_restore_validation_note_20260327.md`
- `analysis/engineering_reports/developments/20260327/late_terminal_step_magnitude_one_sided_restore_window_dump_20260327.csv`
- `analysis/engineering_reports/developments/20260327/late_terminal_step_magnitude_one_sided_restore_component_summary_20260327.csv`
- `analysis/engineering_reports/developments/20260327/late_terminal_step_magnitude_one_sided_restore_engineering_read_20260327.md`
- `analysis/engineering_reports/developments/20260327/late_terminal_step_magnitude_one_sided_restore_governance_feedback_20260327.md`
- `analysis/engineering_reports/developments/20260327/dev_v2_0_hp_bucketed_inner_cluster_query_20260327.md`
- `analysis/specs/formation/formation_specs_v0_1_3d_draft.md`
- `analysis/engineering_reports/developments/20260326/step3_3d_formation_frame_minimalization_note.md`
- `analysis/engineering_reports/developments/20260326/step3_3d_formation_mapping_legality_split_note.md`
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
