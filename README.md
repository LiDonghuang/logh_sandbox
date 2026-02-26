# Fleet Sandbox

Fleet Sandbox is a strategic fleet-combat simulation sandbox focused on deterministic runtime behavior, parameterized strategic archetypes, and controlled governance-driven engineering evolution.

This repository is the engineering workspace for the Python runtime line (Phase III onward), with frozen conceptual/governance artifacts retained as canonical references.

## Project Status

- Current milestone: `v5.0-alpha1` (Contact Hysteresis alpha, engineering execution)
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
- Phase III/IV/ongoing:
  - Numerical runtime implementation
  - Deterministic execution and stability work
  - Controlled layer-by-layer activation and validation

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

- `runtime_v0_1.py`
  - Core dataclasses (`BattleState`, `FleetState`, `UnitState`, `PersonalityParameters`)
  - normalization and initialization utilities
- `runtime/engine_skeleton.py`
  - deterministic tick execution and layer implementations
- `runtime/engine_driver_dummy.py`
  - controlled run harness
- `analysis/`
  - scenario runner, settings, archetype data, visual analysis scripts
- `canonical/`
  - frozen governance/mapping/canonical references (read-only layer)
- `docs/`, `reports/`
  - phase chronicles, freeze declarations, human-readable technical reporting

## Running the Main Analysis Harness

Use the current settings file:

- `analysis/test_run_v1_0.settings.json`

Run:

```powershell
.\.venv_check\Scripts\python.exe .\analysis\test_run_v1_0.py
```

## Configuration Notes

- Recommended demo spacing:
  - `min_unit_spacing = 2.0`
- Density stress mode:
  - `min_unit_spacing = 1.0`
- Fire quality anisotropy defaults (documented freeze):
  - `fire_quality_alpha = 0.1`
  - `alpha_safe_max = 0.15` (documentation-level bound)

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
