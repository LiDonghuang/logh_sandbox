# Late Terminal Settle - Orientation Freeze / Live-Centroid Split Cut

Date: 2026-03-27
Scope: bounded `neutral_transit_v1` late-terminal correction only

## Scope

This turn replaces the prior whole-frame frozen expected-position reference on the bounded candidate-active fixture path with a narrower split cut:

- freeze terminal reference orientation
- keep expected-position center on the live centroid
- keep the existing restore deadband
- keep the existing late-only centroid non-overshoot clamp

The change remains bounded to the maintained fixture-local path:

- `active_mode == neutral_transit_v1`
- single-fleet fixture carrier
- `expected_position_candidate_active == True`

No viewer work, replay widening, settings growth, or generalized terminal framework work is included.

## Implementation

Code touchpoints:

- `runtime/engine_skeleton.py`
- `test_run/test_run_execution.py`

The current split cut does the following:

1. `_build_fixture_expected_position_map(...)` still honors terminal-latched axis data when `frozen_terminal_frame_active == True`.
2. It no longer rewrites `centroid_x / centroid_y` to a latched terminal centroid.
3. Expected positions are therefore rebuilt each subsequent tick using:
   - live centroid center
   - frozen terminal primary axis
   - optional frozen terminal secondary axis
4. Fixture-local latch writeout now records only:
   - `frozen_terminal_frame_active`
   - `frozen_terminal_latched_tick`
   - `frozen_terminal_primary_axis_xy`
   - optional `frozen_terminal_secondary_axis_xy`

The old whole-frame freeze path is no longer active on the bounded candidate-active line.

## Intended effect

This cut is meant to remove the specific mismatch introduced by the prior first cut:

- target keeps pulling toward the real objective anchor
- restore no longer pulls units toward slots centered on a stale first-entry centroid

In short:

- reference orientation stops rotating
- reference center keeps following the actual fleet centroid

## Non-goals

This turn does not:

- modify the target contract
- modify the late clamp rule
- reopen early-side `E2`
- add restore taper families
- add user parameters or settings
- claim closure of the late-terminal residual in advance
