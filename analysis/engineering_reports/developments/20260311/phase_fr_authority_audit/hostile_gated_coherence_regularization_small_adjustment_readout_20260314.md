# Hostile-Gated Coherence Regularization Small Adjustment Readout

Date: 2026-03-14  
Status: Engineering readout  
Scope: Very small paired validation only. No baseline implications.

## 1. Purpose

This note records the first very small adjustment round for `hostile_gated_coherence_regularization_v1`.

Comparison set:

- `off`
- `hybrid_v2_r125_d035_p020`
- `gated_reg_v1` at:
  - `1.0 / 1.0`
  - `1.25 / 1.0`
  - `1.5 / 1.0`
  - `1.5 / 0.75`

Fixtures:

- `exception_2to1_close`
- `neutral_close`
- `neutral_long`

## 2. Main Readout

The new family remains mechanically more stable than the failed co-resolution line:

- no self-shattering in `neutral_long`
- no autonomous same-fleet tearing without hostile pressure

The current best point from this small round is:

```text
hostile_gated_coherence_regularization_v1
scale = 1.5
strength = 0.75
```

## 3. Why This Point Was Chosen

`1.5 / 0.75` gave the best current tradeoff among the tested gated points:

- `exception_2to1_close`
  - `cov21_50 = 0.143`
- `neutral_close`
  - `cov21_50 = 0.163`
  - `fc21_50 = 0.189`
- `neutral_long`
  - preserved single connected component per fleet

So this point is the best current animation candidate inside the new family.

## 4. Current Limitation

This point is still not a credible spacing-floor-style answer.

Its main unresolved problem is:

- same-fleet minimum distance remains far below `min_unit_spacing = 2.0`

Examples:

- `exception_2to1_close`
  - `mean_same_a_min_20_50 = 0.365`
  - `mean_same_b_min_20_50 = 0.410`
- `neutral_close`
  - `mean_same_a_min_20_50 = 0.546`
  - `mean_same_b_min_20_50 = 0.513`

So the family has improved framing and mechanical stability, but not yet same-layer spacing-floor adequacy.

## 5. One-Line Conclusion

```text
the best current gated-regularization point is 1.5 / 0.75, and it is suitable for direct visual inspection, but it still does not establish a credible same-layer spacing floor because same-fleet distances remain far below min_unit_spacing.
```
