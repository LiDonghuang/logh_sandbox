# LOGH Sandbox Repository Context

Status: Working Context File  
Purpose: High-level repository index for governance-side reading and fast navigation  
Authority: Reference only, not canonical semantics authority

## Repository Identity

- Repository: `LiDonghuang/logh_sandbox`
- Primary development branch: `dev_v2.1`

## Current Phase Focus

- 2D mainline functionally closed out with note
- first bounded 3D viewer bootstrap active on `dev_v2.0`
- Step 1 viewer readability / launch semantics alignment completed in the additive 3D viewer layer
- Step 2 container boundary / anti-fat guardrail documentation now defines `viz3d_panda/` as a replay/view bootstrap container only
- Step 3 objective line is now sufficiently established in bounded scope: opening review, first carrier, harness-side validation, and very small viewer-consumption hookup are all in place
- Step 3 formation reference line is now structurally opened and closed in bounded document-only scope across frame / layout / spacing carriers
- Step 3 mapping line remains at scope-confirmation plus minimum-contract records only; the legality line now spans merged opening-scope, minimum-contract, contract-stabilization, touchpoint/interface/consumer-boundary, runtime-integration-envelope, implementation-prep decision/plan records, a merged first bounded runtime/harness implementation baseline, and an active bounded hardening charter
- current recovered anchor is `dev_v2.1`; the active cleanup carrier is `eng/dev-v2.1-targeting-restore-cleanup`
- current neutral fixture active mode is `neutral`; runtime expected-position intake no longer depends on the old `neutral_transit_v1` mode gate
- Panda3D viewer now has a very small viewer-consumption hookup for the bounded neutral-transit first carrier while remaining a pure consumer of runtime-owned results
- A1 hostile penetration line freeze completed as working/stopped/failed status separation
- A3 settings layering completed
- A5 `test_run` structural reset functionally completed; residual maintained-path weight now sits in post-closeout engineering debt
- GitHub branch + PR collaboration workflow now has an active repo-side engineering workflow document for larger carrier review
- Cross-thread collaboration protocol v1.4 is now the active repo-side / APP-sync protocol baseline
- APP-side governance workflow now uses a 10-file repo-backed mirror set plus a local `REPO_INDEX_POINTER` orientation workflow; `repo_context.md` and `system_map.md` are no longer maintained as full APP local mirror files

Current emphasis is bounded 3D viewer bootstrap rather than personality expansion or 3D runtime semantics.

## Key Entry Documents

- `README.md`
  - top-level project identity, repo layout, baseline/runtime status, and practical entry guidance
- `AGENTS.md`
  - execution contract for scoped AI assistance, frozen layers, TS migration, no-silent-fallback, and commit discipline

## Key Governance / Architecture Documents

- `canonical/Sandbox_CrossThread_Protocol_v1.4.md`
  - active cross-thread operating protocol for governance / engineering collaboration, action modes, evidence discipline, and baseline-hardening escalation rules
- `docs/README.md`
  - repo-side documentation layer entry: canonical / context / reference / archive separation
- `docs/APP_Files_Prefix_Mapping_v1.0.md`
  - APP mirror scope, repo-backed active flat-file set policy, and local pointer-based orientation rule
- `docs/governance/Baseline_Replacement_Protocol_v1.0.md`
  - governs experiment vs baseline-replacement boundary and replacement recording discipline
- `docs/governance/Phase_Transition_Governance_Playbook_v1_0.md`
  - phase activation / expansion governance framework and gate structure
- `docs/architecture/Canonical_Authority_Alignment_v1.2.md`
  - engineering reference priority and canonical authority alignment guidance
- `docs/architecture/LOGH_Analytical_Stack_Architecture_v1.0.md`
  - observer/report analytical stack layers and L0-L3 boundary map
- `docs/engineering/GitHub_Branch_PR_Collaboration_Workflow_v1.0.md`
  - active engineering workflow for when to direct-push vs use branch + PR carriers
- `docs/engineering/Legality_First_Bounded_Baseline_Hardening_Working_Charter_v1.0.md`
  - active bounded working charter for legality baseline hardening iterations, evidence requirements, and return-to-governance triggers
