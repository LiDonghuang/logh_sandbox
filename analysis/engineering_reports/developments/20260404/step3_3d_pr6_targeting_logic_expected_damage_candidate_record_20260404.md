# PR6 Targeting Logic Expected-Damage Candidate Record

Status: branch-scoped engineering record  
Date: 2026-04-04  
Scope: runtime combat hot path + test-run runtime interface  
Boundary: `dev_v2.1` candidate; not final doctrine

## What Changed

This local candidate changes unit-level target selection inside
`runtime/engine_skeleton.py::resolve_combat()`.

The old active read was:

- target selection: low-HP priority with only an extremely weak distance tie-break
- fire angle: applied only after target selection as realized-damage quality

The new candidate changes that read to:

- target selection now considers expected damage earlier
- expected damage currently reads as:
  - `base_damage * angle_quality * range_quality`
- realized damage also consumes the same `range_quality`

## New Runtime Surface

Added runtime interface:

- `runtime.physical.fire_control.fire_optimal_range_ratio`

Read:

- `attack_range` remains the max range
- `fire_optimal_range_ratio * attack_range` defines the distance inside which
  range quality remains `1.0`
- beyond that point, range quality decays linearly to `0.0` at `attack_range`

Current default on this line:

- `fire_optimal_range_ratio = 0.5`

## Target Selection Candidate

Current target score is a bounded personality blend:

- `hp_only_score = normalized_hp`
- `expected_damage_score = normalized_hp / expected_damage_ratio`
- `score = (1 - targeting_logic_strength) * hp_only_score + targeting_logic_strength * expected_damage_score`

Where:

- `targeting_logic_strength` comes from normalized fleet `targeting_logic`
- `expected_damage_ratio = angle_quality * range_quality`

This is intentionally a first bounded candidate only.

## Scope Clarification

This record does not claim:

- final targeting doctrine
- final fire-model structure
- completion of `restore_strength` decoupling from `v3_test`
- retirement of `v3a`

Those remain later tasks.
