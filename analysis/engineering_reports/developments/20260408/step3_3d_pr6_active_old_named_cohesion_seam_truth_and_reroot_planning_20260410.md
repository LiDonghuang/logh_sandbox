# step3_3d_pr6_active_old_named_cohesion_seam_truth_and_reroot_planning_20260410

## Scope

- baseline/runtime: planning carrier only
- test-only or harness-only: cross-layer planning
- protocol or policy only: no

## Why this is the next gate

The maintained mainline now has:

- `v4a` movement baseline
- retired public cohesion selector surface
- a single fixed maintained cohesion geometry

But the active seam still carries old names:

- `_compute_cohesion_v3_geometry()`
- `last_fleet_cohesion`

This is now primarily an ownership-truth and reroot problem, not a settings
cleanup problem.

## Current active owner

### Runtime geometry owner

- `runtime/engine_skeleton.py`
  - `_compute_cohesion_v3_geometry(self, state, fleet_id) -> tuple[float, dict]`

Current internal math:

- `c_conn`
  - largest-connected-component ratio under `connect_radius = 1.1 * separation_radius`
- `r`
  - fleet RMS radius around centroid
- `r_ref`
  - `separation_radius * sqrt(n_alive)`
- `rho = r / r_ref`
- `c_scale`
  - bounded size penalty using `rho_low=0.35`, `rho_high=1.15`, `penalty_k=6.0`
- final:
  - `c_v3 = clamp01(c_conn * c_scale)`

### Runtime state seam

- `runtime/runtime_v0_1.py`
  - `BattleState.last_fleet_cohesion`

### Downstream maintained readers

- `runtime/engine_skeleton.py`
  - `evaluate_cohesion()` writes `last_fleet_cohesion`
- `test_run/test_run_execution.py`
  - trajectory/observer export still reads `state.last_fleet_cohesion`

## Truthful current read

- The old public selector surface is already retired.
- The old-name seam is still active.
- The geometry is no longer a selectable family; it is the single maintained
  cohesion geometry on the current mainline.

So the remaining problem is naming / owner truth:

- old-name internals still imply a family-selection era that no longer exists

## Recommended sequence

1. do not change the math yet
2. first reroot names and state seams honestly
3. only after reroot, consider deeper structural unification with any future
   fleet-body summary / diagnostics line

## Likely reroot targets

### Rename candidates

- `_compute_cohesion_v3_geometry()`
  -> candidate:
  - `_compute_fleet_cohesion_geometry()`

- `last_fleet_cohesion`
  -> candidate:
  - `last_fleet_cohesion_score`
  - or `last_runtime_cohesion`

The exact new names should be chosen in implementation, but they should stop
pretending this is a live `v3` family toggle.

## Not part of this planning turn

- no math rewrite
- no telemetry redesign
- no fleet-body summary phase-2 merge
- no personality-parameter reopening

