Scope: harness-only local candidate

Status
- local implementation candidate
- no push
- no runtime-core change

Purpose
- isolate the early `battle 1->4` center-ahead arc
- test whether battle-side harness pre-processing is polluting expected-position realization during the clearly far-from-engagement phase

Change
- In `test_run_execution.py::integrate_movement()`, add a narrow subtraction probe:
  - when:
    - not using the neutral fixture bundle path
    - `formation_hold_active == False`
    - `formation_terminal_active == False`
    - `battle_relation_gap_current >= 0.25`
    - `engagement_geometry_active_current <= 0.05`
  - then:
    - skip the battle-side pre-processing block that rewrites:
      - `last_target_direction`
      - `movement_heading_current_xy`
      - per-unit transition speed envelope
    - and allow runtime to consume the expected-position bridge with the unmodified state

Intent
- This is subtraction-first.
- It does not add a new owner.
- It does not add a new public setting.
- It does not change frozen runtime semantics.
- It only removes battle harness pre-processing from the clearly far phase.

Expected read
- If the early arc is being created mainly by battle harness pre-processing, this candidate should reduce it.
- If not, the arc owner lies deeper elsewhere.
