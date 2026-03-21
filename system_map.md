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

### 3. Maintained Harness Spine

- `test_run/test_run_entry.py`
  - thin maintained launcher ground truth
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

## Current Structural Tension

The current maintained launcher path no longer depends on old launcher shells.

Current remaining burden centers are:

- active auxiliary BRF / viz weight
- large maintained execution host weight
- frozen runtime skeleton weight outside the harness scope

## Practical Interpretation Rule

Read the current maintained path as:

schema -> engine -> maintained harness spine -> active auxiliary surface

Do not read observer wording as runtime ontology.
Do not read test-only selectors as canonical semantics.
