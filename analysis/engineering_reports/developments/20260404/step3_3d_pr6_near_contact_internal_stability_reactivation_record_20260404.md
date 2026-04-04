# PR6 Near-Contact Internal Stability Reactivation Record

Status: local engineering record  
Date: 2026-04-04  
Scope: test-run public config interface / harness-only local line  
Boundary: no frozen-runtime change, no remote push

## What Changed

The active local `v4a` near-contact line restores the previously retired
internal-stability group:

- `runtime.movement.v4a.battle_near_contact_internal_stability_blend`
- `runtime.movement.v4a.battle_near_contact_speed_relaxation`

These now materially own:

- near-contact pulling of `forward_transport_speed_scale` toward `1.0`
- near-contact pulling of `shape_speed_scale` toward the fleet-level advance
  floor read
- per-unit `max_speed` smoothing toward `transition_speed_target`

## Scope Clarification

This reactivation is additive only to the already restored hold raw-to-current
smoothing seam and the restored `v4a.restore_strength` bridge.

It does not claim:

- a final battle doctrine
- a frozen runtime semantic change
- a broader restoration of all previously removed battle-side probes

## Defaults Restored

- `battle_near_contact_internal_stability_blend = 0.55`
- `battle_near_contact_speed_relaxation = 0.28`
