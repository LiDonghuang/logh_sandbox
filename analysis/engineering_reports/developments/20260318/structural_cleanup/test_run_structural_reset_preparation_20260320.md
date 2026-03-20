# Test Run Structural Reset Preparation (2026-03-20)

Status: structural reset preparation  
Scope: `test_run` active surface reset / legacy amnesty preparation  
Classification: preparation only / non-runtime-semantic / non-canonical

## 1. Identity

This document records the preparation round requested by governance under:

- `Phase A Structural Reset Directive`
- `Active Surface Reset / Legacy Amnesty`

This round does **not** claim:

- simplification success
- accepted cleanup
- refactor completed

This round claims only:

- `Active Surface Proposed`
- `Legacy Amnesty Inventory Prepared`
- `Deletion Plan Prepared`
- `Boundary Proposal Prepared`

No runtime semantics changed in this turn.

## 2. Current Structural Problem

The current pushed `test_run` state is stable enough to run routine validation, but it is not a convincing maintained spine.

Current structural pain points:

- `test_run/test_run_main.py` still mixes launcher orchestration, settings assembly, report export, and viz handoff.
- `test_run/test_run_experiments.py` still mixes execution, telemetry assembly, observer-side metrics, frame capture, and normalization in one hot path.
- `test_run/test_run_v1_0.py` still carries historical accumulation and should not remain the future authority host.
- `test_run/test_run_v1_0_viz.py` and battle-report/export paths are too heavy to remain default active-surface obligations.

Therefore the next phase should not be more cleanup-in-place on the old tree.

It should be:

- define a new minimal maintained spine
- port forward only explicitly approved capabilities
- freeze or retire the rest

## 3. Deliverable 1 - Active Surface Definition

### 3.1 Future Maintained Spine

The future maintained spine should be limited to the following modules and files.

#### A. Active Config Surface

- `test_run/settings_accessor.py`
  - unique role: layered settings load and narrow access to maintained runtime/test-only settings
- `test_run/test_run_v1_0.settings.json`
  - unique role: human-edited base harness settings shell
- `test_run/test_run_v1_0.runtime.settings.json`
  - unique role: maintained runtime-layer settings
- `test_run/test_run_v1_0.testonly.settings.json`
  - unique role: maintained test-only settings needed for harness execution and routine regression

#### B. Active Routine Validation Surface

- `test_run/test_run_anchor_regression.py`
  - unique role: fixed routine `3-run` anchor gate

#### C. Future Maintained Harness Spine

These are the modules that should exist after the reset round. They are the only code-level spine that should remain actively maintained.

- `test_run/test_run_entry.py` or equivalent new thin entry module
  - unique role: minimal CLI/launcher entry only
  - responsibilities: load settings, choose scenario, call scenario build, call execution, optionally call routine regression
- `test_run/test_run_scenario.py` or equivalent new scenario-build module
  - unique role: build initial state and scenario inputs only
  - responsibilities: archetype resolution, fleet/unit/battlefield scenario build, seed resolution
- `test_run/test_run_execution.py` or equivalent new execution module
  - unique role: battle execution spine only
  - responsibilities: run battle, return final state, return minimal trajectories required by routine regression and minimal launcher summary
- `test_run/test_run_telemetry.py` or equivalent new optional telemetry collection module
  - unique role: optional observer/telemetry-side collection outside the execution hot path
  - responsibilities: frame capture, bridge/collapse-shadow collection, optional observer metrics, optional viz/report handoff payloads

#### D. Reset Hard Rule

The reset round is not allowed to recreate the old mixed tree under new filenames.

More concretely:

- entry may only remain a thin entry
- scenario may only do build/resolve work
- execution may only do battle execution plus minimal maintained outputs
- telemetry may only do optional add-on collection

If one of these modules regains mixed old-tree responsibilities, the reset round should be treated as failed rather than accepted.

### 3.2 Files That Should Remain Only As Transitional Shells Or Reference

- `test_run/test_run_main.py`
  - transitional shell only until replaced by the new thin entry spine
- `test_run/test_run_experiments.py`
  - transitional mixed hot path to be split; should not remain the final maintained execution host
