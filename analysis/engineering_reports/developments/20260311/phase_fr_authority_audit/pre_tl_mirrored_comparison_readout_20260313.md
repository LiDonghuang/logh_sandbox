# Pre-TL Mirrored Comparison Readout

Date: 2026-03-13
Status: Engineering readout note
Scope: Bounded mirrored close-contact comparison across the currently retained pre-TL substrate selector set.

## 1. Fixture

This readout uses the current mirrored close-contact diagnostic fixture:

- same-force
- mirrored geometry
- all-5 personality parameters
- `test_mode = 2`
- `movement_v3a_experiment = exp_precontact_centroid_probe`
- `symmetric_movement_sync_enabled = true`

The comparison is limited to the current selector set:

- `nearest5_centroid`
- `weighted_local`
- `local_cluster`

This is a bounded substrate-quality readout, not a future `TL` doctrinal choice.

## 2. Readout windows

The run window is fixed at `120 ticks`.

Primary readouts:

- `first_contact_tick`
- `frontcurve_diff_t1_20`
- `frontcurve_diff_t21_40`
- `frontcurve_diff_t41_80`
- `cws_diff_t1_20`
- `cws_diff_t21_40`
- `cws_diff_t41_80`
- `remaining-force gap` as secondary evidence only

## 3. Results

### `nearest5_centroid`

- `first_contact_tick = 20`
- `remaining A/B = 48 / 49`
- `remaining-force gap = 1.0% of initial force`
- `frontcurve_diff_t1_20 = 0.2052`
- `frontcurve_diff_t21_40 = 0.3198`
- `frontcurve_diff_t41_80 = 0.3444`
- `cws_diff_t1_20 = 0.0031`
- `cws_diff_t21_40 = 0.0719`
- `cws_diff_t41_80 = 0.1735`

### `weighted_local`

- `first_contact_tick = 20`
- `remaining A/B = 45 / 45`
- `remaining-force gap = 0.0% of initial force`
- `frontcurve_diff_t1_20 = 0.0552`
- `frontcurve_diff_t21_40 = 0.3053`
- `frontcurve_diff_t41_80 = 0.2901`
- `cws_diff_t1_20 = 0.0045`
- `cws_diff_t21_40 = 0.0589`
- `cws_diff_t41_80 = 0.1197`

### `local_cluster`

- `first_contact_tick = 20`
- `remaining A/B = 45 / 45`
- `remaining-force gap = 0.0% of initial force`
- `frontcurve_diff_t1_20 = 0.0856`
- `frontcurve_diff_t21_40 = 0.3004`
- `frontcurve_diff_t41_80 = 0.4961`
- `cws_diff_t1_20 = 0.0050`
- `cws_diff_t21_40 = 0.0504`
- `cws_diff_t41_80 = 0.2607`

## 4. Comparative reading

### Symmetry safety

Current bounded readout suggests:

- `weighted_local` performs best on early `FrontCurv` symmetry safety
- `local_cluster` is better than `nearest5_centroid` in the earliest `FrontCurv` window, but degrades badly later
- `nearest5_centroid` remains the weakest on early `FrontCurv` symmetry among the three retained selectors

On end-state gap alone:

- `weighted_local` and `local_cluster` both end at `0.0%`
- `nearest5_centroid` ends at `1.0%`

Under the current mirrored interpretation rule, all three remain below the provisional caution boundary and this readout stays secondary.

### Smoothness

Current bounded readout suggests:

- `weighted_local` remains the smoothest practical candidate across the observed windows
- `nearest5_centroid` is acceptable but less stable in early `FrontCurv`
- `local_cluster` remains the most volatile of the three, especially by `ticks 41-80`

### Locality / contact relevance

All three preserve the same `first_contact_tick = 20`, so no candidate here clearly destroys short-horizon contact relevance in this fixture.

Among them:

- `nearest5_centroid` still best preserves explicit local flavor
- `weighted_local` remains at risk of sliding toward the more global shoulder
- `local_cluster` remains local, but at the cost of higher later volatility

### Extensibility for future TL

Current bounded engineering reading remains:

- `nearest5_centroid` is the cleanest current default substrate candidate
- `weighted_local` is the strongest symmetry/smoothness future candidate
- `local_cluster` can remain retained, but under stricter scrutiny

## 5. Current engineering judgment

This readout does not overturn the current end-state plan.

It reinforces the current bounded arrangement:

- default: `nearest5_centroid`
- retained future candidate: `weighted_local`
- retained future candidate: `local_cluster`

Reason:

- `weighted_local` is strongest on symmetry/smoothness, but still sits closest to the "too-global" shoulder
- `nearest5_centroid` remains the best current balance candidate among explicitly local smooth families
- `local_cluster` remains admissible, but still less stable and more governance-sensitive

## 6. Boundary reminder

This readout must not be interpreted as:

- future `TL` implementation
- a permanent doctrinal freeze
- proof that one selector guarantees a battlefield signature

It is only a bounded comparison of pre-TL substrate quality under the current mirrored diagnostic fixture.

## 7. Narrow mirrored follow-up after `soft_local_weighted` implementation

