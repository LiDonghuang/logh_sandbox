# pr9_low_level_locomotion_partial_default_revert_record_20260418

## Scope

- runtime default settings
- partial revert after Human review
- low-level locomotion defaults only

## What changed

After Human review on `36 vs 36`, the previous low-level tuning convergence was
accepted only in part.

The maintained defaults were partially reverted:

- `max_accel_per_tick`: `0.30 -> 0.25`
- `max_turn_deg_per_tick`: `14.0 -> 18.0`
- `turn_speed_min_scale`: unchanged at `0.35`

The following value was intentionally left unchanged in this slice:

- `max_decel_per_tick = 0.65`

## Reason for partial revert

Human judged that the earlier defaults for acceleration and turn-rate were more
reasonable, while the deeper post-contact contact / retreat / collapse question
should be discussed as a separate mechanism issue rather than silently folded
into low-level tuning.

## Boundary

This record does **not** claim that the post-contact reverse / retreat semantics
are solved here.

It only records the bounded default-value rollback requested after Human
inspection.

## Files in scope

- `test_run/test_run_v1_0.runtime.settings.json`
