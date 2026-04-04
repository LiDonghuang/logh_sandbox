# PR6 Hold Raw-to-Current Smoothing Reactivation Record

Status: local engineering record  
Date: 2026-04-04  
Scope: test-run public config interface / harness-only local line  
Boundary: no frozen-runtime change, no remote push

## What Changed

The active local `v4a` near-contact line restores only the first hold
raw-to-current smoothing seam:

- `runtime.movement.v4a.battle_hold_relaxation`
- `runtime.movement.v4a.battle_approach_drive_relaxation`

These now materially own:

- smoothing from `battle_relation_gap_raw` into `battle_relation_gap_current`
- smoothing of `battle_close_drive_current`
- smoothing of `battle_brake_drive_current`
- smoothing of `battle_hold_weight_current`
- separate smoothing of `battle_approach_drive_current`

## What Is Explicitly Not Restored

This reactivation does **not** restore the retired near-contact internal
stability line:

- `battle_near_contact_internal_stability_blend`
- `battle_near_contact_speed_relaxation`

Those remain retired from the active public `v4a` surface in this round.

## Scope Clarification

This record only covers the active `test_run` / harness-side interface.

It does not claim:

- a final battle doctrine
- a frozen runtime semantic change
- a full restoration of the previously removed smoothing family

It records a bounded reactivation of the first hold smoothing seam after the
`restore_strength` anchor was restored.
