Scope: harness-only local candidate

Status
- local implementation candidate
- no push
- no frozen-runtime change

Purpose
- reduce the early `battle 1->4` center-ahead arc by subtraction
- isolate battle precontact morphology-axis chase as a possible owner

Change
- In `test_run_execution.py::_resolve_v4a_reference_surface()`:
  - during clearly far-from-engagement battle state
  - disable direct `desired_axis_hat = target_forward_hat`
  - keep morphology axis on its current state instead of chasing moving battle target direction

Current bounded condition
- bundle is battle-side (`objective_point_xy` absent)
- `battle_relation_gap_current >= 0.25`
- `engagement_geometry_active_current <= 0.05`

Intent
- subtraction-first only
- no new owner
- no public parameter surface
- no change to neutral fixture path

Expected read
- if the early arc is being driven by battle-side morphology-axis chase, this candidate should visibly reduce it without needing extra smoothing
