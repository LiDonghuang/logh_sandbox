# FrontCurv Observer Audit

Date: 2026-03-13
Status: Engineering audit note
Scope: Diagnose why `FrontCurv` still shows visible A/B mismatch during long-range mirrored pre-contact approach, even after observer-axis and mirrored-geometry cleanup.

## 1. Why this audit was opened

The active `test_run` setting was switched from the mirrored close-contact fixture to the longer-range mirrored diagonal opening:

- same-force
- same all-5 personalities
- mirrored deployment
- mirrored facing
- current default pre-TL substrate: `nearest5_centroid`

Under this setting, human visual review reported that `FrontCurve` still diverges visibly in the first `50` ticks.

The key question was:

- is this another pre-TL substrate problem?
- or is `FrontCurv` itself still too sensitive as an observer during long-range pre-contact approach?

## 2. First bounded result

The first bounded re-run showed:

- `first_contact_tick = 115`
- `alive @ tick 50 = 100 / 100`
- `alive @ tick 120 = 100 / 100`

So the visible mismatch through `ticks 1..50` is not a contact-phase amplification artifact.
It is a pure pre-contact observer/readout issue.

Current-default (`nearest5_centroid`) readout:

- `frontcurve_diff_t1_20 = 0.2219`
- `frontcurve_diff_t21_40 = 0.0691`
- `frontcurve_diff_t41_50 = 0.0582`

But corresponding `C_W_SPhere` gaps remain small:

- `cws_diff_t1_20 = 0.0056`
- `cws_diff_t21_40 = 0.0035`
- `cws_diff_t41_50 = 0.0015`

Engineering reading:

- wide movement/posture symmetry is still mostly intact
- the dominant visible mismatch is concentrated in `FrontCurv`

## 3. Substrate comparison does not explain the whole issue

The same long-range mirrored setting was then compared across the three retained pre-TL substrates:

- `nearest5_centroid`
- `weighted_local`
- `local_cluster`

Representative readout:

### `nearest5_centroid`

- `fc 1..20 = 0.2219`
- `fc 21..50 = 0.0655`
- `cws 1..20 = 0.0056`
- `cws 21..50 = 0.0028`

### `weighted_local`

- `fc 1..20 = 0.1262`
- `fc 21..50 = 0.1360`
- `cws 1..20 = 0.0071`
- `cws 21..50 = 0.0057`

### `local_cluster`

- `fc 1..20 = 0.2214`
- `fc 21..50 = 0.2770`
- `cws 1..20 = 0.0054`
- `cws 21..50 = 0.0025`

Engineering reading:

- substrate choice does modulate `FrontCurv`
- but all three retained substrates still show much larger `FrontCurv` mismatch than `C_W_SPhere` mismatch in the same pre-contact window
- so the dominant new suspicion is not simply "the default substrate is wrong"

## 4. Current `FrontCurv` construction under audit

Current `FrontCurv` logic is:

1. project all units onto the local enemy-facing axis
2. take the top `30%` of units by projected advance
3. sort only that front group by width rank
4. split that front group into center vs wing halves
5. define `FrontCurv` as:

```text
mean(advance of front-center band) - mean(advance of front-wing band)
```

The audit question is whether this construction is intrinsically too sensitive before a physically meaningful front has formed.

## 5. Front-band width sensitivity test

Using the same long-range mirrored trajectory, `FrontCurv` was recomputed offline with different front-band widths.

Representative A/B absolute-difference summary:

### top `10%`

- `diff_t1_20 = 0.1024`
- `diff_t21_50 = 0.0762`

### top `20%`

- `diff_t1_20 = 0.1513`
- `diff_t21_50 = 0.0659`

### top `30%` (current)

- `diff_t1_20 = 0.4438`
- `diff_t21_50 = 0.1310`

### top `40%`

- `diff_t1_20 = 0.1089`
- `diff_t21_50 = 0.2766`

### all-unit front-weighted variant

- `diff_t1_20 = 0.1148`
- `diff_t21_50 = 0.1233`

Engineering reading:

- the current `top 30%` construction is a strong outlier in the early pre-contact window
- this strongly suggests the observer is highly sensitive to the exact front-band construction
- the issue is not simply "more front band is better" or "less front band is better"
- it is that the current fixed `30%` cut is not robust under long-range mirrored approach

## 6. Front-band membership churn is not the main issue

To test whether the problem was just rapid front-group membership churn, the tick-to-tick Jaccard overlap of front-band membership was checked.

Representative summary over early ticks:

- `top10 = 0.9889`
- `top20 = 0.9788`
- `top30 = 0.9811`
- `top40 = 0.9895`

Engineering reading:

- front-band membership is actually fairly stable
- so the problem is not well explained as "the front set keeps changing every tick"

## 7. Width-split interaction is also part of the problem

The current construction uses width splitting **inside the front group**.

This was compared against a variant that:

- first builds a global center/wing split over the whole fleet
- then reads only the front-band advances through that global split

Representative summary for `top30`:

### current front-internal split

- `diff_t1_20 = 0.4438`
- `diff_t21_50 = 0.1310`

### global-width split applied to top30

- `diff_t1_20 = 0.2380`
- `diff_t21_50 = 0.3150`

Engineering reading:

- the current early mismatch is indeed amplified by doing the width split inside the already hard-cut front band
- but simply switching to a global width split would worsen the later pre-contact window
- so the problem is not solved by one obvious split substitution

## 8. Current engineering judgment

The current `FrontCurv` observer appears too sensitive for long-range mirrored pre-contact use.

More specifically:

- the issue is not primarily contact amplification
- not primarily front-band membership churn
- not primarily one substrate default
- but rather the interaction of:
  - a hard front-band cut
  - a center/wing split derived from that cut
  - a phase where a true physical front has not yet formed

So the best current engineering reading is:

```text
FrontCurv is currently reliable enough as a contact-near / posture-phase readout,
but still too fragile as a long-range mirrored pre-contact observer.
```

## 9. Current boundary conclusion

This audit does not authorize an implementation change by itself.

It does justify a stricter interpretation boundary:

- during long-range mirrored pre-contact approach,
  visible `FrontCurv` mismatch should be treated with caution
- it should not automatically be read as a low-level asymmetry proof
- and it should not be used as primary evidence for personality-mechanism effects in that phase

## 10. Next audit question

If this line continues, the next bounded question should be:

- whether `FrontCurv` should remain active as-is in long-range mirrored pre-contact diagnostics
- or whether it needs a phase-qualified interpretation, or a different front construction for that regime
