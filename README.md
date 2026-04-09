# Fleet Sandbox

Fleet Sandbox is a strategic fleet-combat simulation sandbox focused on deterministic runtime behavior, parameterized strategic archetypes, and controlled governance-driven engineering evolution.

This repository is the engineering workspace for the Python runtime line (Phase III onward), with frozen conceptual/governance artifacts retained as canonical references.

## Project Status

- Current execution baseline: `v5.0-alpha5`
- Current movement baseline: `v4a`
- Maintained `test_run` mainline no longer supports explicit `v3a` movement execution
- Current maintained runtime cohesion geometry: fixed `v3_test`
- Runtime language: `Python 3.11`
- Governance model: App thread = governance; VS Code/Codex thread = engineering execution

## Phase Context

- Phase I (frozen): Theoretical Foundation
  - Strategic archetypes
  - 10-dimensional personality parameter space
  - Governance and cross-thread protocol
- Phase II (frozen): Engine Skeleton
  - Core dataflow and layer ordering
  - Structural orthogonality constraints
- Phase III/IV/V (ongoing):
  - Numerical runtime implementation
  - Deterministic execution and stability work
  - Controlled layer-by-layer activation, validation, and bounded baseline replacement

## Core Runtime Flow

Per tick:

1. `State -> Tick+1 snapshot`
2. `evaluate_cohesion`
3. `evaluate_target`
4. `evaluate_utility`
5. `integrate_movement` (including spacing projection)
6. `resolve_combat`
7. `State(t+1)`

## Repository Layout

- `runtime/runtime_v0_1.py`
  - Core dataclasses (`BattleState`, `FleetState`, `UnitState`, `PersonalityParameters`)
  - normalization and initialization utilities
- `runtime/engine_skeleton.py`
  - deterministic tick execution and layer implementations
- `test_run/`
  - local scenario runner and run settings
- `archetypes/`
  - runtime archetype data and metatype generation settings
- `analysis/`
  - report standards: `analysis/engineering_reports/_standards/`
  - dated report packs: `analysis/engineering_reports/developments/YYYYMMDD/`
  - exported videos: `analysis/exports/videos/`
- `canonical/`
  - frozen governance/mapping/canonical references (read-only layer)
- `docs/`, `reports/`
  - phase chronicles, freeze declarations, human-readable technical reporting

## Running the Main Analysis Harness

Use the current settings file:

- `test_run/test_run_v1_0.settings.json`

This file is the local layered test-run profile.
Governed experiment baselines should follow phase report settings (for example `analysis/phase_v_default.settings.json`).

Run:

```powershell
.\.venv_check\Scripts\python.exe .\test_run\test_run_v1_0.py
```

## Configuration Notes

- `test_run/test_run_v1_0.settings.json` active runtime structure:
  - `runtime.selectors`
  - `runtime.movement`
  - `runtime.physical`
  - `runtime.observer`
- Recommended demo spacing:
  - `runtime.physical.movement_low_level.min_unit_spacing = 2.0`
- Density stress mode:
  - `runtime.physical.movement_low_level.min_unit_spacing = 1.0`
- Fire quality anisotropy defaults (documented freeze):
  - `runtime.physical.fire_control.fire_quality_alpha = 0.33`
  - `runtime.physical.fire_control.alpha_safe_max = 1.0` (documentation-level current runtime clamp)
- Runtime feature toggles (canonical):
  - `runtime.physical.contact_model.contact_hysteresis_h <= 0` => CH disabled
  - `runtime.physical.contact_model.fsr_strength <= 0` => FSR disabled on legacy/non-`v4a` paths
  - Current active `v4a` path does not consume FSR
- Current maintained runtime cohesion line uses a fixed `v3_test` geometry on the active mainline.
- Current exposed low-level movement knob:
  - `runtime.physical.movement_low_level.alpha_sep`
- Hard-coded movement/projection constant still retained in engine:
  - penetration correction split factor = `0.5`

## Engineering Rules

This repo is operated under strict scoped execution:

- no modification to frozen canonical/mapping/governance layers
- no silent refactor
- deterministic-first validation
- explicit reporting for every governed change

See:

- `AGENTS.md`
- `docs/phase_chronicles/`
- `reports/`
