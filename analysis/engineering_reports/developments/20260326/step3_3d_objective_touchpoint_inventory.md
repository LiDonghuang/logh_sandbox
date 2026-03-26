# Step 3 3D Objective Touchpoint Inventory (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: Step 3 implementation-planning inventory only
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: inventory only; identifies bounded fixture-to-runtime/view paths
Mapping Impact: planning only
Governance Impact: separates required / optional / forbidden touchpoints before any implementation turn
Backward Compatible: yes

Summary
- Required first-implementation touchpoints are confined to the neutral-transit fixture prep and execution path.
- Replay transfer is optional later, not required for the first implementation.
- Viewer readout is optional later and must remain consumer-only.
- Canonical runtime schema and engine core are forbidden for the first implementation.

## 1. Required for First Implementation

| Layer | Path / Touchpoint | Why Required | Category |
| --- | --- | --- | --- |
| test harness / fixture prep | `test_run/test_run_scenario.py::prepare_neutral_transit_fixture(...)` | first bounded carrier must be assembled here without creating a new settings stack | required |
| execution validation | `test_run/test_run_execution.py::run_simulation(...)` fixture validation block | first carrier fields must be validated and normalized here before runtime consumption | required |
| execution handoff | `engine.TEST_RUN_FIXTURE_CFG` population inside `test_run/test_run_execution.py` | existing bounded fixture handoff already exists here; smallest place to mirror the contract | required |
| first consumption | `test_run/test_run_execution.py::TestModeEngineTickSkeleton._evaluate_target_with_fixture_objective(...)` | first carrier needs one bounded runtime-facing consumer | required |
| validation readout | `observer_telemetry['fixture']` assembly in `test_run/test_run_execution.py` | first implementation needs contract echo/readout without involving the viewer | required |
| fixture launcher summary | `test_run/test_run_entry.py::_run_neutral_transit_fixture(...)` | first validation needs a small human-readable summary surface | required |

## 2. Optional Later

| Layer | Path / Touchpoint | Why Optional Later | Category |
| --- | --- | --- | --- |
| replay transfer | `test_run/test_run_entry.run_active_surface(...)` returned bundle | can carry already-owned objective results later, but first implementation can validate without replay changes | optional later |
| replay normalization | `viz3d_panda/replay_source.py::build_replay_bundle(...)` metadata | can pass through objective snapshots later if viewer marker/readout is separately authorized | optional later |
| viewer readout | `viz3d_panda/app.py` overlay text | may display objective mode/source later, but should not be required for first implementation | optional later |
| viewer marker | `viz3d_panda/scene_builder.py` or a future viewer-local marker helper | may render an objective marker later, but only as replay consumption | optional later |
| `transit_axis_hint_xyz` | fixture contract mapping | can remain reserved for later; first implementation does not need it | optional later |

## 3. Forbidden in First Implementation

| Layer | Path / Touchpoint | Why Forbidden | Category |
| --- | --- | --- | --- |
| canonical runtime schema | `runtime/runtime_v0_1.py` | first carrier does not justify widening `BattleState` / `FleetState` / schema types yet | forbidden |
| engine core | `runtime/engine_skeleton.py` | first implementation must not become a broad runtime rewrite | forbidden |
| 3D viewer ownership | `viz3d_panda/*` as objective owner | viewer consumes only; it must not define objective meaning or fallback rules | forbidden |
| new settings surface | new `3d` settings subtree or mirrored config stack | violates inheritance-first / duplication-last | forbidden |
| formation package | any new frame / spacing / extents fields | objective must remain “where to go” only | forbidden |
| legality package | feasibility / legality / collision semantics | outside the first carrier boundary | forbidden |
| combat package | target preference / fire-control / doctrine additions | outside the first carrier boundary | forbidden |

## 4. Recommended First Carrier Data Path

Smallest recommended path:

1. existing fixture settings provide `objective_point_xy`
2. `prepare_neutral_transit_fixture(...)` derives `anchor_point_xyz = (x, y, 0.0)`
3. derived fields are placed into `execution_cfg['fixture']['objective_contract_3d']`
4. `run_simulation(...)` validates the contract and mirrors it into `TEST_RUN_FIXTURE_CFG`
5. `_evaluate_target_with_fixture_objective(...)` consumes projected `xy` only
6. `observer_telemetry['fixture']` echoes the contract for validation

## 5. Why Replay and Viewer Are Not Required First

The first implementation can be judged with:

- fixture telemetry
- launcher summary
- bounded neutral-transit run behavior

Because of that, the first implementation does not need:

- a new replay protocol
- a viewer marker
- a viewer overlay field

Those can remain optional until a later governance turn explicitly opens viewer readout of objective results.

## 6. `transit_axis_hint_xyz` Placement Decision

For the first implementation:

- do not consume it
- do not invent it from viewer or formation logic
- do not store a fake placeholder value just to fill the schema

If it appears in the first implementation, it is more likely to invite frame growth than to help validate the contract.