- `docs/governance/Global_Road_Map_Engagement_to_Personality_20260318.md`
  - top-level phase ordering and current Phase A positioning

## Runtime Core Paths

- `runtime/runtime_v0_1.py`
  - runtime schema and immutable state types
- `runtime/engine_skeleton.py`
  - tick pipeline and core runtime behavior; maintained cohesion path now runs a single selected source inside runtime
  - current hot-path cleanup includes local spatial-hash use for combat candidate generation, movement pair pruning with preserved pair order, and cohesion connectivity search
  - current merged baseline now exposes one first bounded legality seam after mapping-produced reference positions are available and before downstream feasible-position consumption
  - current `dev_v2.1` line also carries a first bounded expected-damage targeting candidate in `resolve_combat()`: target selection now considers bounded angle/range-derived expected damage, `attack_range` remains max range, and `fire_optimal_range_ratio` now also defines the active battle hold-gap base through `fire_optimal_range`
  - active `v4a` restore is now a direct runtime seam: `restore_term = restore_strength * normalize(restore_vector)`
  - active `v4a` no longer consumes FSR

## Test Harness Paths

- `test_run/test_run_entry.py`
  - maintained 2D launcher ground truth for routine run, daily animation, video export, and BRF handoff
- `test_run/test_run_scenario.py`
  - scenario build, archetype resolution, and maintained harness helper surface
- `test_run/test_run_execution.py`
  - maintained battle execution host and engine-adjacent test harness skeleton host
  - current merged baseline reuses existing fixture metrics to trace legality intake / middle-stage / handoff counts and flags
