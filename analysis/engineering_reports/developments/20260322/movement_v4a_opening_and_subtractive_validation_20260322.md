# Movement v4a Opening and Subtractive Validation (2026-03-22)

Status: Limited Authorization  
Scope: bounded opening of `movement_v4a` as a subtractive neutral candidate; implementation plus very bounded paired neutral validation

## 1. Purpose

`v4a` is opened as a subtractive experimental movement line.

Its current purpose is not to produce a finished new baseline.
Its purpose is to remove a small set of already-exposed non-neutral shaping mechanisms from the current shared path and observe what becomes cleaner, what remains problematic, and what should be deferred to a later rebuild stage.

## 2. Why v4a Is Subtractive First

The current neutral-transit evidence already showed that the old shared path contains several shaping mechanisms that are difficult to read as neutral substrate:

- MB low-level movement reshaping
- ODW low-level posture redistribution
- stray-dependent attract
- broad correction-family involvement

Governance therefore authorized subtraction before rebuild.
`v4a` is the narrow implementation of that order.

## 3. Exact Removed Items

`v4a` removes or disables the following runtime behaviors:

1. MB movement-layer injection
   In `runtime/engine_skeleton.py`, `v4a` zeros the low-level `mb` reshaping effect before the parallel/tangent redistribution branch.

2. ODW movement-layer injection
   In `runtime/engine_skeleton.py`, `v4a` disables the `odw_posture_bias_active` branch so center/wing parallel redistribution no longer modifies maneuver composition.

3. stray-dependent attract
   In `runtime/engine_skeleton.py`, `v4a` suppresses the attract branch by forcing `attract_x = attract_y = 0.0` and clearing the stray-driven shaping contribution.

4. FSR in neutral validation path
   In `test_run/test_run_execution.py`, `v4a` disables `fsr_surface["enabled"]` when the active path is neutral-transit fixture validation.

## 4. Exact Untouched Items

`v4a` deliberately leaves the following items unchanged:

- direct cohesion remains centroid-restoration based
- no reference-formation generator is introduced
- FR canonical interface/meaning is not rewritten
- `exp_precontact_centroid_probe` remains available
- `centroid_probe_scale` remains reused unchanged
- target substrate plumbing remains unchanged
- separation, boundary, combat, and observer surfaces are not redesigned
- baseline `v3a` remains the maintained baseline; `v4a` is not a replacement path

## 5. Settings Surface and Minimality Notes

Settings changes were kept narrow:

- `runtime.selectors.movement_model` now accepts `baseline | v3a | v4a`
- `baseline` still resolves to `v3a`
- current layered `testonly` settings now set `movement_model = v4a`, so `test_mode=2` uses `v4a` as the current explicit experimental default
- the old `runtime.movement.v3a.test_only` subtree was moved out of `test_run_v1_0.runtime.settings.json` into `test_run_v1_0.testonly.settings.json`

This move did **not** require a new loader path.
Existing layered settings merge already supports the same `runtime.*` tree being overlaid from the test-only file.

## 6. Validation Setup

Validation was deliberately bounded:

1. `python -m py_compile runtime/engine_skeleton.py test_run/test_run_scenario.py test_run/test_run_execution.py test_run/settings_accessor.py test_run/test_run_entry.py`
2. `python test_run/test_run_anchor_regression.py`
3. one paired neutral-transit comparison on the current layered fixture geometry and seeds:
   - case A: `movement_model = v3a`
   - case B: `movement_model = v4a`

Important note:

- the existing `neutral_transit_v1` scenario path already hard-disabled `FSR` in fixture runtime config before this turn
- therefore the visible paired delta in this validation should be read mainly as MB / ODW / stray subtraction
- the `v4a` FSR gate is still correct for consistency, but it was not the differential driver in this paired fixture check

## 7. Neutral Transit Observations

Paired result on the current long-diagonal fixture:

| movement | arrival_tick | final_tick | final_rms_radius_ratio | mean_corrected_unit_ratio | peak_projection_pairs | peak_projection_mean_disp | peak_projection_max_disp |
|---|---:|---:|---:|---:|---:|---:|---:|
| v3a | 445 | 455 | 0.684 | 0.899 | 147 | 0.285 | 0.863 |
| v4a | 451 | 461 | 1.017 | 0.774 | 119 | 0.354 | 0.944 |

Additional distance reading:

- `v3a` final centroid-to-objective distance: `0.817`
- `v4a` final centroid-to-objective distance: `0.233`

## 8. Comparison with Current Path

### 8.1 What became cleaner

- projection breadth went down:
  `mean_corrected_unit_ratio` fell from `0.899` to `0.774`
- pair burden went down:
  `peak_projection_pairs_count` fell from `147` to `119`
- final geometry stopped collapsing inward:
  `final_rms_radius_ratio` moved from `0.684` to `1.017`

This is the clearest current `v4a` success signal.
The de-shaped path is less compacted and less broadly projection-driven.

### 8.2 What did not improve automatically

- arrival became slightly slower:
  `445 -> 451`
- peak projection displacement intensity rose:
  `0.863 -> 0.944`
- peak mean displacement also rose:
  `0.285 -> 0.354`

So subtraction reduced projection breadth but did **not** automatically make all local correction intensity smaller.

### 8.3 Current engineering reading

This is a useful result.
It means the removed shaping family was masking at least two different things:

- broad compaction / burden spread
- remaining local correction intensity from the surviving substrate

That is exactly the kind of clarification `v4a` was meant to produce.

## 9. Explicit Non-Authorizations

This turn did **not** do any of the following:

- no reference-formation implementation
- no new FR mechanism
- no broad movement-core rewrite
- no 3D implementation
- no silent baseline replacement
- no re-insertion of MB / ODW into a different low-level branch

## 10. Recommendation on v4b

Recommendation:

- open `v4b` review, not broad implementation

Reason:

- `v4a` succeeded at its bounded job
- it reduced compaction and projection breadth enough to make the remaining problem cleaner
- it also showed that subtraction alone does not solve local correction intensity

So the next sensible question is no longer whether subtraction helped.
It did.
The next question is which minimal formation-aware rebuild move should be reviewed first under a separate `v4b` authorization.

## 11. Bottom Line

`v4a` is worth keeping open as an experimental container.
It is not ready to replace `v3a`, but it already succeeded as a subtractive neutral-validation line:

- less broad projection burden
- less end-state compaction
- clearer remaining core issues

That is enough to justify a later bounded `v4b` review request without implying any baseline replacement.
