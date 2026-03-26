# Step 3 3D Objective First Implementation Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: bounded neutral-transit fixture path only
Affected Parameters: `execution_cfg['fixture']` carrier shape for `neutral_transit_v1`
New Variables Introduced: `execution_cfg['fixture']['objective_contract_3d']`
Cross-Dimension Coupling: 3D contract carrier derives `anchor_point_xyz=(x, y, 0.0)` from the existing bounded fixture objective input
Mapping Impact: runtime-facing contract carrier added without widening runtime schema
Governance Impact: executes the first very small implementation authorized for Step 3
Backward Compatible: yes; 2D maintained battle path remains untouched

Summary
- The first bounded carrier is now implemented at `execution_cfg['fixture']['objective_contract_3d']`.
- The carrier exists only on the existing `neutral_transit_v1` fixture path.
- `anchor_point_xyz` is currently derived from the existing fixture `objective_point_xy` as `(x, y, 0.0)`.
- `source_owner`, `objective_mode`, and `no_enemy_semantics` are explicitly wired as `fixture`, `point_anchor`, and `enemy_term_zero`.
- First consumption remains narrow: runtime-facing consumption uses projected `xy` only.
- No new 3D settings surface was introduced.
- No viewer ownership, movement substrate, formation package, legality package, or runtime-schema widening was introduced.

## Scope

This implementation touches only:

- `test_run/test_run_scenario.py`
- `test_run/test_run_execution.py`
- `test_run/test_run_entry.py`

It does not touch:

- `runtime/runtime_v0_1.py`
- `runtime/engine_skeleton.py`
- `viz3d_panda/*`

## What Was Implemented

### 1. Fixture carrier creation

`prepare_neutral_transit_fixture(...)` now creates:

```python
execution_cfg["fixture"]["objective_contract_3d"] = {
    "anchor_point_xyz": (objective_x, objective_y, 0.0),
    "source_owner": "fixture",
    "objective_mode": "point_anchor",
    "no_enemy_semantics": "enemy_term_zero",
}
```

This is derived from the existing bounded fixture input and does not require a new settings subtree.

### 2. Fixture validation and bounded mirror

`run_simulation(...)` now:

- requires the `objective_contract_3d` mapping for `neutral_transit_v1`
- validates `anchor_point_xyz`
- validates `source_owner = fixture`
- validates `objective_mode = point_anchor`
- validates `no_enemy_semantics = enemy_term_zero`
- rejects `transit_axis_hint_xyz` in the first implementation
- mirrors the normalized carrier into `engine.TEST_RUN_FIXTURE_CFG`

### 3. First consumption rule

`TestModeEngineTickSkeleton._evaluate_target_with_fixture_objective(...)` now consumes:

- projected `xy` taken from `objective_contract_3d.anchor_point_xyz`

This keeps the first implementation:

- 3D contract-aware
- XY-consumed
- still bounded to the existing neutral-transit carrier

## Hard Boundary Check

The implementation remains:

- single-fleet only
- no-enemy only
- no-combat
- no-firing
- no-TL runtime activation
- no-penetration redesign
- no-formation-mechanics expansion
- no-legality redesign
- single point anchor only

## Explicit Non-Changes

This turn does not:

- open `transit_axis_hint_xyz`
- add a new replay protocol
- require the viewer to prove the contract exists
- widen canonical runtime schema
- redefine 2D maintained baseline semantics
