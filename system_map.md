# LOGH Sandbox System Map

Status: Working System Map  
Purpose: Fast structural orientation for governance-side repo reading  
Authority: Reference only, not canonical semantics authority

## Layer Map

### 1. Schema Layer

- `runtime/runtime_v0_1.py`
- Defines:
  - `PersonalityParameters`
  - `Vec2`
  - `UnitState`
  - `FleetState`
  - `BattleState`

### 2. Engine Layer

- `runtime/engine_skeleton.py`
- Main tick pipeline:
  - `evaluate_cohesion`
  - `evaluate_target`
  - `evaluate_utility`
  - `integrate_movement`
  - `resolve_combat`
- Current maintained cohesion evaluation is selected inside runtime; the maintained harness no longer owns a duplicate v3 geometry host
- Current runtime hot-path reduction uses one local 2D spatial-hash helper across:
  - combat candidate generation
  - movement pair pruning with preserved original pair ordering
  - cohesion connectivity / largest connected component search
- Current branch/PR candidate also exposes one first bounded legality seam inside `integrate_movement`: mapping-produced reference-position intake, legality-owned middle-stage tracing, and feasible-position handoff

### 3. Maintained Harness Spine

- `test_run/test_run_entry.py`
  - thin maintained 2D launcher ground truth
  - routine run, daily animation, video export, and BRF handoff
- `test_run/test_run_scenario.py`
  - settings resolution, archetype/build helper surface, and initial scenario build
- `test_run/test_run_execution.py`
  - battle execution host, maintained outputs, and engine-adjacent harness skeleton host
  - current branch/PR candidate reuses existing fixture metrics for legality surface counts and handoff-stage flags
- `test_run/test_run_telemetry.py`
  - observer / bridge / collapse-shadow collection
  - current branch/PR candidate exposes a minimal legality echo through the existing runtime debug payload extraction path

### 4. Harness Support Layer

- `test_run/settings_accessor.py`
  - layered settings load and access

### 5. Active Auxiliary Surface

- `test_run/battle_report_builder.py`
  - battle report markdown assembly
- `test_run/brf_narrative_messages.py`
  - battle report narrative message library

- `test_run/test_run_v1_0_viz.py`
- Role:
  - battlefield rendering
  - plot panel display
  - animation/export display path

### 6. Settings Layer

