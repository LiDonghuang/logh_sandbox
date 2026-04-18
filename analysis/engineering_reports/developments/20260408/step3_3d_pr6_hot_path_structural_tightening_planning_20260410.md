# step3_3d_pr6_hot_path_structural_tightening_planning_20260410

## Scope

- planning carrier only
- no mechanism rewrite in this turn
- no compute optimization in this turn

## Why this is the next line

The subtraction-first cleanup phase has now reached a natural stage boundary:

- old-family mainline surfaces have been heavily reduced
- active owners are materially clearer
- viewer-facing fleet-body summary Phase 1 has been established
- active old-named cohesion seam has been rerooted

The next line should therefore be:

- continued structure tightening

not:

- further broad deletion
- compute optimization
- mechanism redesign

## Hot-path audit summary

### Runtime hot path

- [engine_skeleton.py](e:/logh_sandbox/runtime/engine_skeleton.py)
  - `integrate_movement()`
    - lines `668-1348`
    - length `681`
  - `resolve_combat()`
    - lines `1350-1724`
    - length `375`

### Harness hot path

- [test_run_execution.py](e:/logh_sandbox/test_run/test_run_execution.py)
  - `run_simulation()`
    - lines `2177-3642`
    - length `1466`
  - `_resolve_v4a_reference_surface()`
    - lines `448-793`
    - length `346`
  - `_evaluate_target_with_pre_tl_substrate()`
    - lines `874-1282`
    - length `409`
  - `integrate_movement()`
    - lines `1327-1680`
    - length `354`

## Current function-role read

### `engine_skeleton.py::integrate_movement()`

Current responsibilities are mixed:

1. runtime preflight / gate setup
2. fixture terminal gate preparation
3. per-fleet separation and restore-vector realization
4. per-unit step composition
5. global post-move projection
6. hard boundary clamp
7. diagnostics-only fleet-radius stats
8. diagnostics-only pending-payload assembly

This is too many responsibilities for one maintained hot-path function.

### `engine_skeleton.py::resolve_combat()`

Current responsibilities:

1. contact thresholds and fire-quality setup
2. snapshot target assignment
3. contact hysteresis resolution
4. damage application
5. orientation override
6. diag4 contact-history enrichment
7. fleet pruning

Large, but still more tightly mechanism-coupled than `integrate_movement()`.
It should not be the first structural-tightening slice.

### `test_run_execution.py::run_simulation()`

Current responsibilities:

1. config extraction / validation
2. engine surface wiring
3. helper definition
4. fixture bundle setup
5. main tick loop
6. fixture-only branch
7. battle observer aggregation
8. end-of-run normalization

This is the largest maintained orchestrator in the repo. It should be split,
but only after the first runtime hot-path slice proves the tightening method.

### `_resolve_v4a_reference_surface()` and `_evaluate_target_with_pre_tl_substrate()`

These are also large, but they are still mechanism-owner-heavy. They are better
treated after the first structural-tightening slice, not before.

## Recommended first bounded refactor

### Slice A: `engine_skeleton.py::integrate_movement()` diagnostic-only extraction

This is the lowest-risk first slice because it removes non-movement ownership
from the runtime hot path without changing movement semantics.

Target blocks to move out:

1. fleet-radius diagnostics block
   - current lines around `1125-1181`
   - now passive only after FSR actuator retirement

2. pending movement diagnostic payload flush
   - current lines around `1304-1344`
   - diagnostics-only responsibility

The first slice should **not** yet extract:

- per-unit movement composition
- projection math
- fixture terminal gate semantics

Why:

- those still directly define movement behavior
- extracting them first risks parameter-shuttling wrappers

### Acceptance criteria for Slice A

- `integrate_movement()` becomes visibly shorter
- no movement formula changes
- no new fallback
- no helper whose main purpose is just parameter transfer
- diagnostics behavior remains unchanged

## Recommended second bounded refactor

### Slice B: `test_run_execution.py::run_simulation()` preflight and engine-wiring tightening

After Slice A succeeds, the next best target is the non-loop portion of
`run_simulation()`:

1. execution/runtime/observer config validation
2. engine surface wiring
3. fixture activation normalization

This should shrink the orchestrator before touching the main tick loop.

### Acceptance criteria for Slice B

- `run_simulation()` caller body becomes shorter before the tick loop
- engine surface ownership becomes easier to inspect
- no behavior change

## Deferred for later slices

- `resolve_combat()`
- `_evaluate_target_with_pre_tl_substrate()`
- `_resolve_v4a_reference_surface()`
- compute optimization

These remain important, but they are not the right first tightening slice.

## Planning conclusion

The next implementation slice should be:

1. `engine_skeleton.py::integrate_movement()` diagnostic-only extraction

If that succeeds cleanly, follow with:

2. `test_run_execution.py::run_simulation()` preflight / engine-wiring tightening
