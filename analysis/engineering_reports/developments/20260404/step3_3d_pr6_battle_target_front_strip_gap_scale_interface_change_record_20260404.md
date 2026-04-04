# PR6 Battle Target Front-Strip Gap Scale Interface Change Record

Status: local engineering record  
Date: 2026-04-04  
Scope: test-run public config interface / harness-only local line  
Boundary: no frozen-runtime change, no remote push

## What Changed

The active local `v4a` near-contact relation now exposes one single public
correction parameter:

- `runtime.movement.v4a.battle_target_front_strip_gap_scale`

This parameter multiplies the base target front-strip gap:

- `target_front_strip_gap = max(0, attack_range - expected_reference_spacing) * battle_target_front_strip_gap_scale`

Default local test-only value in the layered testonly settings is now:

- `0.8`

## What Was Removed

The following two public test-run interfaces were removed from the active
`v4a` movement settings surface:

- `runtime.movement.v4a.battle_standoff_self_extent_weight`
- `runtime.movement.v4a.battle_standoff_enemy_extent_weight`

Reason:

- on the active local line they were no longer honest owners of the near-contact
  relation
- leaving them in the public settings surface would continue to mislead Human
  observation and parameter interpretation

## Scope Clarification

This record only covers the active `test_run` / harness-side interface.

It does **not** claim:

- a final battle doctrine
- a final fire-plane doctrine
- a frozen runtime semantic change

It records a narrowing of the active local public parameter surface so Human
observation matches the parameters that still materially own the mechanism.
