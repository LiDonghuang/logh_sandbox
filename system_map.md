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

### 3. Maintained Harness Spine

- `test_run/test_run_entry.py`
  - thin maintained 2D launcher ground truth
  - routine run, daily animation, video export, and BRF handoff
- `test_run/test_run_scenario.py`
  - settings resolution, archetype/build helper surface, and initial scenario build
- `test_run/test_run_execution.py`
  - battle execution host, maintained outputs, and engine-adjacent harness skeleton host
- `test_run/test_run_telemetry.py`
  - observer / bridge / collapse-shadow collection

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

### 8. Additive 3D Viewer Bootstrap Layer

- `viz3d_panda/app.py`
  - Panda3D viewer entrypoint and playback loop; owns launch/playback wiring only
- `viz3d_panda/replay_source.py`
  - in-memory replay bundle build from existing `test_run` returned `position_frames`; replay consumption only
- `viz3d_panda/scene_builder.py`
  - simple viewer-local scene/grid/light setup
- `viz3d_panda/unit_renderer.py`
  - wedge-token unit rendering with viewer-local HP size buckets
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
- limited visual refinement active: deeper semi-transparent side colors and subordinate straight-beam fire-links with `minimal` / `full` viewer-local display modes
- launch semantics aligned: default viewer runs inherit layered `run_control.max_time_steps`
- anti-fat guardrail active: viewer consumes, runtime owns
- Step 3 opening review is doc-only: a minimum 3D objective contract draft and bounded neutral-transit first-carrier notes now exist under `analysis/`
- Step 3 next-mainline planning is also doc-only: first bounded fixture-side implementation touchpoints and validation notes now exist under `analysis/`
- Step 3 first implementation is now bounded to the neutral-transit fixture path: `objective_contract_3d` exists there, is consumed as projected `xy`, and is validated on the harness side only
- the Panda3D viewer still reads the active battle replay path only; it does not yet consume the neutral-transit fixture path and therefore needs a separate governance clarification before any viewer-side hookup
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
