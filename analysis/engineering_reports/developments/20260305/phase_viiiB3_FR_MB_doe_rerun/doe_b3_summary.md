# DOE B3 Summary - FR/MB Corrected Re-run

## Standards Compliance
- Standards version: `DOE_Report_Standard_v1.0 + BRF_Export_Standard_v1.0`
- Stats script: `doe_postprocess.py v1.0.0`
- Deviations: `No deviations`

## 1. Cell-level Main Effects
| Cell | n | A win rate (%) | Mean survivors A | Mean survivors B | Median end_tick | Mean Cut_T | Mean Pocket_T | Delta end (v3a-v1) | Delta Cut_T (v3a-v1) | Delta Pocket_T (v3a-v1) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| FR2_MB2_PD5 | 12 | 91.7 | 25 | 2.167 | 432 | 143.833 | 165.250 | 13 | 1 | -24.833 |
| FR2_MB5_PD5 | 12 | 75 | 17.083 | 5.583 | 436.500 | 157.750 | 159.833 | 34.167 | -7.167 | 7.333 |
| FR2_MB8_PD5 | 12 | 50 | 10.833 | 7.167 | 445.500 | 152.500 | 167.083 | -26 | 21.667 | -6.500 |
| FR5_MB2_PD5 | 12 | 58.3 | 7.083 | 5.667 | 471.500 | 187.417 | 177 | -68.500 | 44.500 | 14 |
| FR5_MB5_PD5 | 12 | 33.3 | 3.583 | 12.333 | 446.500 | 152.583 | 181.167 | 7.833 | 49.500 | 28.333 |
| FR5_MB8_PD5 | 12 | 58.3 | 5.667 | 6.167 | 507 | 181.167 | 183.667 | -1.333 | 107.667 | 8.667 |
| FR8_MB2_PD5 | 12 | 41.7 | 6.750 | 5.833 | 453 | 147.250 | 176.833 | -6 | -48.500 | 9.667 |
| FR8_MB5_PD5 | 12 | 33.3 | 5.750 | 9.167 | 475 | 143.417 | 179 | 43 | -36.833 | 14.333 |
| FR8_MB8_PD5 | 12 | 16.7 | 2.583 | 14.083 | 437.500 | 150.917 | 179.167 | 19 | -52.833 | -15.333 |

## 2. Factor Main-Effect Check
### FR
| Level | n | A win rate (%) | Mean survivors A | Median end_tick | Mean Cut_T | Mean Pocket_T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 36 | 72.2 | 17.639 | 436.500 | 151.361 | 164.056 |
| 5 | 36 | 50 | 5.444 | 470.500 | 173.722 | 180.611 |
| 8 | 36 | 30.6 | 5.028 | 453 | 147.194 | 178.333 |
- No observable main effect metrics: `none`
- Duplication pattern detected across FR levels: `False`

### MB
| Level | n | A win rate (%) | Mean survivors A | Median end_tick | Mean Cut_T | Mean Pocket_T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 36 | 63.9 | 12.944 | 442 | 159.500 | 173.028 |
| 5 | 36 | 47.2 | 8.806 | 449.500 | 151.250 | 173.333 |
| 8 | 36 | 41.7 | 6.361 | 448 | 161.528 | 176.639 |
- No observable main effect metrics: `none`
- Duplication pattern detected across MB levels: `False`

### PD
- Status: not testable (single level: 5).

## 3. Opponent Hardness Table
| Opponent | n | A win rate all (%) | A win rate v1 (%) | A win rate v3a (%) | Median end_tick | Mean survivors A | Mean survivors B |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| muller | 18 | 38.9 | 66.7 | 11.1 | 444.500 | 5.056 | 11.056 |
| bittenfeld | 18 | 44.4 | 44.4 | 44.4 | 455.500 | 10.167 | 6.333 |
| reinhard | 18 | 50 | 44.4 | 55.6 | 470.500 | 8.944 | 5.222 |
| reuenthal | 18 | 50 | 33.3 | 66.7 | 442.500 | 7.389 | 11.611 |
| kircheis | 18 | 55.6 | 77.8 | 33.3 | 434.500 | 10.278 | 6.667 |
| mittermeyer | 18 | 66.7 | 44.4 | 88.9 | 441 | 14.389 | 4.556 |

## 4. Censoring/Cap Sensitivity Note
- Observed max end_tick: `682`
- Runs at observed max end_tick: `1/108` (`0.9%`)
- Duration metrics low sensitivity: `True`
- Recommendation: prioritize event-time metrics (contact/kill/cut/pocket) over duration-only comparisons.

## 5. Governance Brief (B3, FR/MB Corrected)
- Scope: B3 rerun uses strict naming and injection discipline (`FR = formation_rigidity`, `FCR = force_concentration_ratio`), with hard preflight assertions and abort-on-fail.
- Preflight status: `108/108` runs passed all four assertions; no FR/FCR label collision found in B3 run-table schema.
- FR main effect (overall): A-side win rate drops with FR increase (`FR2: 72.2%`, `FR5: 50.0%`, `FR8: 30.6%`), indicating a strong first-order effect under this DOE design.
- FR x MB interaction: effect is not purely monotonic at every MB slice. Example from aggregated cells:
  - MB=2: FR2 `91.7%` -> FR5 `58.3%` -> FR8 `41.7%`
  - MB=5: FR2 `75.0%` -> FR5 `33.3%` -> FR8 `33.3%`
  - MB=8: FR2 `50.0%` -> FR5 `58.3%` -> FR8 `16.7%`
  This non-uniform slope confirms interaction between FR and MB (and model split), not a single-axis linear response.
- Movement-model caveat: interaction shape differs by model (`v1` vs `v3a`), so governance decisions should be based on paired deltas plus per-model slices, not pooled means only.
- Censoring caveat: duration metrics remain low-sensitivity for this batch flag; event-time metrics should remain primary for conclusions.