- `test_run/test_run_telemetry.py`
  - observer / bridge / collapse-shadow collection
  - current merged baseline exposes a minimal legality echo in the existing runtime debug payload extraction path
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
- current viewer-local 3D direction readout modes now center on `movement` and `posture`; `movement` is the old short-window smoothed travel-direction read, `posture` is a bounded viewer-only maneuver-posture synthesis, and low-speed playback still uses transform-only smoothing rather than building a synthetic smoothed frame
- current fire-link eye-load reduction uses endpoint smoothing at low speed, viewer-time-driven `sqrt(gear)` pulse motion, deterministic outer-beam alternation on a slower independent clock, and near/mid-only rendering with far-range suppression
- debug-only objective-area direction-read investigation records now exist for `neutral_transit_v1` around `objective_reached_tick +/- 5`; historical read was that effective flips far more than the old travel-smoothed mode in that window, candidate choice was almost entirely the widest centered source, and smoothing was not the primary cause
- debug-only late-terminal residual decomposition records now also exist for `neutral_transit_v1`; current read is that once centroid-level arrival is reached, moving expected-position restore becomes the strongest surviving driver, with separation/projection reshaping the residual unit motion
- the prior bounded late-terminal whole-frame freeze first cut is now superseded locally on the candidate-active `neutral_transit_v1` path by a narrower split cut: terminal reference orientation is latched, but expected-position center continues to follow the live centroid
- the current best local late-terminal candidate now layers two further bounded cuts on top of that split cut: terminal step magnitude is reduced inside the existing stop-radius window, and only backward axial restore is softened; current local read is that this is the best candidate so far, while a stricter no-net-backward follow-up was locally rejected after it created a new rotational side effect
- current engineering read is that this late-terminal result may also matter for the unresolved early restoration problem: the useful correction turned out to be component-wise and one-sided, which suggests early restore compatibility may also be more directional than scalar
- current guardrail rule is `viewer consumes, runtime owns`
- current neutral-transit first-carrier validation still lives in `test_run` launcher / fixture telemetry, and `viz3d_panda/` can now consume that same bounded fixture path through a very small viewer-side source hookup plus minimal consumer-side objective marker / fleet halo overlays
- current viewer-local fleet avatar overlay is fixed-size, screen-space, `4:5`, supports a local `P` show/hide toggle, uses per-fleet grouped layering, falls back to a midpoint-based side-by-side layout when two battle fleets project too close, re-solves during paused camera movement, stays on the main interpolation path through gear `5`, and now uses a lighter ring-style highlight without extra avatar-local playback smoothing
- current 3D avatar presentation is now split by role: battle-follow portraits use small `_s` assets, while fixed corner avatar blocks use `_m` assets with language-aware full names, HP-total `Fleet Size` readout, and initial-total-HP bars; the corner avatar blocks stay visible independently of the `P` toggle
- current Panda3D viewer/export support now includes viewer-local camera-take recording plus a dedicated offscreen video-export entry at `viz3d_panda/export_video.py`, with default export artifacts under `analysis/exports/videos/`
- current dual-layer unit view includes a minimal transparency-order correction to reduce inner-cluster occlusion by the transparent outer shell, near/mid/far cluster fading, and cleaner low-speed transform-only smoothing of motion-facing elements
- current tracked fleet camera now uses a small gear-aware playback stabilizer on focus motion only; pause/step inspection remains exact
- a stage governance memo now records the accepted pre-Formation viewer-only state under `analysis/engineering_reports/developments/20260327/`; it is a local-state governance record, not canonical governance authority
- a future simplified warship proxy path is currently proposal-only; no ship-proxy implementation is active in the viewer
- a viewer-local governance query is now recorded for whether HP may reduce the close-range inner cluster cuboid count while keeping per-cuboid size fixed; query-only, not active
- current viewer-local input/camera refinements include hold-to-repeat `N/B` stepping, backquote/tilde direct reset, fleet `1/2` centroid tracking with manual angle retention after initialization, a right-drag-safe track lock path, a small gear-aware playback stabilizer on tracked focus motion, and broader zoom/pitch comfort limits
- current Step 3 formation work is draft-only and document-only; no formation runtime/mapping/legality implementation is active
- current formation-reference document line is structurally complete in bounded scope across frame / layout / spacing opening notes
- current mapping line has repo-side scope-confirmation and minimum-contract working records only; the legality line now has merged opening-scope and minimum-contract/stabilization records plus a merged first bounded runtime/harness implementation baseline and active hardening records
- current GitHub collaboration mode now has an active repo-side workflow document under `docs/engineering/` for carrier-by-carrier branch / PR review
- cross-thread protocol v1.4 now makes minimal human-readable evidence an explicit control requirement for substantive runtime modifications
- the legality line now also has an active bounded hardening working charter under `docs/engineering/`, allowing multiple bounded baseline-hardening iterations until a real governance trigger is reached
- current bounded standard-rectangle root-cause read is now recorded locally under `analysis/engineering_reports/developments/20260328/`; current engineering read is that the early `aspect_ratio = 1.0 / 4.0` stretching is a runtime movement-vs-restore issue rather than malformed reference layout generation or a viewer-only artifact
- a follow-up spacing-decoupling probe note now also exists under `analysis/engineering_reports/developments/20260328/`; current engineering read is that the overloaded low-level spacing radius is a major amplifier in the same early standard-rectangle stretch issue, but that result is still diagnostic-only and pre-implementation
- a new two-layer spacing opening package now starts under `analysis/engineering_reports/developments/20260329/`; current engineering read is that the concept line is open structurally, a second bounded comparison path still supports the spacing-decoupling result, and governance is now also being asked whether `v4a` should be reviewed as a possible shared neutral+battle default candidate while keeping `v3a` retained
- the `20260329` package now also includes implementation-prep discussion for two-layer spacing and a bounded shared default-review discussion note for `v4a`; current engineering read is still discussion-only, with no spacing implementation and no default switch authorized
- the `20260329` package now also includes a battle-path-relevant next evidence pack; current engineering read is that the `expected/reference spacing = 2.0` vs `runtime low-level floor = 1.0` split remains materially important outside the earlier fixture-only frame, but still does not by itself authorize silent implementation
- the post-PR6 cleanup line now keeps the two-layer spacing / soft-morphology / transition / battle-standoff opening package while narrowing ownership truth: maintained battle still reads direct `v4a` test-only reference settings (`expected_reference_spacing`, `reference_layout_mode`), but `v4a.restore_strength` is now carried by a native `v4a` runtime seam rather than the old `v3_test` centroid-probe bridge
- the same cleanup line now also narrows old-family public surface in `test_run/`: stale restore-bridge truth surfaces are gone from active `v4a`, `continuous_fr_shaping` has been retired from the harness/settings path, and `pre_tl_target_substrate` has been retired as a public test-only knob while the old non-bundle fallback target read is reduced to one fixed nearest-5-centroid behavior
- the same PR #6 branch now also adds a bounded `soft_morphology_v1` reference-surface carrier under `runtime.movement.v4a.test_only`; current branch-only read is that the branch now has a first credible soft planar formation-reference carrier with alive-ratio-driven morphology state and stable broad-band ownership, but neutral-transit still reads tighter than a fully settled "living formation" substrate
- the same PR #6 branch now also carries a bounded transition-movement seam package under `runtime.movement.v4a.test_only`; current branch-only read is that `shape_vs_advance_strength`, `heading_relaxation`, and continuous material-phase transport materially reduce the earlier non-arrival bug, while the harness-only morphology-level terminal/hold stage has since been disabled locally after Human read judged its arrival regularization too discrete
- the same PR #6 branch now also adds a new Round 1 / Round 2 formation-transition package under `analysis/engineering_reports/developments/20260330/` plus additional `runtime.movement.v4a.test_only` seams in `test_run/`; current branch-only read is that battle target can now be read through a bounded fleet-level standoff distance plus a unit-level attack-direction-aware speed envelope, while Human read says these seams are directionally correct but now expose the next battle problem more clearly: drifting fire-plane geometry, wing-localized engagement, and rotating contact around a local junction
- the same `20260329` branch package now also includes a bounded turning-cost / heading-inertia discussion note plus a future 3D runtime computation-principles review note; both remain methodology discussion only and do not authorize implementation or default switching
- no parallel simulation settings surface is owned by `viz3d_panda/`
- no 3D runtime combat/movement baseline is established by this surface

