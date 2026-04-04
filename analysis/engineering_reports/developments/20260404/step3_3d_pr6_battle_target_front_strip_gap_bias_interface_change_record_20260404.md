# PR6 Battle Target Front-Strip Gap Bias Interface Change Record

Status: local engineering record  
Date: 2026-04-04  
Scope: test-run public config interface / harness-only local line  
Boundary: no frozen-runtime change, no remote push

## What Changed

The active local `v4a` near-contact relation now exposes one single public
correction parameter:

- `runtime.movement.v4a.battle_target_front_strip_gap_bias`

This parameter adds a last-stage distance correction directly onto the base
target front-strip gap:

- `target_front_strip_gap = max(0, attack_range - expected_reference_spacing + battle_target_front_strip_gap_bias)`

Default local test-only value in the layered testonly settings is now:

- `-4.0`

This preserves roughly the same inward shift that the earlier local
`battle_target_front_strip_gap_scale = 0.5` produced under the common working
read:

- `attack_range = 10`
- `expected_reference_spacing = 2`
- base target front-strip gap = `8`

## Why Bias Replaced Scale

The earlier local scale path:

- multiplied `target_front_strip_gap_base`

That was acceptable as a temporary narrowing step, but it was not the cleanest
long-term human-facing correction read.

The current bias path is preferred because it more honestly expresses:

- "move the target front-strip gap inward/outward by a distance amount"

rather than:

- "scale the gap semantics multiplicatively"

This keeps the correction attached to the target front-gap semantics, without
rescaling the final control error or fleet-body geometry.

## What This Record Supersedes

This record supersedes the earlier local scale-interface record:

- `step3_3d_pr6_battle_target_front_strip_gap_scale_interface_change_record_20260404.md`

That earlier note remains useful as local history, but the active public
interface is now the additive bias path.

## Scope Clarification

This record only covers the active `test_run` / harness-side interface.

It does not claim:

- a final battle doctrine
- a final fire-plane doctrine
- a frozen runtime semantic change

It records a narrowing and clarification of the active local public parameter
surface so Human observation matches the parameter that still materially owns
the mechanism.
