# PR6 Front-Strip Gap Target Simplification Local Record

Status: local engineering record  
Date: 2026-04-04  
Scope: harness-only / local candidate  
Boundary: no frozen-runtime change, no remote push

## What Changed

The active local `v4a` near-contact battle relation no longer builds a composite
`desired_distance` from:

- `desired_front_gap`
- own/enemy front-strip depths
- extra weighted body buffer

Instead, it now uses one direct relation target:

- `target_front_strip_gap`

Current read:

- compute current `front_strip_gap`
- compare it directly against `target_front_strip_gap`
- drive the signed near-contact relation from that one difference

## Current Formula

- `fire_entry_margin = expected_reference_spacing`
- `target_front_strip_gap = max(0, attack_range - fire_entry_margin)`
- `current_front_strip_gap = reference_distance - own_front_strip_depth - enemy_front_strip_depth`
- `distance_gap = current_front_strip_gap - target_front_strip_gap`

The signed relation then continues to use the existing speed/tick-scaled relation
band and the existing `approach / close / brake / hold` projection.

## Important Scope Clarification

Under this local candidate, the following settings are no longer active owners of
the near-contact relation formula:

- `battle_standoff_self_extent_weight`
- `battle_standoff_enemy_extent_weight`

Their interface has **not** been deleted in this local turn, but they are not
currently participating in the simplified near-contact target calculation.

This is recorded explicitly so later review does not incorrectly assume they are
still shaping the active near-contact distance read.
