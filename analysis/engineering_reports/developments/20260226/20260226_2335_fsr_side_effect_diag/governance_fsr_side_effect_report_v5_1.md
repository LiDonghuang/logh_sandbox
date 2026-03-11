# Engineering Report v1.0 - Phase V FSR Side-Effect Diagnostic

Engine Version: v5.0-alpha1  
Modified Layer: `runtime/engine_skeleton.py` (debug-only instrumentation path)  
New Debug Flags: `debug_fsr_diag_enabled`, `debug_outlier_eta`, `debug_outlier_persistence_ticks`  
Cross-Dimension Coupling: none (diagnostic readout only; no new behavior coupling)  
Backward Compatibility: yes (`debug_fsr_diag_enabled` default OFF; baseline behavior preserved)  
Determinism Confirmation: PASS (fixed-seed repeated run digest equal)  
Mirror Macro Metric: `|M(0.9,0.8) + M(0.8,0.9)| = 7`  
Jitter Count: `534` (diagnostic scenario run)

## Scenario Baseline
- `FR_A=0.9`, `FR_B=0.8`
- `FSR_ENABLED=true`, `fsr_strength=0.2`
- `seed=20260227`
- Reproducibility:
  - run1 digest: `70664c593fd354089c9d4d81992099e25449f7dae0f8a453c3a871998eff6071`
  - run2 digest: `70664c593fd354089c9d4d81992099e25449f7dae0f8a453c3a871998eff6071`
  - survivors (run1/run2): `[19,25] / [19,25]`

## Diagnostic Tables
| Item | Result |
|---|---|
| Projection spike test | `flag=true`, peak=`2.3210`, baseline=`1.4672 +/- 0.2787` |
| Collision-pairs spike test | `flag=false`, peak=`265`, baseline=`246.5652 +/- 11.0171` |
| Outlier persistence | `max_outlier_persistence=144`, `>20 ticks = true`, first outlier tick=`5`, persistent emergence tick=`24` |
| Frontline width vs fsr_strength | rows=`(0.0,12.6804),(0.1,13.5207),(0.2,16.4760),(0.3,15.8999)`; corr=`+0.8897`; monotonic_nonincreasing=`false` |
| Performance overhead (diag ON/OFF) | `6.9718s / 6.4001s = 1.0893x` (`+8.93%`) |

## Analysis Reasoning (Evidence Chain)
1. Reproduction validity is established first: same seed, same digest, same survivors.  
2. Outlier dynamics are not transient noise: first outlier appears at tick 5, persistent class appears by tick 24, and max persistence reaches 144 ticks.  
3. Temporal ordering supports a projection-side contribution: projection displacement spike test is positive before/around outlier persistence window (`flag=true`).  
4. Pair-collision surge is not the dominant trigger in this sample: collision-pairs spike test is negative (`flag=false`) under the same window criterion.  
5. Frontline-width collapse is not supported by current sample: width does not decrease with higher `fsr_strength`; observed relation is positive and non-monotonic.  
6. Therefore, in this scenario, persistent outliers correlate more strongly with projection displacement spikes than with pair-count surges or frontline collapse.  
7. Constraints check: instrumentation is debug-only, OFF by default, no combat/targeting/movement-objective change, no stochastic branch introduced.  
8. Runtime overhead with diagnostics stays within Governance cap (`+8.93% < +10%`).

## Required Q1-Q4 Answers
1. Does `max_projection_displacement` spike prior to outlier formation?  
Yes (detected by threshold test, `flag=true`).

2. Does `collision_pairs_count` increase sharply during ejection?  
No (same criterion returns `flag=false`).

3. Is outlier persistence multi-tick (>20 ticks) or transient?  
Multi-tick (`max_outlier_persistence=144`).

4. Is frontline width collapse correlated with `fsr_strength` magnitude?  
Not in this sample (no collapse pattern; positive/non-monotonic relation).

## Conditional Next Step (Proposal Only, Not Implemented)
- Candidate for Governance review: single-tick projection displacement clamp (per-unit bounded projection displacement).
- Implementation remains blocked until Governance approval.

## Attachments
- Time-series samples: `fsr_side_effect_timeseries_sample.csv`
- Snapshot (early): `fsr_side_effect_frame_early.png`
- Snapshot (mid): `fsr_side_effect_frame_mid.png`
- Snapshot (late): `fsr_side_effect_frame_late.png`
- Structured summary: `fsr_side_effect_diag_summary_v5_1.json`

## Short Interpretation (<=15 lines)
1. Fixed-seed reproduction passes; diagnostics are deterministic.  
2. Persistent outlier behavior is confirmed and not a short-lived fluctuation.  
3. Projection displacement spike appears as the strongest correlated precursor in this run.  
4. Collision pair count does not show a matching sharp surge under the same criterion.  
5. Frontline width does not exhibit collapse with higher `fsr_strength` in this scenario.  
6. Debug path remains behavior-safe when OFF and performance stays within the +10% budget.  
