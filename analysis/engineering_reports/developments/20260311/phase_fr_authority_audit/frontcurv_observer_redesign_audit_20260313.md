# FrontCurv Observer Redesign Audit

Date: 2026-03-13
Status: Engineering redesign audit note
Scope: Compare bounded `FrontCurv` observer redesign candidates without changing runtime or reopening personality-mechanism work.

## 1. Audit goal

The prior audit established that current `FrontCurv` is too sensitive in long-range mirrored pre-contact approach.

The redesign question is narrower:

- is there a bounded observer-shape candidate that improves long-range mirrored stability
- without clearly degrading the close-contact / contact-near diagnostic regime where `FrontCurv` still seems useful

This note remains observer-only.
It does not authorize implementation.

## 2. Candidate family under audit

The current baseline observer uses:

- top `30%` front band by projected advance
- width split inside the front band

This redesign audit compared the following offline variants:

- `top10`
- `top20`
- `top30` (current reference)
- `allweight`

Here:

- `top10` / `top20` / `top30` mean the same basic construction with different front-band widths
- `allweight` means an all-unit weighted variant:
  - build a global center/wing split over the whole fleet
  - assign front weight continuously from projected advance
  - compute a weighted center-vs-wing advance contrast over all units

So `allweight` is the smoothest redesign candidate in this bounded set.

## 3. Two-fixture comparison rule

To keep the redesign bounded and disciplined, the candidates were read against two fixtures:

### A. Long-range mirrored approach

- same-force
- same all-5 personalities
- mirrored diagonal opening
- no contact before `tick 115`

This fixture stresses long-range pre-contact stability.

### B. Mirrored close-contact fixture

- same-force
- same all-5 personalities
- mirrored close-contact opening

This fixture stresses contact-near usefulness.

## 4. Long-range mirrored results

Representative A/B `FrontCurv` absolute-difference summary:

### `top10`

- `diff_t1_20 = 0.1024`
- `diff_t21_50 = 0.0762`

### `top20`

- `diff_t1_20 = 0.1513`
- `diff_t21_50 = 0.0659`

### `top30` (current)

- `diff_t1_20 = 0.4438`
- `diff_t21_50 = 0.1310`

### `allweight`

- `diff_t1_20 = 0.1148`
- `diff_t21_50 = 0.1233`

Engineering reading:

- `top10` is best in the earliest long-range window
- `top20` is acceptable and slightly cleaner than `top10` in the later pre-contact window
- current `top30` is clearly the weakest long-range option in this bounded set
- `allweight` is not best in long-range early ticks, but remains much better than current `top30`

## 5. Close-contact results

Representative A/B `FrontCurv` absolute-difference summary:

### `top10`

- `diff_t1_20 = 0.0587`
- `diff_t21_40 = 0.8350`
- `diff_t41_80 = 0.5385`

### `top20`

- `diff_t1_20 = 0.1174`
- `diff_t21_40 = 0.8291`
- `diff_t41_80 = 0.6350`

### `top30` (current)

- `diff_t1_20 = 0.4105`
- `diff_t21_40 = 0.6396`
- `diff_t41_80 = 0.6887`

### `allweight`

- `diff_t1_20 = 0.2607`
- `diff_t21_40 = 0.4902`
- `diff_t41_80 = 0.5527`

Engineering reading:

- `top10` and `top20` are good only in the earliest pre-contact slice
- once the close-contact fixture reaches contact-near behavior, both become much noisier than desired
- current `top30` is poor early, but not the worst in the immediate contact-near slice
- `allweight` is the strongest balanced candidate in the close-contact fixture

## 6. Trade-off summary

This bounded redesign audit shows a clear trade-off:

- narrower hard front bands (`top10`, `top20`) improve long-range mirrored stability
- but they become too brittle in close-contact / contact-near use
- the current `top30` is weak in long-range and not compelling enough to justify keeping as-is
- `allweight` is not the best in any single slice, but is the most balanced across both fixtures

## 7. Additional 1125-cell DOE reinforcement

To test whether the long-range concern was only a narrow fixture artifact, a larger mirrored same-force DOE was also run with:

- `5` mirrored origin pairs
- `5` aspect ratios
- `5` fleet sizes
- `3` min-separation values
- `3` attack-range values

