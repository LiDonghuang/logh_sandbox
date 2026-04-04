# step3_3d_pr6_far_battle_motion_axis_lock_record_20260404

Status:
- local candidate only
- harness-only
- not pushed

Scope:
- `battle` far-from-engagement motion direction ownership
- no runtime-core change
- no public parameter change

Change:
- In `test_run/test_run_execution.py`, `battle` far-from-engagement motion now locks
  `last_target_direction` onto `initial_forward_hat_xy` instead of continuing to
  chase the moving enemy-centroid direction.
- Activation remains continuous-state based:
  - `battle_relation_gap_current >= V4A_BATTLE_FAR_EXPECTED_POSITION_RELATION_GAP_THRESHOLD`
  - `engagement_geometry_active_current <= V4A_BATTLE_FAR_EXPECTED_POSITION_ENGAGEMENT_THRESHOLD`

Reason:
- Earlier subtraction on `desired_axis_hat` and `resolved_forward_hat` alone did not
  materially change early `battle 1->4` arc.
- In-memory A/B showed that freezing far-phase battle motion direction reduced early
  curvature more meaningfully than those prior axis-only cuts.

Current local telemetry read:
- `front_curvature_index` mean over first 120 ticks:
  - before this cut: `0.1343`
  - after this cut: `0.0924`
- `front_curvature_index` at `tick 80`:
  - before: `0.476`
  - after: `0.158`

Boundary:
- This does not yet claim full visual correction.
- It is a subtraction-first local candidate aimed only at the early
  `battle 1->4` center-ahead arc.
