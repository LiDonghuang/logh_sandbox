# PR6 v4a Near-Contact Parameter Surface Update Record

Status: local engineering record  
Date: 2026-04-04  
Scope: test-run public config interface / harness-only local line  
Boundary: no frozen-runtime change, no remote push

## What Changed

The active local `v4a` near-contact line now exposes the following public
test-only parameters because they are materially used by the current battle
relation and internal hold-stability implementation:

- `runtime.movement.v4a.battle_relation_lead_ticks`
- `runtime.movement.v4a.battle_hold_relaxation`
- `runtime.movement.v4a.battle_approach_drive_relaxation`
- `runtime.movement.v4a.battle_near_contact_internal_stability_blend`
- `runtime.movement.v4a.battle_near_contact_speed_relaxation`

These parameters own:

- how early fleets begin near-contact deceleration
- how raw signed battle-relation values are smoothed into current state
- how quickly forward approach authority follows that state
- how strongly near-contact hold reduces unit-to-unit internal speed divergence
- how quickly per-unit max-speed changes follow near-contact targets

## What Was Removed

The following public test-only interface was removed from the active `v4a`
surface:

- `runtime.movement.v4a.restore_strength`

Reason:

- it no longer honestly owned the active local `v4a` battle / formation line
- it was only being forwarded into an older surface field
- leaving it public would continue to mislead Human observation and parameter interpretation

## Scope Clarification

This record only covers the active `test_run` / harness-side interface.

It does not claim:

- a final battle doctrine
- a frozen runtime semantic change
- a permanent final parameter surface

It records a narrowing and clarification of the active local public parameter
surface so Human-facing settings match the parameters that still materially own
the current near-contact behavior.
