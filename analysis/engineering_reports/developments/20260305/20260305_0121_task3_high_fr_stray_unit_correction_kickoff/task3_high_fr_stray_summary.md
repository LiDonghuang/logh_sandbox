# Task3 High-FR Stray DOE Summary

> [VOID NOTICE - 2026-03-05]
> Status: VOID (do not use for governance/runtime decisions).
> Reason: FR/FCR mapping error in DOE injection.
> `cell_FR` was injected as `force_concentration_ratio` (FCR) instead of canonical `formation_rigidity` (FR).
> Impact: FR-related conclusions in this summary are invalid.

## Standards Compliance
- Standards version: `DOE_Report_Standard_v1.0 + BRF_Export_Standard_v1.0`
- Stats script: `doe_postprocess.py v1.0.0`
- Deviations: `No deviations`

## 1. Cell-level Main Effects
| Cell | n | A win rate (%) | Mean survivors A | Mean survivors B | Median end_tick | Mean Cut_T | Mean Pocket_T | Delta end (v3a-v1) | Delta Cut_T (v3a-v1) | Delta Pocket_T (v3a-v1) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| FR7_MB2_PD5 | 12 | 75 | 12.250 | 4.083 | 443.500 | 214.083 | 187 | -36.333 | 91.833 | 29.667 |
| FR7_MB5_PD5 | 12 | 50 | 6.250 | 6.417 | 458.500 | 179.667 | 180.417 | -4.833 | 108 | 2.500 |
| FR7_MB8_PD5 | 12 | 41.7 | 4.833 | 8.667 | 456 | 162.083 | 190.083 | 35.667 | 71.500 | 6.167 |
| FR8_MB2_PD5 | 12 | 75 | 12.250 | 4.083 | 443.500 | 214.083 | 187 | -36.333 | 91.833 | 29.667 |
| FR8_MB5_PD5 | 12 | 50 | 6.250 | 6.417 | 458.500 | 179.667 | 180.417 | -4.833 | 108 | 2.500 |
| FR8_MB8_PD5 | 12 | 41.7 | 4.833 | 8.667 | 456 | 162.083 | 190.083 | 35.667 | 71.500 | 6.167 |
| FR9_MB2_PD5 | 12 | 75 | 12.250 | 4.083 | 443.500 | 214.083 | 187 | -36.333 | 91.833 | 29.667 |
| FR9_MB5_PD5 | 12 | 50 | 6.250 | 6.417 | 458.500 | 179.667 | 180.417 | -4.833 | 108 | 2.500 |
| FR9_MB8_PD5 | 12 | 41.7 | 4.833 | 8.667 | 456 | 162.083 | 190.083 | 35.667 | 71.500 | 6.167 |

## 2. Factor Main-Effect Check
### FR
| Level | n | A win rate (%) | Mean survivors A | Median end_tick | Mean Cut_T | Mean Pocket_T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7 | 36 | 55.6 | 7.778 | 454 | 185.278 | 185.833 |
| 8 | 36 | 55.6 | 7.778 | 454 | 185.278 | 185.833 |
| 9 | 36 | 55.6 | 7.778 | 454 | 185.278 | 185.833 |
- No observable main effect metrics: `win_rate, mean_survivors_A, median_end_tick, mean_cut_tick_T, mean_pocket_tick_T`
- Duplication pattern detected across FR levels: `True`

### MB
| Level | n | A win rate (%) | Mean survivors A | Median end_tick | Mean Cut_T | Mean Pocket_T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 36 | 75 | 12.250 | 443.500 | 214.083 | 187 |
| 5 | 36 | 50 | 6.250 | 458.500 | 179.667 | 180.417 |
| 8 | 36 | 41.7 | 4.833 | 456 | 162.083 | 190.083 |
- No observable main effect metrics: `none`
- Duplication pattern detected across MB levels: `False`

### PD
- Status: not testable (single level: 5).

