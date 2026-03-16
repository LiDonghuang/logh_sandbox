# FrontCurv Observer Governance Report

Date: 2026-03-13
Status: Governance-facing short report
Scope: Bounded observer audit closeout for `FrontCurv`
Implementation: Not requested

## 1. Summary judgment

Engineering recommends treating current `FrontCurv` as an observer under redesign pressure.

The current evidence does **not** support reading the issue as:

- a broad personality-mechanism effect
- an attack-range effect
- a mirrored outcome / winner-loser effect

The evidence **does** support reading it as:

- a bounded observer-construction problem
- centered on the current hard `top30` front-band construction
- with sensitivity amplified by tighter packing, smaller fleets, and closer mirrored openings

## 2. Evidence base

This judgment is based on:

- `frontcurv_observer_audit_20260313.md`
- `frontcurv_observer_redesign_audit_20260313.md`
- `frontcurv_mirrored_distance_aspect_size_doe_20260313.csv`
- `frontcurv_mirrored_distance_aspect_size_sep_range_doe_20260313.csv`

The largest reinforcement comes from the expanded mirrored DOE:

- `1125` cells
- same-force
- same all-5 personalities
- mirrored geometry
- `nearest5_centroid` pre-TL substrate

## 3. High-signal findings

### A. The mismatch is systematic

Across the `1125`-cell mirrored DOE:

- `mean frontcurve_diff_t1_20 = 0.1444`
- `mean frontcurve_diff_t21_50 = 0.2303`
- `mean frontcurve_diff_t51_120 = 0.3849`

This means the issue is not fixture-local.

### B. The issue remains observer-dominant, not battle-outcome-dominant

In the same DOE:

- `mean cws_diff_t1_20 = 0.0086`
- `mean remaining_gap_pct_initial = 1.2997`

So `FrontCurv` asymmetry is much larger than broader mirrored battle-outcome asymmetry.

### C. `min_separation` is the strongest new physical amplifier

- `sep 1.0 -> fc_t1_20 = 0.1737`
- `sep 2.0 -> fc_t1_20 = 0.1426`
- `sep 3.0 -> fc_t1_20 = 0.1169`

This strongly suggests geometry-sampling sensitivity.

### D. `attack_range` is effectively inert for the early mismatch

- `range 3.0 -> fc_t1_20 = 0.1447`
- `range 5.0 -> fc_t1_20 = 0.1444`
- `range 7.0 -> fc_t1_20 = 0.1442`

This weakens any explanation based on early fire-range semantics.

### E. Hard `top30` is increasingly hard to defend

Bounded redesign comparison still reads as:

- `top10 / top20` are cleaner in long-range mirrored pre-contact
- but too brittle in close-contact / contact-near slices
- `allweight` is the strongest cross-regime balance candidate in the bounded redesign set

Engineering therefore judges:

```text
current hard top30 is no longer well defended as the default construction
```

## 4. Bounded engineering recommendation

Engineering does **not** request immediate implementation.

Engineering does recommend that Governance treat the next-step question as:

```text
Should FrontCurv move away from the current hard top30 construction,
with smooth all-unit weighting treated as the leading bounded redesign direction?
```

This is still an observer-only question.
It should not be reinterpreted as:

- personality-mechanism reopening
- TL reopening
- broad runtime redesign

## 5. Requested governance consideration

Engineering requests governance guidance on only two points:

1. Whether Governance agrees that current `top30` has become weak enough that it should no longer be treated as a stable default by presumption.
2. Whether `allweight` is an acceptable bounded redesign lead candidate for future observer-only comparison, without yet authorizing implementation.

## 6. Boundary statement

This report does **not** claim:

- `FrontCurv` is solved
- `allweight` is already approved
- runtime or canonical semantics should change now

It only claims:

- the current observer issue is systematic
- hard `top30` is increasingly difficult to justify
- a smooth redesign direction is now more credible than continued reliance on the current hard-band construction
