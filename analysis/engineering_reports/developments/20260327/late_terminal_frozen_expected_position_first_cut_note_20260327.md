# Late Terminal Settle - Frozen Expected-Position Reference First Cut

Date: 2026-03-27
Status: bounded mechanism first cut
Scope: `neutral_transit_v1` only, candidate-active fixture path only

## Scope

This turn implements one bounded late-terminal correction only:

- when the post-step fleet centroid first enters the existing `stop_radius` window,
- freeze the expected-position reference frame,
- and from the next tick onward stop rebuilding expected positions from the moving centroid / moving target axis.

This turn does **not**:

- reopen `E2`
- add a restore taper family
- add parameters or settings
- reopen viewer / realistic / smoothing work
- promote the logic into a generalized terminal framework

## Code surface

- `runtime/engine_skeleton.py`
  - `_build_fixture_expected_position_map(...)` now checks a bounded fixture-local frozen terminal frame and, when present, uses:
    - `frozen_terminal_centroid_xy`
    - `frozen_terminal_primary_axis_xy`
    - optional `frozen_terminal_secondary_axis_xy`
  - otherwise it keeps the prior moving-frame behavior
- `test_run/test_run_execution.py`
  - initializes the bounded fixture-local frozen-frame fields
  - on the first post-step tick where the centroid is confirmed inside `stop_radius`, latches:
    - `frozen_terminal_centroid_xy`
    - `frozen_terminal_primary_axis_xy`
    - `frozen_terminal_secondary_axis_xy`
    - `frozen_terminal_latched_tick`
  - records the same state on fixture telemetry

## Trigger semantics

The latch semantics follow the authorized first cut exactly:

- the already-completed tick is not retroactively rewritten
- the terminal frame is latched after the first post-step in-window confirmation
- the frozen frame is consumed from subsequent ticks onward

## Bounded identity

The implementation is still limited to the existing candidate-active fixture path:

- `active_mode == neutral_transit_v1`
- single-fleet fixture path
- `expected_position_candidate_active == True`

No generalized runtime schema or new restore family was introduced.
