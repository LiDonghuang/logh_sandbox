# Step 3 3D Objective Implementation-Bounded Structural Draft (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: Step 3 implementation-planning draft only
Affected Parameters: none
New Variables Introduced: none in code; draft-only carrier proposal `execution_cfg['fixture']['objective_contract_3d']`
Cross-Dimension Coupling: bounded neutral-transit fixture may derive a 3D anchor from existing 2D fixture objective input
Mapping Impact: planning only; no runtime/viewer mapping changed
Governance Impact: defines the smallest plausible first implementation surface without authorizing code
Backward Compatible: yes

Summary
- The first implementation carrier should stay on the existing bounded fixture path, not on viewer or canonical runtime schema.
- The recommended first carrier is a small `objective_contract_3d` mapping under `execution_cfg['fixture']`.
- `anchor_point_xyz` should initially be derived from the existing fixture `objective_point_xy` as `(x, y, 0.0)`.
- `source_owner`, `objective_mode`, and `no_enemy_semantics` should be fixed to `fixture`, `point_anchor`, and `enemy_term_zero`.
- `transit_axis_hint_xyz` should remain omitted in the first implementation.
- First implementation should keep neutral transit single-fleet / no-enemy / point-anchor-only.
- The first runtime consumption path should remain the existing fixture target-direction hook, not a new 3D movement substrate.
- Replay transfer and viewer readout are optional later, not required for first implementation.

## 1. Scope

This document plans the smallest possible first implementation surface for `ObjectiveLocationSpec v0.1 (3D Draft)`.

It does not authorize:

- runtime code changes
- 3D movement implementation
- 3D formation implementation
- 3D combat / targeting expansion
- 3D legality / projection expansion

## 2. First Carrier Placement

The first bounded implementation should not start by changing:

- `runtime/runtime_v0_1.py`
- `BattleState`
- `FleetState`
- `viz3d_panda/`

The smallest plausible first carrier is:

- `execution_cfg['fixture']['objective_contract_3d']`

Reason:

- the first carrier is already explicitly bounded to `neutral_transit_v1`
- the fixture path is already single-fleet and no-enemy
- this avoids creating a new parallel settings surface
- this avoids pretending the viewer owns semantics
- this avoids widening canonical runtime schema before the contract is validated

## 3. Proposed First-Carrier Shape

Recommended first mapping shape:

```python
execution_cfg["fixture"]["objective_contract_3d"] = {
    "anchor_point_xyz": (objective_x, objective_y, 0.0),
    "source_owner": "fixture",
    "objective_mode": "point_anchor",
    "no_enemy_semantics": "enemy_term_zero",
}
```

First-implementation rule for `transit_axis_hint_xyz`:

- do not wire it in the first implementation
- keep it absent rather than present-but-semantic

This keeps the first carrier narrow and avoids silent growth into frame semantics.

## 4. Why `anchor_point_xyz` Should Be Derived First

The current bounded fixture already owns:

- `fixture.neutral_transit_v1.objective_point_xy`

For the first implementation-planning turn, the recommended derivation is:

- `anchor_point_xyz = (objective_point_xy[0], objective_point_xy[1], 0.0)`

Reason:

- no new 3D settings file or settings subtree is needed
- inheritance-first / duplication-last stays intact
- the first carrier remains compatible with the current neutral-transit identity
- the contract can be exercised without opening vertical movement or frame construction

This is a first-carrier derivation only, not a claim that final 3D objectives are confined to `z = 0.0`.

## 5. Minimum Wiring by Layer

### Runtime-facing fixture carrier

Smallest likely touched locations:

- `test_run/test_run_scenario.py`
  - derive `objective_contract_3d` during `prepare_neutral_transit_fixture(...)`
- `test_run/test_run_execution.py`
  - validate the fixture-side mapping inside `run_simulation(...)`
  - mirror the mapping into `engine.TEST_RUN_FIXTURE_CFG`
- `test_run/test_run_execution.py`
  - keep `_evaluate_target_with_fixture_objective(...)` as the first consumption hook

### How first consumption should stay bounded

For the first implementation only:

- consume `anchor_point_xyz` by projecting to current XY target-direction preparation
- do not create a 3D movement substrate
- do not create a 3D frame or legality package

This means the first implementation is still structurally 3D-contract-aware, while behavior remains bounded to the existing neutral-transit carrier.

## 6. Field-by-Field First Wiring

### `anchor_point_xyz`

- first landing point: `execution_cfg['fixture']['objective_contract_3d']['anchor_point_xyz']`
- first consumption: fixture target-direction preparation in execution host
- first implementation should project to `xy` only for neutral-transit consumption

### `source_owner`

- first landing point: same fixture contract mapping
- fixed first reading: `fixture`
- should be echoed into fixture telemetry/readout for validation

### `objective_mode`

- first landing point: same fixture contract mapping
- fixed first reading: `point_anchor`
- no other modes should be admitted in first implementation

### `no_enemy_semantics`

- first landing point: same fixture contract mapping
- fixed first reading: `enemy_term_zero`
- should be validated, not inferred

### `transit_axis_hint_xyz`

- first implementation status: omitted
- later status: optional only after a separate governance opening

## 7. Touch / No-Touch Boundary

Should be touched in the first implementation, if later authorized:

- fixture preparation in `test_run/test_run_scenario.py`
- fixture execution validation in `test_run/test_run_execution.py`
- fixture telemetry echo/readout in `test_run/test_run_execution.py`

Should remain untouched in the first implementation:

- `runtime/runtime_v0_1.py`
- `runtime/engine_skeleton.py`
- `viz3d_panda/app.py`
- `viz3d_panda/replay_source.py`
- `viz3d_panda/scene_builder.py`
- `viz3d_panda/unit_renderer.py`
- layered visualization settings surfaces
- 2D maintained battle path behavior

## 8. How the First Carrier Stays Hard-Bounded

The first implementation must preserve:

- single-fleet only
- no-enemy only
- no-combat
- no-firing
- no-TL runtime activation
- no-penetration redesign
- no-formation-mechanics expansion
- no-legality redesign
- single point anchor only

That means the first implementation must not:

- admit moving objective carriers
- admit waypoint lists
- admit pursuit / retreat switching
- admit viewer-owned fallback semantics

## 9. Recommended Minimal Outcome

If a later code turn is authorized, the smallest acceptable first result is:

- fixture prepares a 3D objective contract mapping
- execution validates it
- neutral-transit target-direction preparation consumes its projected `xy` anchor
- telemetry echoes the contract fields for validation

Nothing more is required for the first implementation turn.
