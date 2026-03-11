# Formation Metric Distribution Report (Phase VI Calibration, Observer-only)

## What / Why (<=20 lines)
1. This report measures formation snapshot metric distributions under the requested Phase VI case set.
2. Goal: explain Tier-2 N/A behavior via threshold-vs-distribution mismatch, without changing runtime behavior.
3. Snapshot cadence is fixed at 10 ticks; `t=0` is state-only and excluded from event/coverage stats.
4. Metrics analyzed per case+side over `t>=1`: AR, AreaScale, split_separation, angle_coverage, wedge_ratio.
5. Coverage is computed as `%ticks` satisfying current threshold conditions.
6. Threshold proposal below is documentation-only and is not applied in code.
7. Assumption: FR/MB/PD tuple is applied symmetrically to A/B in each case; non-scanned parameters are fixed at 5.0.
8. Assumption: run horizon is fixed at 300 ticks (Phase V baseline comparability setting).

## Current Implemented Thresholds

| Label | Condition |
| --- | --- |
| Split | `split_separation > 1.2` |
| Enveloping | `angle_coverage > 0.5` |
| Line | `AR > 3.0` |
| Compact | `AR < 1.5` and `AreaScale <= q30(side-local)` |
| Rectangle | `1.5 <= AR <= 3.0` and `|wedge_ratio - 1| < 0.2` |

## Threshold-vs-Distribution Comparison

- Split: mean coverage=100.00% -> **too loose**
- Enveloping: mean coverage=36.46% -> **plausible**
- Line: mean coverage=0.00% -> **too strict**
- Compact/Rectangle are shape labels; they show non-zero occupancy but are not primary Tier-2 trigger labels.

## Proposed Threshold Set (Proposal Only, Not Applied)

| Label | Current | Proposed | Rationale |
| --- | --- | --- | --- |
| Split (`split_separation`) | 1.20 | 1.715 | Pull toward pooled q75 to reduce chronic non-activation |
| Enveloping (`angle_coverage`) | 0.50 | 0.583 | Align with observed upper-mid distribution |
| Line (`AR`) | 3.00 | 2.200 | Reduce strictness while preserving high-elongation semantics |
| Compact (`AreaScale` quantile) | q30 | q35 | Minor relaxation for diagnostic occupancy |
| Rectangle (`|wedge_ratio-1|`) | <0.20 | <0.25 | Minor tolerance widening |

## Expected Effect

- Estimated case-level Tier-2 (Split/Enveloping/Line) trigger presence under proposal: **100.0%** of runs.
- This estimate is analytical-only and does not imply detector activation until governance-approved implementation.
