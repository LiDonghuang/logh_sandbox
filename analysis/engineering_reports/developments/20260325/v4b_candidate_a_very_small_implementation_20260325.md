# v4b Candidate A - Very Small Implementation Memo (2026-03-25)

Status: Limited Authorization  
Scope: fixture-only minimal implementation for expected-position restoration in `neutral_transit_v1`

## 1. Purpose

This turn implements one bounded change only:

in the `neutral_transit_v1` fixture path, replace centroid-directed restoration input with deterministic expected-position-directed restoration input.

It does **not** open:

- battle-path activation
- generalized reference-formation framework
- legality / projection redesign
- baseline replacement

## 2. Exact Implementation Boundary

Active only when all of the following are true:

- fixture mode is `neutral_transit_v1`
- the path is single-fleet and no-enemy
- movement model is current `v4a`
- the fixture path has a deterministic fixed-order initial geometry to anchor against

The implementation does **not** modify runtime dataclass structures.

## 3. Modified Files

### `runtime/engine_skeleton.py`

Added one bounded helper and one bounded replacement point:

- fixture-only expected-position reconstruction helper at `runtime/engine_skeleton.py:225`
- restoration-object replacement at `runtime/engine_skeleton.py:1028` and `runtime/engine_skeleton.py:1053`

Behavior:

- when the fixture-only gate is active, `cohesion_vector` is derived from `expected_position - unit.position`
- otherwise the existing centroid-directed behavior remains unchanged

No legality/projection code was changed.

### `test_run/test_run_execution.py`

Added fixture-only preparation and diagnostics:

- deterministic initial expected-slot offsets at `test_run/test_run_execution.py:1317`
- fixture-only gate wiring into `engine.TEST_RUN_FIXTURE_CFG` at `test_run/test_run_execution.py:1429`
- diagnostics keys added under `observer_telemetry["fixture"]` at `test_run/test_run_execution.py:1445`
- per-tick diagnostic collection at `test_run/test_run_execution.py:1600`

## 4. Deterministic Mapping Rule

The mapping rule is:

- fixed initial unit order
- no reflow
- no slot reassignment

Expected positions are reconstructed from:

- initial local offsets in an objective-facing 2D frame
- current centroid anchor
- current objective-facing primary axis
- explicit degeneracy fallback to the initial primary axis only when the current axis collapses numerically

## 5. FR Usage Reading In This Turn

In this fixture-only path, `FR` now acts as restore-to-reference gain because the restoration direction itself is no longer centroid-directed.

This is a bounded usage mapping only.
It is **not** a canonical FR rewrite and it does not change battle-wide semantics.

## 6. New Test-Only Diagnostics

New fixture-only keys:

- `expected_position_rms_error`
- `front_extent_ratio`
- `expected_position_candidate_active`

Existing reused keys:

- `corrected_unit_ratio`
- `projection_pairs_count`
- `projection_mean_displacement`
- `projection_max_displacement`
- `formation_rms_radius_ratio`

Meaning:

- `expected_position_rms_error`: RMS distance from current positions to expected reference positions
- `front_extent_ratio`: front-most extent along the objective-facing axis, normalized by the initial front extent

## 7. Explicit Non-Changes

This turn did **not** change:

- battle path
- TL logic
- projection / legality algorithm
- same-fleet min-spacing surface
- MB / ODW / stray / FSR family
- slot reassignment / reflow
- 3D runtime-facing parameters

## 8. Validation Scope

Validation remained bounded to:

- `py_compile`
- 3-run anchor regression
- paired neutral-transit checks

Paired cases:

- `P0_super_long`: `arena=400`, `origin=[50,50]`, `objective=[350,350]`
- `P1_long_diag`: `arena=400`, `origin=[50,50]`, `objective=[150,150]`

The second case is an explicit bounded assumption used to satisfy the requested long-diagonal comparison.

## 9. Bottom Line

This is a true fixture-only restoration-object replacement.

It keeps the rest of the stack still:

- same objective trend
- same separation
- same legality / projection
- same battle path

Only the restoration object was swapped from centroid to expected position.