- `test_run/test_run_v1_0.settings.json`
- `test_run/test_run_v1_0.runtime.settings.json`
- `test_run/test_run_v1_0.testonly.settings.json`
- `test_run/test_run_v1_0.viz.settings.json`
- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`

### 7. Documentation Layer

- `docs/README.md`
  - repo-side documentation entry with canonical / context / reference / archive separation
- `docs/APP_Files_Prefix_Mapping_v1.0.md`
  - APP-side flat mirror policy and active 11-file governance working set
- `docs/engineering/GitHub_Branch_PR_Collaboration_Workflow_v1.0.md`
  - active engineering workflow for direct-push vs branch + PR carrier review

### 8. Additive 3D Viewer Bootstrap Layer

- `viz3d_panda/app.py`
  - Panda3D viewer entrypoint and playback loop; owns launch/playback wiring, low-speed smoothing, and fixed-size screen-space avatar overlay only
- `viz3d_panda/replay_source.py`
  - in-memory replay bundle build from existing `test_run` returned `position_frames`; replay consumption only
- `viz3d_panda/scene_builder.py`
  - simple viewer-local scene/grid/light setup
- `viz3d_panda/unit_renderer.py`
  - wedge-token unit rendering with viewer-local HP size buckets plus minimal objective marker, lighter two-ring fleet halo overlays, and dual-layer close-range cluster rendering
- `viz3d_panda/camera_controller.py`
  - simple viewer-local orbit/pan/zoom controls
- `launch_dev_v2_0_viewer.bat`
  - thin human-facing launcher
- `.vscode/launch.json`
  - includes `dev_v2.0 Viewer (Panda3D)` launch entry for local debug/run use

Current availability:

- active on `dev_v2.0`
- viewer/replay bootstrap only
- additive to the current 2D maintained path
- readability pass active: single semi-transparent wedge token replaces the earlier thin line-arrow marker
- current fire-link surface is reduced to `enabled` / `disabled`; enabled now means a corrected-center pulse-train multi-beam cue rather than the old `minimal` / `full` straight-beam family
- unit visual enhancement active: far-range wedge readability now cross-fades into a near-range fixed 10-cuboid internal cluster, still within viewer-local rendering only
- unit origin is now corrected at the rendered geometry source, so unit coordinates and rendered geometry center align in `x / y / z` without a separate visual-center helper
- inner cluster size is now fixed per cuboid while HP bucket changes visible count only
- current close-range cluster is laid out as a trapezoid-friendly non-uniform `2/3/5` row set with margin inside the outer body; the outer token has been pulled back from an overly sharp dart read toward a broader trapezoid-like read, and the inner cuboids are now slightly larger, more spread toward the frame outline, and more visibly staggered in `z`
- launch semantics aligned: default viewer runs inherit layered `run_control.max_time_steps`
- anti-fat guardrail active: viewer consumes, runtime owns
- viewer-local control refinements now include hold-to-repeat `N/B` stepping, backquote/tilde direct reset, a near-top-down reset camera, fleet `1/2` centroid tracking that preserves manual angle adjustments after initialization, a right-drag-safe track lock path, a small gear-aware tracked-camera anti-jitter profile, and broader zoom/pitch limits
- viewer-local direction readout now includes `realistic`; current local shape reads as a short-window travel-posture mode, and low-speed playback now uses transform-only smoothing rather than rebuilding a synthetic smoothed frame
- fire-link presentation now uses low-speed endpoint smoothing, viewer-time-driven `sqrt(gear)` pulse motion, deterministic outer-beam alternation on an independent slow clock, and near/mid-only rendering with far-range suppression
- a debug-only `objective_area_realistic` investigation record set now exists for `neutral_transit_v1`; in the `objective_reached_tick +/- 5` window, effective flips far more than realistic, the widest centered candidate source dominates, and smoothing is not the primary source of the residual
- a debug-only late-terminal residual decomposition record set now exists for `neutral_transit_v1`; current read is that after centroid-level arrival, moving expected-position restore becomes the strongest surviving driver while separation/projection reshape the remaining unit motion
- the prior whole-frame late-terminal freeze first cut is now superseded locally for the candidate-active `neutral_transit_v1` path by an orientation-freeze / live-centroid split cut: the terminal axis is latched while the expected-position center keeps following the live centroid
- the current best local late-terminal candidate now adds two bounded terminal-window cuts on top of that split cut: per-unit step magnitude is reduced inside the existing stop-radius window, and only backward axial restore is softened; current local read is that this is the best candidate so far, while a stricter no-net-backward follow-up was locally rejected because it introduced a new rotational artifact
- current engineering read is that the late-terminal result may also inform the unresolved early restoration problem, because the successful bounded improvement was component-wise and one-sided rather than purely scalar
- Step 3 objective line is now sufficiently established in bounded scope: draft, bounded first carrier, harness-side validation, and very small viewer-consumption hookup are all complete
- Step 3 first implementation remains bounded to the neutral-transit fixture path: `objective_contract_3d` exists there, is consumed as projected `xy`, and is validated on the harness side only
- the Panda3D viewer now supports a very small viewer-consumption hookup for the bounded neutral-transit fixture path via `viz3d_panda/replay_source.py` and `viz3d_panda/app.py`
- current viewer-side neutral-transit support now includes source selection, small contract echo overlay, a single-fleet objective marker, and lighter two-ring per-fleet halos, while semantic ownership remains outside the viewer
- current viewer-side fleet avatar support is fixed-size, screen-space, `4:5`, toggleable with local `P` portraits on/off control, uses per-fleet grouped layering, falls back to midpoint-based side-by-side layout when two battle fleets project too close on screen, re-solves during paused camera movement, and now uses a small gear-aware anti-jitter profile during playback
- current dual-layer unit rendering includes a minimal transparency-order correction intended to reduce inner-cluster occlusion by the transparent outer shell, plus near/mid/far cluster fading and transform-only smoothing of motion-facing elements
- a stage governance memo now records the accepted pre-Formation viewer-only state under `analysis/engineering_reports/developments/20260327/`; this is a local-state governance memo, not canonical governance authority
- a simplified warship-like proxy remains proposal-only and is not an active unit-rendering path
- a viewer-local governance query is now recorded for whether HP may reduce the close-range inner cluster cuboid count while keeping per-cuboid size fixed; query-only, not active
- the formation-reference document line is now structurally completed in bounded scope across frame / layout / spacing opening notes
- the mapping line remains at scope-confirmation plus minimum-contract working records; the legality line now spans merged opening-scope, minimum-contract, contract-stabilization, touchpoint/interface/consumer-boundary, runtime-integration-envelope, implementation-prep decision/plan records, and a first bounded runtime/harness implementation attempt report under `analysis/engineering_reports/developments/20260327/` and `analysis/engineering_reports/developments/20260328/`
- the failed early-side `E2` candidate was withdrawn during subtraction-first cleanup; active bounded neutral-transit corrections now read as first-turn `A1 + B1` plus a post-cleanup late-only terminal non-overshoot clamp in `test_run/test_run_execution.py`
- late-stage `realistic` human-read residual around the objective remains open as a viewer-local/readout issue and is not currently claimed as closed
- late terminal settle root-cause work is now being read primarily as a solver-layer residual rather than a viewer-primary issue
- the HP-bucketed inner-cluster-count query remains deferred / not active during this investigation turn
- GitHub collaboration mode now has a repo-side workflow document under `docs/engineering/`; larger structure-sensitive carriers should preferentially use branch + PR review into `dev_v2.0`
- no parallel simulation settings or replay-protocol ownership lives here
- no 3D runtime semantics or baseline protocol owned here

## Current Structural Tension

The current maintained launcher path no longer depends on old launcher shells, and Phase A is now functionally closed out rather than still acting as launcher-reset headline work.

Current remaining burden centers are:

- active auxiliary BRF / viz weight
- large maintained execution host weight
- maintained telemetry pairwise cost
- residual runtime skeleton weight after successful bounded cleanup/performance rounds
- viewer bootstrap replay ergonomics and remaining human-readability refinement inside `viz3d_panda/`

These are post-closeout maintained-path debts, not reasons to reopen old compatibility or launcher-reset work.

## Practical Interpretation Rule

Read the current maintained path as:

schema -> engine -> maintained harness spine -> active auxiliary surface

Read the new viewer bootstrap as:

maintained harness output -> additive `viz3d_panda/` replay/view layer

Do not read observer wording as runtime ontology.
Do not read test-only selectors as canonical semantics.
Do not read the Panda3D bootstrap container as a 3D combat-engine baseline.
Do not read `viz3d_panda/` as a future-proof license to absorb simulation ownership.
