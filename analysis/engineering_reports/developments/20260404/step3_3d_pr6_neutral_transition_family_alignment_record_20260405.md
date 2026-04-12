# step3_3d_pr6_neutral_transition_family_alignment_record_20260405

Status: local implementation record  
Scope: harness-only / `test_run` movement bridge  
Branch state: local dirty worktree, not committed

## Purpose

Align `neutral_transit_v1` with the same active `v4a` transition-mechanism family already used by battle, without deleting or weakening the established battle-side line.

This round does **not** broaden doctrine and does **not** redesign runtime movement. It only removes one concrete family mismatch:

- before: neutral objective path still used a direct `arrival_gain` target carrier
- after: neutral objective path now uses the same signed relation / hold smoothing family that battle already uses

## Files

- `test_run/test_run_execution.py`

## Change

In `_evaluate_target_with_fixture_objective()`:

- keep the non-`v4a` fixture path unchanged
- for `v4a` + active fixture bundle:
  - compute `distance_gap = distance_to_objective - stop_radius`
  - reuse the existing `battle_relation_lead_ticks`
  - reuse the existing `battle_hold_relaxation`
  - reuse the existing `battle_approach_drive_relaxation`
  - reuse the existing `battle_hold_weight_strength`
  - update the bundle's current relation fields:
    - `battle_relation_gap_*`
    - `battle_close_drive_*`
    - `battle_brake_drive_*`
    - `battle_hold_weight_*`
    - `battle_approach_drive_*`
  - drive neutral objective motion by:
    - `relation_drive = approach_drive - brake_drive`

So neutral no longer owns a separate direct `arrival_gain` transition carrier in the active `v4a` path.

## Validation

`python -m py_compile test_run/test_run_execution.py`

### `4 -> 1` alignment probe

Settings:

- `movement_model = v4a`
- `cohesion_decision_source = v3_test`
- initial aspect ratio `4.0`
- target reference layout `rect_centered_1.0`

Observed after the change:

- `tick = 1`
  - battle front mean forward displacement: `0.5213`
  - neutral front mean forward displacement: `0.5213`
  - battle back mean forward displacement: `0.0233`
  - neutral back mean forward displacement: `0.0233`
  - battle `td_norm`: `0.077`
  - neutral `td_norm`: `0.077`

This shows that the first-step transition carrier is now aligned between battle and neutral.

### `4 -> 1` later-shape probe

`tick = 5`

- battle `actual_forward`: `5.384`
- neutral `actual_forward`: `6.612`

Compared with the pre-alignment local read, neutral forward compression is materially stronger than before, instead of reading as almost purely lateral tightening.

## Current truthful read

- `battle` transition family was preserved
- `neutral` was moved onto the same signed relation / hold smoothing family
- later battle/neutral divergence still exists and should now be read as a different problem than the earlier missing-family mismatch
