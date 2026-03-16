# Hostile Spacing and Coherence Co-Resolution v1 Failure Note

Date: 2026-03-14  
Status: Engineering note  
Scope: Bounded prototype readout only. No implementation authorization.

## 1. Purpose

This note records the failure of the first `hostile_spacing_and_coherence` co-resolution prototype.

This is not:

- a baseline proposal
- a governance directive
- a request to reopen DOE

## 2. Main Finding

`hostile_spacing_co_resolution_v1` failed the first prototype test.

The failure is not "insufficient improvement."  
It is a more basic mechanical failure:

```text
the prototype introduced same-fleet instability even when hostile overlap was absent or low
```

## 3. Key Evidence

The clearest evidence came from `neutral_long`.

- `cov21_50 = 0.0`
- yet the prototype still produced:
  - `a_components_20_50 = 4.32`
  - `b_components_20_50 = 5.26`
  - `mean_same_a_min_20_50 = 0.032`
  - `mean_same_b_min_20_50 = 0.026`

So even without hostile overlap pressure in that window, the prototype was already tearing same-fleet geometry apart and collapsing spacing far below `min_unit_spacing = 2.0`.

This is enough to classify the first point as a failed attempt.

## 4. Mechanism Interpretation

The likely mechanism error is:

- same-fleet spacing/coherence was added as an additional local correction source
- not merely as a bounded guard on hostile-side correction

That means the prototype allowed same-fleet pair terms to become an active destabilizing force of their own.

So instead of:

```text
hostile-driven correction regularized by local coherence
```

the first prototype behaved more like:

```text
hostile correction plus a second independent same-fleet correction field
```

That is why it could shatter fleets even when hostile overlap did not justify it.

## 5. Current Engineering Judgment

The correct reading is:

- co-resolution as a direction is not disproven
- this first implementation form is disproven
- parameter tuning is not the right next step

The first prototype failed because the same-fleet side of the correction was structurally too autonomous.

## 6. One-Line Conclusion

```text
hostile_spacing_co_resolution_v1 should be treated as a failed first attempt, because it allowed same-fleet coherence correction to become an independent destabilizing source, producing fleet tearing and spacing collapse even outside meaningful hostile-overlap pressure.
```
