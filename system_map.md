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

### 3. Harness Core Layer

- `test_run/test_run_v1_0.py`
- Role:
  - engine-facing harness core
  - shared helper surface for launcher/harness

### 4. Launcher / Experiment Layer

- `test_run/test_run_main.py`
  - run orchestration
  - settings interpretation
  - export / viz handoff
- `test_run/test_run_experiments.py`
  - build initial state
  - execute simulation
  - collect observer/combat telemetry
- `test_run/settings_accessor.py`
  - layered settings load and access

### 5. Visualization / Observer Display Layer

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

## Current Structural Tension

The current simplification target is mostly inside the harness layer:

- `test_run/test_run_main.py` is still too large and too parameter-heavy
- launcher/core boundaries are cleaner than before, but not yet minimal
- default stdout has been reduced, but interface width remains high

## Practical Interpretation Rule

Read the system as:

schema -> engine -> harness core -> launcher/experiments -> viz/observer

Do not read observer wording as runtime ontology.
Do not read test-only selectors as canonical semantics.