- `test_run/test_run_v1_0.py`
  - reference/transitional shell only; not future authority host
- `test_run/test_run_v1_0.settings.comments.json`
  - reference/comment companion only; not hot-path authority
- `test_run/test_run_v1_0.settings.reference.md`
  - reference only

### 3.3 Files Planned To Exit Active Surface

- `test_run/test_run_v1_0_viz.py`
- `test_run/test_run_v1_0.viz.settings.json`
- `test_run/battle_report_builder.py`
- `test_run/brf_narrative_messages.py`

These may remain in repo history or as optional legacy/reference paths, but they should not remain part of the maintained hot path.

## 4. Deliverable 2 - Legacy Amnesty Inventory

### 4.1 No Longer Maintained Compatibility Targets

The following are explicitly de-scoped from maintained compatibility:

- `analysis/engineering_reports/developments/...`
- historical DOE runners
- historical audit runners
- one-off development scripts
- old temporary direct callers of the previous harness surface

### 4.2 No Longer Port-Forwarded By Default

Unless separately re-approved, the following do not automatically move into the new maintained spine:

- battle report export path
- BRF narrative assembly path
- rich viz/render/export-video path
- rich observer-side diagnostic panels
- historical test-phase mode/toggle/candidate surface
- historical compatibility wrappers or adapter layers

### 4.3 Old Surfaces Covered By Amnesty

The following old surfaces should no longer constrain new spine design:

- old `run_simulation(...)` historical scalar-call expectations
- launcher-side report/viz export obligations inside the default run path
- history-shaped helper surfaces inside `test_run_main.py`
- mixed execution plus observer-side assembly inside `test_run_experiments.py`
- `test_run_v1_0.py` as an assumed long-term host for future restructuring

### 4.4 Legacy/Reference Paths Governance May Still Inspect

- `test_run/test_run_main.py`
- `test_run/test_run_experiments.py`
- `test_run/test_run_v1_0.py`
- `test_run/test_run_v1_0_viz.py`
- `test_run/battle_report_builder.py`
- `test_run/brf_narrative_messages.py`
- `analysis/engineering_reports/developments/...`

These remain available as historical/reference material, but not as active design constraints.

## 5. Deliverable 3 - Deletion Plan

### 5.1 Batch 1 - Status Demotion First

First batch should freeze or explicitly demote these paths from active surface:

- `test_run/test_run_v1_0_viz.py`
- `test_run/test_run_v1_0.viz.settings.json`
- `test_run/battle_report_builder.py`
- `test_run/brf_narrative_messages.py`
- `analysis/engineering_reports/developments/...`

Effect:

- they stop constraining active spine design
- they stop counting as maintained hot-path obligations

Important governance meaning:

- `freeze` here means governance/status demotion first
- it does **not** require immediate physical deletion in the same first batch

Physical deletion should come later, after the new maintained spine has taken over routine execution and regression successfully.

### 5.2 Batch 2 - Port Forward Minimal Maintained Spine

Second batch should create the new maintained spine and port forward only approved capabilities:

- minimal settings load
- scenario build
- execution
- routine `3-run` regression

Capabilities that must remain runnable after Batch 2:

- build initial state
- run a battle
- produce the routine summary data needed by `test_run_anchor_regression.py`
- pass the fixed `3-run` anchor gate

New spine acceptance must be strict.

The new spine should count as established only when **all** of the following are true:

- `test_run/test_run_anchor_regression.py` is wired to the new spine
- routine `3-run` anchor regression passes through the new spine
- the default maintained hot path no longer imports or depends on:
  - `test_run/test_run_v1_0_viz.py`
  - `test_run/battle_report_builder.py`
  - `test_run/brf_narrative_messages.py`
- `test_run/test_run_main.py`, `test_run/test_run_experiments.py`, and `test_run/test_run_v1_0.py` no longer act as the primary maintained entry/execution hosts

This means:

- creating new files is not enough
- naming a new spine is not enough
- the new spine succeeds only when it has actually taken over routine run plus regression, while the old heavy hosts have exited the maintained primary path

### 5.3 Batch 3 - Retire Old Mixed Hot Paths