After `soft_local_weighted` was added to `test_run`, Engineering ran one additional narrow mirrored comparison:

- `6` representative mirrored fixtures
- `3` substrates
  - `nearest5_centroid`
  - `soft_local_weighted`
  - `weighted_local`
- total `18` runs

Representative fixture set:

- `long_10_100`
- `mid_30_100`
- `mid_50_50`
- `mid_50_100`
- `mid_50_150`
- `close_90_100`

All fixtures remained:

- same-force
- mirrored geometry
- all-5 personalities
- `aspect_ratio = 2.0`
- `120` ticks

### Aggregate readout across the 6 fixtures

`nearest5_centroid`

- `mean frontcurve_diff_t1_20 = 0.1654`
- `mean frontcurve_diff_t21_50 = 0.1831`
- `mean frontcurve_diff_t51_120 = 0.3247`
- `mean cws_diff_t1_20 = 0.0065`
- `mean remaining-force gap = 1.7778%`

`soft_local_weighted`

- `mean frontcurve_diff_t1_20 = 0.1703`
- `mean frontcurve_diff_t21_50 = 0.2319`
- `mean frontcurve_diff_t51_120 = 0.4020`
- `mean cws_diff_t1_20 = 0.0096`
- `mean remaining-force gap = 1.5556%`

`weighted_local`

- `mean frontcurve_diff_t1_20 = 0.1630`
- `mean frontcurve_diff_t21_50 = 0.1760`
- `mean frontcurve_diff_t51_120 = 0.3821`
- `mean cws_diff_t1_20 = 0.0080`
- `mean remaining-force gap = 0.8333%`

### Direct reading

This follow-up does **not** strengthen the case for `soft_local_weighted`.

On this narrow implemented comparison:

- `soft_local_weighted` is slightly worse than `nearest5_centroid` even in the earliest `FrontCurv` window
- it is clearly worse than `nearest5_centroid` in the `21..50` and `51..120` windows
- it is also worse than `weighted_local` on the aggregate observer readout

Representative deltas against `nearest5_centroid`:

- `long_10_100`
  - `d_fc1_20 = -0.0788`
  - `d_fc21_50 = +0.0946`
  - `d_fc51_120 = +0.0445`
- `mid_30_100`
  - `d_fc1_20 = +0.0394`
  - `d_fc21_50 = +0.0902`
  - `d_fc51_120 = +0.1709`
- `close_90_100`
  - `d_fc1_20 = +0.0836`
  - `d_fc21_50 = +0.0779`
  - `d_fc51_120 = +0.1351`

Here:

- negative delta means `soft_local_weighted` improved relative to `nearest5_centroid`
- positive delta means it worsened

So the implemented `soft_local_weighted` prototype still shows:

- some value as a degeneracy-softening concept
- but no clean mirrored-readout advantage yet

### Engineering update

The current engineering reading should therefore be tightened:

- `nearest5_centroid` remains the practical default
- `weighted_local` still reads better on pure mirrored observer metrics
- `soft_local_weighted` remains conceptually interesting because it directly addresses hard-boundary degeneracy, but the current implementation does not yet justify promoting it above `weighted_local` on readout quality alone

This means:

- the current selector state remains useful
- but the `soft_local_weighted` case should still be treated as provisional
- and the broader boundary reminder remains unchanged:

```text
this is pre-TL substrate ranking,
not future TL semantics ranking
```

## 8. Narrow parameter follow-up inside the soft-local family

Engineering then ran one additional bounded parameter comparison inside the `soft_local_weighted` family.

This was still a narrow mirrored comparison:

- `4` representative mirrored fixtures
  - `long_10_100`
  - `mid_30_100`
  - `mid_50_100`
  - `close_90_100`
- `5` configurations
  - `nearest5_centroid`
  - `weighted_local`
  - current implemented `soft_local_weighted`
  - `soft_tight`
  - `soft_wide`
- total `20` runs

Here:

- `soft_current` = current implemented `soft_local_weighted`
- `soft_tight` = same local pool / boundary rank, but with a narrower smooth envelope
- `soft_wide` = same local pool / boundary rank, but with a wider smooth envelope

### Aggregate readout

`nearest5_centroid`

- `mean frontcurve_diff_t1_20 = 0.1591`
- `mean frontcurve_diff_t21_50 = 0.1877`
- `mean frontcurve_diff_t51_120 = 0.3393`
- `mean cws_diff_t1_20 = 0.0068`
- `mean remaining-force gap = 1.50%`

`weighted_local`

- `mean frontcurve_diff_t1_20 = 0.1544`
- `mean frontcurve_diff_t21_50 = 0.1828`
- `mean frontcurve_diff_t51_120 = 0.3440`
- `mean cws_diff_t1_20 = 0.0088`
- `mean remaining-force gap = 1.25%`

`soft_current`

- `mean frontcurve_diff_t1_20 = 0.1709`
- `mean frontcurve_diff_t21_50 = 0.2648`
- `mean frontcurve_diff_t51_120 = 0.4098`
- `mean cws_diff_t1_20 = 0.0119`
- `mean remaining-force gap = 1.00%`

`soft_tight`

