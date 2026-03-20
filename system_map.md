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
  - thin maintained launcher ground truth
  - routine run, daily animation, video export, and BRF handoff
- `test_run/test_run_scenario.py`
  - settings resolution and initial scenario build
- `test_run/test_run_execution.py`
  - battle execution host and maintained outputs
- `test_run/test_run_telemetry.py`
  - observer / bridge / collapse-shadow collection

### 4. Legacy / Transitional Harness Layer

- `test_run/test_run_v1_0.py`
  - transitional helper host and historical launcher shim
- `test_run/test_run_experiments.py`
  - transitional shell over the maintained spine
- `test_run/settings_accessor.py`
  - layered settings load and access

### 5. Optional Report / Visualization Layer

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

## Current Structural Tension

The current reset target is now concentrated in one remaining helper host plus optional heavy paths:

- `test_run/test_run_v1_0.py` still sits under the maintained spine as a helper anchor
- BRF and viz paths remain physically present and callable from the maintained launcher
- the maintained spine is smaller, but the historical helper surface has not been fully retired yet

## Practical Interpretation Rule

Read the current maintained path as:

schema -> engine -> maintained harness spine -> optional report/viz surfaces

Do not read observer wording as runtime ontology.
Do not read test-only selectors as canonical semantics.
