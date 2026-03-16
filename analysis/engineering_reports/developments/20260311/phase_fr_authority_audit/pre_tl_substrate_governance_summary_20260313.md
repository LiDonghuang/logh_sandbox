# Pre-TL Substrate Governance Summary

Date: 2026-03-13
Status: Governance-facing short summary
Scope: Bounded pre-TL substrate selector state, current candidate ranking, and recommended next step
Implementation: Partially completed in `test_run`; no frozen-layer change requested

## 1. Summary judgment

Engineering recommends treating the current pre-TL substrate line as:

- a bounded low-level substrate preparation task
- not a future `TL` definition task
- not a doctrine-freezing step

The current selector set is now sufficient for a clean bounded comparison state:

- default: `nearest5_centroid`
- future candidate 1: `soft_local_weighted`
- future candidate 2: `weighted_local`
- high-scrutiny retained candidate: `local_cluster`

## 2. What changed

`soft_local_weighted` has now been added to `test_run` as a selectable pre-TL substrate.

This change is:

- `test_run` / harness-only
- not a runtime baseline change
- not a frozen-layer modification
- not a semantic promotion of future `TL`

The active default remains:

- `nearest5_centroid`

## 3. Why `soft_local_weighted` is worth retaining

Earlier bounded in-memory comparisons indicated:

- `weighted_local` can improve early `FrontCurv` symmetry
- but often pays a stronger mid/late-phase cost

`soft_local_weighted` was constructed as a softer local-envelope alternative:

- nearest-`8` local enemy pool
- continuous radial weighting
- smooth envelope around the current nearest-`5` boundary

Engineering judgment from the bounded comparisons is:

- `soft_local_weighted` preserves more locality than `weighted_local`
- handles degeneracy more cleanly than hard `nearest5`
- often recovers part of `weighted_local`'s late regression
- is not yet strong enough to replace `nearest5_centroid` as default

## 4. Current ranking

Engineering's current bounded ranking is:

1. `nearest5_centroid` as practical default
2. `soft_local_weighted` as leading future candidate
3. `weighted_local` as secondary future candidate
4. `local_cluster` retained under stricter scrutiny

This ranking is about:

- neutral substrate quality
- symmetry safety
- degeneracy safety
- locality / contact relevance

It is not a future `TL` semantic ranking.

## 5. Why no default switch is recommended yet

Current evidence does not justify switching the default away from `nearest5_centroid`.

Reason:

- `soft_local_weighted` looks more promising than `weighted_local`
- but it still shows mixed trade-offs across mirrored fixtures
- and no candidate has yet earned a clean "replace default" judgment

So the correct bounded state is:

- keep `nearest5_centroid` as default
- retain `soft_local_weighted` and `weighted_local` as selectable future candidates

## 6. Recommended next step

Engineering recommends only one bounded next step:

- a narrow mirrored comparison centered on:
  - `nearest5_centroid`
  - `soft_local_weighted`
  - optional secondary reference: `weighted_local`

The goal should remain:

- compare substrate quality
- not define future `TL`
- not reopen broad personality DOE
- not promote a permanent doctrinal winner yet

## 7. Boundary reminder

Even after this selector expansion:

- the low-level substrate remains only a weighting structure
- future `TL` still owns targeting horizon and targeting preference semantics
- observed targeting patterns remain emergent outputs, not guaranteed signatures of one substrate