Once the new spine is runnable, retire or demote these paths from maintained status:

- `test_run/test_run_main.py` as current orchestration host
- `test_run/test_run_experiments.py` as the mixed execution/telemetry/observer host
- `test_run/test_run_v1_0.py` as a presumed future core shell

Retirement options:

- delete
- freeze
- keep as legacy reference only

The exact choice can vary by file, but they should not continue as the maintained primary path.

Physical deletion is appropriate here only after Batch 2 has already satisfied the new-spine acceptance standard.

### 5.4 How Routine Regression Remains Stable

Routine regression remains stable by preserving:

- `test_run/settings_accessor.py`
- `test_run/test_run_anchor_regression.py`
- the current anchor file: `analysis/engineering_reports/developments/20260318/structural_cleanup/a5_iteration0_baseline_anchor_20260318.json`
- the maintained runtime/test-only settings JSON layers

The new spine must preserve only the data contract that the routine `3-run` gate actually needs.

It does **not** need to preserve legacy viz/report/export surfaces.

## 6. Deliverable 4 - Boundary Proposal

This proposal stays inside the only boundary governance explicitly authorized for this round:

- `execution`
- `telemetry / observer-side collection`

### 6.1 Proposed Execution Boundary

Execution should own only:

- engine tick loop
- battle state transitions
- minimal alive/fleet-size/cohesion trajectories required by maintained validation
- minimal final-state return

Execution should **not** own:

- frame rendering preparation
- report inference assembly
- viz/export branching
- rich observer diagnostic formatting
- optional historical analysis payload shaping

### 6.2 Proposed Telemetry / Observer Boundary

Telemetry / observer-side collection should own only optional add-on responsibilities:

- position frame capture
- attack-target geometry capture
- event bridge collection
- collapse-shadow collection
- optional observer metric series
- optional viz/report payload preparation

This side should become:

- explicitly optional
- detachable from the default execution hot path
- non-authoritative for runtime semantics

### 6.3 Minimal Contract Between The Two Sides

The execution side should expose only a narrow contract to telemetry collection:

- final state
- tick count
- minimal maintained trajectories
- optional per-tick state snapshots only when explicitly requested

The telemetry side may consume that contract, but should not continue to define the execution interface shape.

## 7. Immediate Next Reset Round Recommendation

The first code round after this preparation should be:

- execution-spine extraction first
- not viz cleanup
- not battle-report cleanup
- not more launcher-only subtraction

Recommended order:

1. create the new minimal entry/scenario/execution spine
2. wire `test_run_anchor_regression.py` to the new spine
3. verify the fixed `3-run` gate still passes
4. freeze old mixed hot paths from active-surface status

Success standard for that next code round:

- the new spine owns routine run plus routine regression
- the old heavy paths no longer serve as primary maintained hosts
- the maintained hot path no longer depends on viz/report legacy surfaces
- the new modules have not re-created the old mixed tree under new names

## 8. Governance Inspection Paths

Governance should inspect these current repo paths directly:

### Current hot paths

- `test_run/test_run_main.py`
- `test_run/test_run_experiments.py`
- `test_run/test_run_v1_0.py`

### Current maintained validation/config anchors

- `test_run/settings_accessor.py`
- `test_run/test_run_anchor_regression.py`
- `test_run/test_run_v1_0.settings.json`
- `test_run/test_run_v1_0.runtime.settings.json`
- `test_run/test_run_v1_0.testonly.settings.json`
- `analysis/engineering_reports/developments/20260318/structural_cleanup/a5_iteration0_baseline_anchor_20260318.json`

### Legacy-heavy optional paths

- `test_run/test_run_v1_0_viz.py`
- `test_run/test_run_v1_0.viz.settings.json`
- `test_run/battle_report_builder.py`
- `test_run/brf_narrative_messages.py`

### Historical non-maintained direct callers

- `analysis/engineering_reports/developments/...`

## 9. Required Reporting Formula For This Round

This round should be reported exactly as:

- `Active Surface Proposed`
- `Legacy Amnesty Inventory Prepared`
- `Deletion Plan Prepared`
- `No runtime semantics changed in this turn`
