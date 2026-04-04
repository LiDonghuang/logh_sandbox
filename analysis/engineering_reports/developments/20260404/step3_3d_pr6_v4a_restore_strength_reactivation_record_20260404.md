## Scope

- test-only / harness-only
- `test_run` v4a movement surface
- no frozen runtime modification

## What changed

`runtime.movement.v4a.restore_strength` has been reactivated on the current local line.

The public surface now again feeds the runtime movement surface for `v4a` as:

- `movement_surface["v3a_experiment"] = exp_precontact_centroid_probe` when `restore_strength < 1.0`
- `movement_surface["centroid_probe_scale"] = restore_strength`

and falls back to:

- `movement_surface["v3a_experiment"] = base`
- `movement_surface["centroid_probe_scale"] = 1.0`

when `restore_strength == 1.0`.

## Why this was restored

Local comparison against the `0402` anchor showed:

- current local scene had `v3a_experiment = base`
- current local scene had `centroid_probe_scale = 1.0`
- `0402` had `v3a_experiment = exp_precontact_centroid_probe`
- `0402` had `centroid_probe_scale = 0.25`

Under `runtime_decision_source = v3_test`, that difference was active and materially changed `tick=1` movement.

Restoring the `0.25` path reproduced the `0402` `tick=1` battle and neutral movement decomposition exactly.

## Validation summary

For `battle 1->4`, `max_steps = 5`, `tick = 1`:

- `front_curvature_tick1_A` returned to `-0.0006960814463861098`
- `center_mean_vlat` returned to `0.003014`
- `wings_mean_vlat` returned to `0.002153`

matching the `0402` anchor.

## Interface note

This reverses a previous incorrect retirement of `v4a.restore_strength`.

That retirement was not semantically valid because the path remained active under:

- `runtime_decision_source = v3_test`
- runtime movement surface reuse inside `v4a`