## 3. Opponent Hardness Table
| Opponent | n | A win rate all (%) | A win rate v1 (%) | A win rate v3a (%) | Median end_tick | Mean survivors A | Mean survivors B |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bittenfeld | 18 | 50 | 66.7 | 33.3 | 484 | 3.833 | 7.667 |
| kircheis | 18 | 50 | 66.7 | 33.3 | 443.500 | 8.333 | 6.500 |
| mittermeyer | 18 | 50 | 66.7 | 33.3 | 448.500 | 10.833 | 6 |
| muller | 18 | 50 | 33.3 | 66.7 | 432.500 | 6.833 | 10.167 |
| reinhard | 18 | 50 | 0 | 100 | 460.500 | 9 | 5.667 |
| reuenthal | 18 | 83.3 | 100 | 66.7 | 472 | 7.833 | 2.333 |

## 4. Censoring/Cap Sensitivity Note
- Observed max end_tick: `619`
- Runs at observed max end_tick: `3/108` (`2.8%`)
- Duration metrics low sensitivity: `True`
- Recommendation: prioritize event-time metrics (contact/kill/cut/pocket) over duration-only comparisons.

## 5. Task3 Outlier Diagnostics (Observer-Heavy)
| Model | n | Mean max_outlier_persistence_global | Mean outlier_total/tick | Mean %ticks(outlier_total>0) | Persistent-outlier first-seen rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| v1 | 54 | 82.778 | 1.444 | 57.306 | 100% |
| v3a | 54 | 68.222 | 1.415 | 32.371 | 100% |

### 5.1 Cell x Model Outlier Summary
| Cell | Model | Mean max_persist | Mean outlier/tick | Mean %ticks(outlier>0) |
| --- | --- | ---: | ---: | ---: |
| FR7_MB2_PD5 | v1 | 83.167 | 1.247 | 58.743 |
| FR7_MB2_PD5 | v3a | 60.167 | 1.308 | 34.043 |
| FR7_MB5_PD5 | v1 | 91.833 | 1.490 | 55.664 |
| FR7_MB5_PD5 | v3a | 68.833 | 1.422 | 33.173 |
| FR7_MB8_PD5 | v1 | 73.333 | 1.597 | 57.513 |
| FR7_MB8_PD5 | v3a | 75.667 | 1.515 | 29.897 |
| FR8_MB2_PD5 | v1 | 83.167 | 1.247 | 58.743 |
| FR8_MB2_PD5 | v3a | 60.167 | 1.308 | 34.043 |
| FR8_MB5_PD5 | v1 | 91.833 | 1.490 | 55.664 |
| FR8_MB5_PD5 | v3a | 68.833 | 1.422 | 33.173 |
| FR8_MB8_PD5 | v1 | 73.333 | 1.597 | 57.513 |
| FR8_MB8_PD5 | v3a | 75.667 | 1.515 | 29.897 |
| FR9_MB2_PD5 | v1 | 83.167 | 1.247 | 58.743 |
| FR9_MB2_PD5 | v3a | 60.167 | 1.308 | 34.043 |
| FR9_MB5_PD5 | v1 | 91.833 | 1.490 | 55.664 |
| FR9_MB5_PD5 | v3a | 68.833 | 1.422 | 33.173 |
| FR9_MB8_PD5 | v1 | 73.333 | 1.597 | 57.513 |
| FR9_MB8_PD5 | v3a | 75.667 | 1.515 | 29.897 |

### 5.2 Directional Delta (v3a - v1)
- delta_mean_max_outlier_persistence_global: `-14.556`
- delta_mean_outlier_total_per_tick: `-0.029`
- delta_mean_pct_ticks_outlier_total_gt0: `-24.936`

## 6. Explicit Assumptions
1. Matrix `replicates=6` under `opponent_roster=first6` is interpreted as one run against each of the first six archetypes.
2. Determinism spot-check rows (`*_DET`) are interpreted as repeated identical runs vs fixed opponent `first6[0]=reinhard` (2 repeats per model).
3. Runtime length policy follows current engine behavior for `steps=-1` (elimination+10; capped by internal safety limit).
