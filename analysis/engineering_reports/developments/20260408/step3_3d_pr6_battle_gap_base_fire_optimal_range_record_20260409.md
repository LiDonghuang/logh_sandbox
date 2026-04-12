# step3_3d_pr6_battle_gap_base_fire_optimal_range_record_20260409

## Scope

- active `v4a` battle near-contact gap semantics
- harness/runtime-facing formula cleanup only
- no public interface addition

## Change

In `test_run/test_run_execution.py`, the active `v4a` battle front-strip target-gap base no longer reads:

- `attack_range - expected_reference_spacing`

It now reads:

- `fire_optimal_range - expected_reference_spacing`

where:

- `fire_optimal_range = attack_range * fire_optimal_range_ratio`

The existing public correction seam remains unchanged:

- `battle_target_front_strip_gap = max(0, battle_target_front_strip_gap_base + battle_target_front_strip_gap_bias)`

## Why

Battle distance maintenance should align with the current fire-control model's effective
full-quality range, not the absolute maximum range ceiling.

Using `attack_range` as the battle standoff base pushed the maintained distance too far
outward under the current fire model and forced overly negative `battle_target_front_strip_gap_bias`
values in order to recover practical battle spacing.

## Truth surface updates

Updated:

- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`

to reflect the new base-gap read.
