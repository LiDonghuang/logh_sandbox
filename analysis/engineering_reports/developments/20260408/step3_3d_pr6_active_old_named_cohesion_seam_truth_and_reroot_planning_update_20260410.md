# step3_3d_pr6_active_old_named_cohesion_seam_truth_and_reroot_planning_update_20260410

## Scope

- planning carrier only
- no math rewrite
- no telemetry redesign
- no implementation in this turn

## Why this update exists

After:

- `test_mode` retirement
- fleet-body-summary Phase 1 cutover
- FSR actuator retirement
- `v4a` candidate parameter-surface structuring

the remaining old-name cohesion seam is now narrow enough to plan as a bounded
reroot rather than a broad cleanup cluster.

The prior planning note identified the seam. This update tightens the truth map
and records the concrete implementation boundary for the next slice.

## Current truthful seam

### Runtime geometry owner

- [engine_skeleton.py](e:/logh_sandbox/runtime/engine_skeleton.py)
  - `EngineTickSkeleton._compute_cohesion_v3_geometry(self, state, fleet_id)`

Current maintained math is fixed, not selectable:

- `alive_positions`, `centroid_x`, `centroid_y`
- `r`
  - RMS fleet radius around centroid
- `r_ref`
  - `separation_radius * sqrt(n_alive)`
- `rho = r / r_ref`
- `c_scale`
  - bounded size penalty with:
    - `rho_low = 0.35`
    - `rho_high = 1.15`
    - `penalty_k = 6.0`
- `c_conn`
  - largest-connected-component ratio using
    - `connect_radius = 1.1 * separation_radius`
- final score
  - `c_v3 = clamp01(c_conn * c_scale)`

There is no longer a maintained public selector for alternative cohesion
families. This function now computes the single maintained runtime cohesion
score on the current mainline.

### Runtime state carrier

- [runtime_v0_1.py](e:/logh_sandbox/runtime/runtime_v0_1.py)
  - `BattleState.last_fleet_cohesion`

### Maintained writers

- [engine_skeleton.py](e:/logh_sandbox/runtime/engine_skeleton.py)
  - `evaluate_cohesion()`
  - writes `replace(state, last_fleet_cohesion=runtime_cohesion)`

### Maintained readers

- [test_run_scenario.py](e:/logh_sandbox/test_run/test_run_scenario.py)
  - initial state construction still seeds `last_fleet_cohesion`
    via `build_initial_cohesion_map(...)`
- [test_run_execution.py](e:/logh_sandbox/test_run/test_run_execution.py)
  - trajectory export still appends:
    - `state.last_fleet_cohesion.get(fleet_id, 1.0)`

### No longer active on maintained mainline

- `runtime.selectors.cohesion_decision_source`
- `collapse_signal.v3_*`
- observer surfaces for:
  - `cohesion_v3`
  - `c_conn`
  - `rho`
  - `c_scale`

So the remaining problem is naming / state-carrier truth, not selector or
observer cleanup.

## Planning conclusion

The next bounded implementation slice should reroot the seam honestly without
changing the math:

### Rename targets

- runtime geometry owner
  - `_compute_cohesion_v3_geometry()`
  - -> `_compute_fleet_cohesion_score_geometry()`

- runtime state carrier
  - `last_fleet_cohesion`
  - -> `last_fleet_cohesion_score`

### Why these names

- `fleet`
  - makes the seam about the current fleet body, not a historical version line
- `cohesion_score`
  - matches current truth: this is a scalar runtime cohesion score, not a
    selector-owned family id
- `geometry`
  - keeps the function name honest about what it computes

## Explicit non-goals for the next implementation slice

- do not rename internal diagnostic terms yet:
  - `c_conn`
  - `rho`
  - `c_scale`
  - `c_v3`
- do not merge this seam into fleet-body-summary
- do not change the score formula
- do not reopen personality coupling
- do not add compatibility aliases unless a real maintained reader requires one

## Recommended implementation boundary

Touch only:

- [engine_skeleton.py](e:/logh_sandbox/runtime/engine_skeleton.py)
- [runtime_v0_1.py](e:/logh_sandbox/runtime/runtime_v0_1.py)
- [test_run_scenario.py](e:/logh_sandbox/test_run/test_run_scenario.py)
- [test_run_execution.py](e:/logh_sandbox/test_run/test_run_execution.py)

If comments / settings truth mention the old-name seam in active surfaces,
update them in the same slice. Do not widen beyond that.

## Acceptance criteria for the next slice

- maintained math is unchanged
- maintained state flow is unchanged
- old-name `v3` carrier wording is gone from the active seam
- no new compatibility wrapper or duplicate alias is introduced
- battle / neutral behavior is unaffected