- `mean frontcurve_diff_t1_20 = 0.1197`
- `mean frontcurve_diff_t21_50 = 0.2063`
- `mean frontcurve_diff_t51_120 = 0.3489`
- `mean cws_diff_t1_20 = 0.0084`
- `mean remaining-force gap = 0.75%`

`soft_wide`

- `mean frontcurve_diff_t1_20 = 0.1401`
- `mean frontcurve_diff_t21_50 = 0.2146`
- `mean frontcurve_diff_t51_120 = 0.3524`
- `mean cws_diff_t1_20 = 0.0123`
- `mean remaining-force gap = 1.25%`

### Direct reading

This additional sweep suggests a more precise conclusion:

- the current implemented `soft_local_weighted` is too loose
- widening the envelope does not help
- narrowing the envelope helps substantially

`soft_tight` is the only soft-local variant in this sweep that looks genuinely competitive.

Its trade-off is:

- clearly best `FrontCurv` performance in the earliest window
- mid-window still worse than `nearest5_centroid` / `weighted_local`
- late-window close to `nearest5_centroid`, and much better than `soft_current`

So the engineering reading is now:

- `soft_local_weighted` as currently implemented remains provisional and not strong enough
- but the soft-local family itself should not be discarded
- a tighter-envelope version is the first soft-local direction that looks worth preserving for future comparison

### Updated engineering reading

Current bounded ranking remains unchanged at the implemented-selector level:

- default: `nearest5_centroid`
- active future candidates: `weighted_local`, `soft_local_weighted`, `local_cluster`

But inside the soft-local family, the current internal priority should be read as:

1. `soft_tight` direction
2. current `soft_local_weighted`
3. `soft_wide`

This is still a substrate-quality comparison only.

It is not:

- a future `TL` semantic ranking
- a doctrine decision
- an authorization to switch the default

## 9. Implemented `soft_local_weighted_tight` follow-up

Engineering then promoted the tighter soft-local direction into `test_run` as a selectable test-only substrate:

- `soft_local_weighted_tight`

The next narrow mirrored comparison used:

- `6` representative mirrored fixtures
- `3` implemented substrates
  - `nearest5_centroid`
  - `soft_local_weighted_tight`
  - `weighted_local`
- total `18` runs

### Aggregate readout

`nearest5_centroid`

- `mean frontcurve_diff_t1_20 = 0.1654`
- `mean frontcurve_diff_t21_50 = 0.1831`
- `mean frontcurve_diff_t51_120 = 0.3247`
- `mean cws_diff_t1_20 = 0.0065`
- `mean remaining-force gap = 1.7778%`

`soft_local_weighted_tight`

- `mean frontcurve_diff_t1_20 = 0.1432`
- `mean frontcurve_diff_t21_50 = 0.1888`
- `mean frontcurve_diff_t51_120 = 0.3352`
- `mean cws_diff_t1_20 = 0.0077`
- `mean remaining-force gap = 1.0556%`

`weighted_local`

- `mean frontcurve_diff_t1_20 = 0.1630`
- `mean frontcurve_diff_t21_50 = 0.1760`
- `mean frontcurve_diff_t51_120 = 0.3821`
- `mean cws_diff_t1_20 = 0.0080`
- `mean remaining-force gap = 0.8333%`

### Direct reading

This is the first soft-local variant that looks genuinely competitive after implementation.

Compared with `nearest5_centroid`, `soft_local_weighted_tight` reads as:

- clearly better in the earliest `FrontCurv` window
- slightly worse in the middle and late `FrontCurv` windows
- slightly worse on early `C_W_SPhere`
- somewhat smaller remaining-force gap

Compared with `weighted_local`, it reads as:

- clearly better on late `FrontCurv`
- slightly worse on the middle window
- slightly better on early `C_W_SPhere`

Representative deltas versus `nearest5_centroid`:

- `long_10_100`
  - `d_fc1_20 = -0.1188`
  - `d_fc21_50 = +0.0522`
  - `d_fc51_120 = +0.0387`
- `mid_50_100`
  - `d_fc1_20 = -0.0248`
  - `d_fc21_50 = +0.0072`
  - `d_fc51_120 = -0.1370`
- `close_90_100`
  - `d_fc1_20 = +0.0158`
  - `d_fc21_50 = +0.0714`
  - `d_fc51_120 = +0.1298`

So the tighter soft-local version still has real trade-offs, but it is no longer behaving like the weaker `soft_local_weighted` baseline.

### Updated engineering reading

At the implemented-selector level, the current bounded ordering is best read as:

1. `nearest5_centroid` remains the practical default
2. `soft_local_weighted_tight` becomes the leading future candidate
3. `weighted_local` remains a useful but more globally leaning comparison candidate

Reason:

- `nearest5_centroid` still has the cleanest overall balance
- `soft_local_weighted_tight` now improves the early degeneracy-sensitive `FrontCurv` window without collapsing into the weaker `soft_local_weighted` behavior
- `weighted_local` still smooths early geometry, but its later `FrontCurv` cost remains more pronounced

This still remains:

```text
pre-TL substrate ranking,
not future TL semantics ranking
```
