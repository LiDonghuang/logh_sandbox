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

### 3. Maintained Harness Spine

- `test_run/test_run_entry.py`
  - thin maintained entry
- `test_run/test_run_scenario.py`
  - settings resolution and initial scenario build
- `test_run/test_run_execution.py`
  - battle execution host and maintained outputs
- `test_run/test_run_telemetry.py`
  - observer / bridge / collapse-shadow collection

### 4. Legacy / Transitional Harness Layer

- `test_run/test_run_main.py`
  - legacy full launcher orchestration
  - settings interpretation
  - export / viz handoff
- `test_run/test_run_v1_0.py`
  - historical launcher target shell
- `test_run/test_run_experiments.py`
  - transitional shell over the maintained spine
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

The current reset target is now split across the legacy layer and optional heavy paths:

- `test_run/test_run_main.py` still carries the old full-launcher weight
- legacy viz / report paths remain physically present
- the maintained spine is smaller, but the old tree has not been fully retired yet

## Practical Interpretation Rule

Read the system as:

schema -> engine -> maintained harness spine -> legacy launcher shell -> viz/observer

Do not read observer wording as runtime ontology.
Do not read test-only selectors as canonical semantics.
