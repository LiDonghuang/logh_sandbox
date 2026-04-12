# Step3 3D PR6 - Hold Radius and Neutral Relation Cleanup Record - 2026-04-08

## Scope

- line of work: `battle / neutral` movement-family unification
- layer scope:
  - `test_run` harness
  - minimal runtime bridge rename only where `stop_radius` was still an active fixture gate
- out of scope:
  - targeting
  - terminal/hold redesign
  - old-family retirement
  - compute optimization

## Why this round happened

After `restore_strength` was cleaned into a direct `v4a` seam, Human confirmed:

- battle `1->4` looked acceptable again with `restore_strength=0.05`
- but neutral still differed from battle
- and the public objective-radius semantics were split across:
  - `stop_radius`
  - `hold_stop_radius`

Static audit then showed:

1. neutral still had residual special relation semantics inside `_evaluate_target_with_pre_tl_substrate()`
2. `stop_radius` remained active in the runtime fixture step gate
3. active `v4a` harness hot path still contained redundant silent parameter fallbacks that were already covered by scenario preparation validation

## Changes made

### 1. Public objective radius semantics unified to `hold_radius`

Renamed the active public / bridge carrier from:

- `stop_radius`
- `hold_stop_radius`

to:

- `hold_radius`

Touched:

- `test_run/test_run_scenario.py`
- `test_run/test_run_execution.py`
- `runtime/engine_skeleton.py`
- `test_run/test_run_entry.py`
- `test_run/test_run_v1_0.testonly.settings.json`
- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`

Current read:

- `hold_radius` is the shared objective hold / termination radius semantic
- it is no longer described as a separate neutral-only movement relation owner

### 2. Neutral residual relation semantics deleted from the shared evaluator

Inside `_evaluate_target_with_pre_tl_substrate()`:

- neutral no longer gets its own:
  - `target_front_strip_gap = hold_radius`
  - `hold_band = expected_reference_spacing`
  - `target_front_strip_gap_bias = 0`

Instead:

- neutral now uses the same relation family as battle
- the only remaining semantic difference is objective source:
  - battle -> enemy reference
  - neutral -> fixture objective point

### 3. Active-path silent fallbacks reduced

Removed the runtime-tick fallback rewrites for active `v4a` relation parameters in the shared evaluator:

- `battle_target_front_strip_gap_bias`
- `battle_relation_lead_ticks`
- `battle_hold_relaxation`
- `battle_approach_drive_relaxation`

Those values are already validated earlier during scenario/runtime configuration preparation.

## What stayed intentionally unchanged

- battle transition mechanisms were not deleted
- neutral was not reverted to an older arrival-only path
- bounded normalization / clamp semantics were not touched
- terminal / hold latching redesign was not reopened

## Validation

Minimal checks:

- `py_compile`
  - `runtime/engine_skeleton.py`
  - `test_run/test_run_execution.py`
  - `test_run/test_run_scenario.py`
  - `test_run/test_run_entry.py`

Minimal smoke:

- `battle_4to1`, `5` ticks: passed
- `neutral_4to1`, `5` ticks: passed

Narrow numeric read after the change:

- by frame `5`, battle and neutral now share the same relation-side focus indicators in the tested `4->1` probe
- but Human-facing residual difference still appears in actual formation compression / arrival behavior

## Current honest read

This round removed real residual neutral-only movement logic and cleaned a split radius semantic.

However, it did **not** fully solve:

- neutral `4->1` lacking battle-like forward compression
- neutral arrival-side collapse

So the current truthful read is:

- the active neutral-specific relation owner was reduced
- but the remaining residual difference now lies deeper than the deleted neutral special branch alone
