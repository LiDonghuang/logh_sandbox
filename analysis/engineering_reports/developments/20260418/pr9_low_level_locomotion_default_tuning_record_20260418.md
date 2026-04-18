# pr9_low_level_locomotion_default_tuning_record_20260418

## Scope

- runtime default settings
- `36 vs 36` behavior tuning anchor
- low-level locomotion parameter convergence only

## Why this record exists

The low-level locomotion seam was already established on `2026-04-17`.

This follow-up record exists because the maintained default parameter values were
then tuned against a Human-reviewed `36 vs 36` anchor window, especially
`tick 70~100` around first contact and early separation.

This is a new independent record rather than a back-edit of the original
establishment note.

## Default-value change

Updated defaults in `test_run/test_run_v1_0.runtime.settings.json`:

- `max_accel_per_tick`: `0.25 -> 0.30`
- `max_decel_per_tick`: `0.35 -> 0.65`
- `max_turn_deg_per_tick`: `18.0 -> 14.0`
- `turn_speed_min_scale`: unchanged at `0.35`

## Human-facing tuning intent

The tuning goal in this slice was narrow:

- do not reopen the repaired neutral / pre-contact regression window
- reduce overly-close first contact in `36 vs 36`
- reduce the visible tendency for early post-contact spacing recovery to happen
  through large body rotation

## Bounded read

This record does **not** claim that the deeper post-contact reference-direction
semantics are fully solved by parameter tuning alone.

It only records the bounded low-level locomotion convergence that improved the
current maintained default behavior window.

## Files in scope

- `test_run/test_run_v1_0.runtime.settings.json`
