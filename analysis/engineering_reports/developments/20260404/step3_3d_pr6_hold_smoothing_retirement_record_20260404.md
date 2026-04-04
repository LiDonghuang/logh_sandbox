# step3_3d_pr6_hold_smoothing_retirement_record_20260404

Status:
- local change only
- harness-only
- not pushed

Scope:
- retirement of the 2026-04-04 hold raw-to-current smoothing surface
- public `test_run` configuration narrowing

Retired public settings:
- `runtime.movement.v4a.battle_hold_relaxation`
- `runtime.movement.v4a.battle_approach_drive_relaxation`

Execution change:
- near-contact battle relation no longer smooths
  - `battle_relation_gap`
  - `close_drive`
  - `brake_drive`
  - `hold_weight`
  - `approach_drive`
  through separate raw-to-current relaxation.
- current values now collapse back to the raw values in the active harness path.

Reason:
- Human explicitly requested deletion of the added smoothing mechanism.
- The goal of this turn is subtraction-first rollback, not a replacement design.

Boundary:
- no runtime-core change
- no viewer mechanism change
- no change to `battle_relation_lead_ticks`