for a total of `1125` cells, all under:

- same all-5 personalities
- `nearest5_centroid` pre-TL substrate
- `120` ticks

The resulting high-signal findings reinforce the redesign concern rather than weaken it.

### 7.1 Global pattern

Across all `1125` cells:

- `mean frontcurve_diff_t1_20 = 0.1444`
- `mean frontcurve_diff_t21_50 = 0.2303`
- `mean frontcurve_diff_t51_120 = 0.3849`
- `mean cws_diff_t1_20 = 0.0086`
- `mean remaining_gap_pct_initial = 1.2997`

Engineering reading:

- `FrontCurv` asymmetry remains far larger than `C_W_SPhere` asymmetry
- end-state force gap stays small on average
- so the dominant issue continues to look like observer sensitivity, not broad mirrored battle collapse

### 7.2 Min-separation is the strongest new DOE axis

The clearest new main effect is `min_separation`:

- `sep 1.0 -> fc_t1_20 = 0.1737`
- `sep 2.0 -> fc_t1_20 = 0.1426`
- `sep 3.0 -> fc_t1_20 = 0.1169`

This is the strongest single-axis range in the expanded DOE.

Engineering reading:

- tighter packing systematically worsens early mirrored `FrontCurv` mismatch
- this strongly suggests a geometry-sampling / front-band sensitivity problem
- it does **not** point first to attack-range or contact-fire semantics

### 7.3 Attack-range is effectively inert for the early mismatch

By contrast, `attack_range` has almost no effect on `fc_t1_20`:

- `range 3.0 -> 0.1447`
- `range 5.0 -> 0.1444`
- `range 7.0 -> 0.1442`

Engineering reading:

- the early mismatch is not meaningfully explained by attack-range variation
- the redesign target remains observer construction rather than range-related mechanics

### 7.4 Distance, size, and aspect still matter

The DOE also shows weaker but still real dependence on:

- closer mirrored openings being worse on average
- smaller fleets being worse on average
- lower / squarer aspect ratios being somewhat worse on average

Representative means:

- `origin 10 -> fc_t1_20 = 0.1283`
- `origin 90 -> fc_t1_20 = 0.1727`

- `size 50 -> fc_t1_20 = 0.1625`
- `size 150 -> fc_t1_20 = 0.1231`

- `aspect 1.0 -> fc_t1_20 = 0.1753`
- `aspect 2.5 -> fc_t1_20 = 0.1220`

Engineering reading:

- the current observer is more fragile in tighter, smaller, and squarer formations
- this is again more consistent with hard front-band / grouping sensitivity than with a specific runtime combat effect

### 7.5 Expanded-DOE implication for redesign

The expanded DOE therefore strengthens three bounded judgments:

1. the current `FrontCurv` issue is systematic rather than fixture-local
2. the current `top30` hard-band construction is increasingly difficult to defend as default
3. a smoother redesign direction remains more plausible than another hard-band variant

In other words:

- the 1125-cell DOE does **not** prove that `allweight` is correct
- but it does make the status quo harder to justify
- and it makes a smooth redesign direction more credible than continued reliance on a hard `top30` split

## 8. Current engineering judgment

If the goal is:

- one observer shape that behaves less badly across both regimes

then the current bounded redesign reading is:

```text
allweight is the strongest balance candidate in this bounded redesign set.
```

If the goal is:

- maximize long-range mirrored pre-contact stability only

then:

```text
top10 or top20 look cleaner than allweight.
```

But that would come at too much cost in the close-contact regime.

So the current engineering reading is:

- `top10` / `top20` are phase-specialized candidates
- `allweight` is the strongest cross-regime balance candidate
- current `top30` is no longer well defended as the default construction

## 9. Boundary conclusion

This audit still does not authorize implementation.

It does justify a narrower next-step question:

- whether `FrontCurv` should move away from the current hard `top30` construction
- and whether an all-unit weighted construction is the best bounded redesign direction to study next

## 10. What this does not mean

This does **not** mean:

- `FrontCurv` is now solved
- `allweight` should be silently adopted
- the observer should be immediately rewritten
- personality or TL semantics should be reopened

This remains only a bounded observer redesign audit result.
