# Runtime Signal Audit Summary

Engine Version: v5.0-alpha5  
Phase: Post-replacement stabilization  
Baseline Under Audit: `v3_test @ 1.1`

## Scope

This was a lightweight stabilization audit, not a new DOE.

It used the frozen post-replacement context:

- movement baseline: `v3a`
- `movement_v3a_experiment = exp_precontact_centroid_probe`
- `centroid_probe_scale = 0.5`
- bridge thresholds:
  - `bridge_theta_split = 1.7`
  - `bridge_theta_env = 0.5`
- runtime collapse source baseline:
  - `v3_test`
  - `v3_connect_radius_multiplier = 1.1`
  - `v3_r_ref_radius_multiplier = 1.0`

## Audit Inputs

### A. Replacement-sensitive confirmation sample

Representative paired batch:

- 9 cells: `FR={2,5,8}`, `MB={2,5,8}`, `PD=5`
- 3 opponents: `mittermeyer`, `muller`, `reinhard`
- 2 paired seed profiles: `SP01`, `SP02`
- baseline source only: `v3_test`

Total baseline runs in this audit view:

```text
54
```

### B. Direct signal readout subset

Direct observer readout:

- same 9 cells
- same 3 opponents
- `SP01`

Total direct signal runs:

```text
27
```

## Runtime-Path Summary

Across the 54-run representative batch:

- `first_deep_pursuit_tick_A`
  - mean = `246.23`
  - min = `54`
  - max = `495`
- `first_deep_pursuit_tick_B`
  - mean = `169.27`
  - min = `25`
  - max = `451`
- `%ticks_deep_pursuit_A` mean = `10.48`
- `%ticks_deep_pursuit_B` mean = `24.91`
- `mean_enemy_collapse_signal_A` mean = `0.2763`
- `mean_enemy_collapse_signal_B` mean = `0.2920`

Interpretation:

- the old `tick=1` saturation is gone
- the new baseline is not suppressed to zero
- the collapse signal remains active, but no longer dominates the full battle from the opening tick

## Direct Signal Readout

Across the 27-run direct observer subset:

- `c_conn_A`
  - mean = `0.8711`
  - min = `0.6931`
  - max = `0.9807`
- `c_conn_B`
  - mean = `0.8410`
  - min = `0.7390`
  - max = `0.9067`
- `rho_A` mean = `0.4429`
- `rho_B` mean = `0.4364`
- `c_scale_A = 1.0` for all runs
- `c_scale_B = 1.0` for all runs
- pre-contact `cohesion_v3` means match `c_conn`, confirming:

```text
collapse signal is currently driven by c_conn semantics,
not by rho/c_scale saturation
```

This is consistent with the earlier semantics-review findings.

## Event Integrity

Across the 54-run representative batch:

- `First Contact` mean = `107.85`
- `Formation Cut` mean = `134.78`
- `Pocket Formation` mean = `158.19`
- `missing_cut = 0`
- `pocket_without_cut = 0`
- `event_order_anomaly_count = 2`

The two anomaly cases were identical in structure:

```text
FR8_MB5_PD5 vs muller
SP01 and SP02
First Contact = 105
First Kill = 114
Pocket Formation = 181
Formation Cut = 338
```

Interpretation:

- anomaly is localized, not broad
- it is a `pocket_before_cut` edge case
- it does not indicate renewed collapse-signal saturation

## Stability

- baseline determinism spot-check: `True`
- no new sign of collapse-signal over-suppression
- no large `rho/c_scale` instability was observed in the representative subset

## Audit Conclusion

The active collapse baseline:

```text
v3_test @ 1.1
```

behaves within an acceptable stabilization envelope.

It avoids the old early-saturation failure, preserves event detectability, and shows no new broad saturation or suppression problem.

One localized `pocket_before_cut` residual remains and should be tracked as an event-bridge edge case, but it is not large enough to block baseline declaration.