## Settings Paths

- `test_run/test_run_v1_0.settings.json`
  - thin entry settings / layer pointer
- `test_run/test_run_v1_0.runtime.settings.json`
  - runtime values
  - `run_control.post_resolution_hold_steps` is now the authoritative harness/runtime hold-window control for battle-resolution and neutral objective-arrival continuation
  - current `dev_v2.1` local runtime line also adds `runtime.physical.fire_control.fire_optimal_range_ratio` as the bounded range-quality carrier for the current targeting candidate and the active battle hold-gap base
- `test_run/test_run_v1_0.testonly.settings.json`
  - test-only harness controls
  - active local movement seams currently include bounded `v4a` transition-movement / terminal controls used only in `test_run`; `v4a.restore_strength` is now a direct native `v4a` restore seam, the first near-contact smoothing group remains active on the local `v4a` line, and `fixture.neutral.stop_radius` is the neutral-only objective termination radius
  - the same local cleanup line has retired the public `continuous_fr_shaping` and `pre_tl_target_substrate` settings surfaces; retained `v3a` support surfaces are now narrower and explicitly legacy
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
- `analysis/engineering_reports/developments/20260327/dev_v2_0_preformation_viewer_state_governance_memo_20260327.md`
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
- `analysis/engineering_reports/developments/20260327/step3_3d_formation_frame_structural_confirmation_note_20260328.md`
- `analysis/engineering_reports/developments/20260327/step3_3d_formation_layout_structural_confirmation_note_20260328.md`
- `analysis/engineering_reports/developments/20260327/step3_3d_formation_spacing_structural_confirmation_note_20260328.md`
- `analysis/engineering_reports/developments/20260327/step3_3d_mapping_opening_scope_confirmation_note_20260328.md`
- `analysis/engineering_reports/developments/20260327/step3_3d_mapping_minimum_contract_structural_draft_note_20260328.md`
- `analysis/engineering_reports/developments/20260327/step3_3d_legality_opening_scope_confirmation_note_20260328.md`
- `analysis/engineering_reports/developments/20260327/step3_3d_legality_minimum_contract_structural_draft_note_20260328.md`
- `analysis/engineering_reports/developments/20260327/step3_3d_legality_contract_stabilization_note_20260328.md`
- `analysis/engineering_reports/developments/20260327/step3_3d_legality_touchpoint_inventory_note_20260328.md`
- `analysis/engineering_reports/developments/20260327/step3_3d_legality_interface_surface_stabilization_note_20260328.md`
- `analysis/engineering_reports/developments/20260327/step3_3d_legality_consumer_boundary_note_20260328.md`
- `analysis/engineering_reports/developments/20260327/step3_3d_legality_post_handoff_ownership_note_20260328.md`
- `analysis/engineering_reports/developments/20260327/step3_3d_legality_runtime_integration_envelope_note_20260328.md`
- `analysis/engineering_reports/developments/20260327/step3_3d_legality_touchpoint_placement_decision_note_20260328.md`
- `analysis/engineering_reports/developments/20260327/step3_3d_legality_data_surface_decision_note_20260328.md`
- `analysis/engineering_reports/developments/20260327/step3_3d_legality_execution_order_decision_note_20260328.md`
- `analysis/engineering_reports/developments/20260327/step3_3d_legality_first_bounded_implementation_plan_20260328.md`
- `analysis/engineering_reports/developments/20260328/step3_3d_legality_first_bounded_implementation_report_20260328.md`
- `analysis/engineering_reports/developments/20260328/step3_3d_legality_first_bounded_baseline_validation_pack_20260328.md`
- `analysis/engineering_reports/developments/20260328/step3_3d_standard_rectangle_root_cause_probe_note_20260328.md`
- `analysis/engineering_reports/developments/20260328/step3_3d_standard_rectangle_spacing_decoupling_probe_note_20260329.md`
- `analysis/engineering_reports/developments/20260328/test_run_post_resolution_hold_steps_runtime_surface_note_20260329.md`
- `analysis/engineering_reports/developments/20260328/step3_3d_standard_rectangle_expected_spacing_governance_request_20260329.md`
- `analysis/engineering_reports/developments/20260329/step3_3d_two_layer_spacing_opening_scope_note_20260329.md`
- `analysis/engineering_reports/developments/20260329/step3_3d_two_layer_spacing_followup_and_v4a_default_request_20260329.md`
- `analysis/engineering_reports/developments/20260329/step3_3d_two_layer_spacing_implementation_prep_discussion_note_20260329.md`
- `analysis/engineering_reports/developments/20260329/step3_3d_v4a_shared_default_review_discussion_note_20260329.md`
- `analysis/engineering_reports/developments/20260329/step3_3d_two_layer_spacing_next_evidence_pack_20260329.md`
- `analysis/engineering_reports/developments/20260329/step3_3d_two_layer_spacing_battle_compact_comparison_20260329.csv`
- `analysis/engineering_reports/developments/20260401/step3_3d_pr6_far_field_target_and_engagement_geometry_design_note_20260401.md`
- `analysis/engineering_reports/developments/20260401/step3_3d_pr6_far_field_target_cleanup_local_note_20260401.md`
- `analysis/engineering_reports/developments/20260401/step3_3d_pr6_human_motion_read_rubric_note_20260401.md`
- `analysis/engineering_reports/developments/20260401/step3_3d_pr6_literature_review_background_and_goal_note_20260401.md`
- `docs/engineering/GitHub_Branch_PR_Collaboration_Workflow_v1.0.md`
- `docs/engineering/Legality_First_Bounded_Baseline_Hardening_Working_Charter_v1.0.md`
- `docs/archive/ts_handoff_archive/`
  - current long-term home for TS handoff packages previously stored under the top-level `archive/` path
- `docs/exports/`
  - current repo-side home for exported reports / flowcharts / formulas
- `viz3d_panda/docs/3D_VIZ_Debug_Block_Reference_v1.0.md`
  - maintained viewer-side reference for the 3D HUD/debug block and current focus indicators
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
- `analysis/engineering_reports/developments/20260404/step3_3d_pr6_formal_failure_audit_20260404.md`
  - formal failure audit for the local `v4a` incident thread; use together with the TS handoff as incident-scene / recovery context, not as merge-readiness evidence

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
