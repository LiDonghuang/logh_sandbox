# DOE B2 Summary - Controlled Cell Persona Override

> [VOID NOTICE - 2026-03-05]
> Status: VOID (do not use for governance/runtime decisions).
> Reason: FR/FCR mapping error in DOE injection.
> `cell_FR` was injected as `force_concentration_ratio` (FCR) instead of canonical `formation_rigidity` (FR).
> Impact: FR-related conclusions in this document are invalid.

## Standards Compliance
- Standards version: `DOE_Report_Standard_v1.0 + BRF_Export_Standard_v1.0`
- Stats script: `doe_postprocess.py v1.0.0`
- Deviations: `No deviations`

## 1. Cell-level Main Effects
| Cell | n | A win rate (%) | Mean survivors A | Mean survivors B | Median end_tick | Mean Cut_T | Mean Pocket_T | Delta end (v3a-v1) | Delta Cut_T (v3a-v1) | Delta Pocket_T (v3a-v1) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| FR2_MB2_PD5 | 12 | 75 | 31.250 | 26.333 | 300 | 139.818 | 193.667 | 0 | -28.200 | -18.333 |
| FR2_MB5_PD5 | 12 | 50 | 28.750 | 28.417 | 300 | 138.364 | 186.833 | 0 | -27.200 | 14.333 |
| FR2_MB8_PD5 | 12 | 25 | 26.917 | 29.833 | 300 | 128.750 | 187.667 | 0 | 4.833 | -2.667 |
| FR5_MB2_PD5 | 12 | 75 | 31.250 | 26.333 | 300 | 139.818 | 193.667 | 0 | -28.200 | -18.333 |
| FR5_MB5_PD5 | 12 | 50 | 28.750 | 28.417 | 300 | 138.364 | 186.833 | 0 | -27.200 | 14.333 |
| FR5_MB8_PD5 | 12 | 25 | 26.917 | 29.833 | 300 | 128.750 | 187.667 | 0 | 4.833 | -2.667 |
| FR8_MB2_PD5 | 12 | 75 | 31.250 | 26.333 | 300 | 139.818 | 193.667 | 0 | -28.200 | -18.333 |
| FR8_MB5_PD5 | 12 | 50 | 28.750 | 28.417 | 300 | 138.364 | 186.833 | 0 | -27.200 | 14.333 |
| FR8_MB8_PD5 | 12 | 25 | 26.917 | 29.833 | 300 | 128.750 | 187.667 | 0 | 4.833 | -2.667 |

## 2. Factor Main-Effect Check
### FR
| Level | n | A win rate (%) | Mean survivors A | Median end_tick | Mean Cut_T | Mean Pocket_T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 36 | 50 | 28.972 | 300 | 135.441 | 189.389 |
| 5 | 36 | 50 | 28.972 | 300 | 135.441 | 189.389 |
| 8 | 36 | 50 | 28.972 | 300 | 135.441 | 189.389 |
- No observable main effect metrics: `win_rate, mean_survivors_A, median_end_tick, mean_cut_tick_T, mean_pocket_tick_T`
- Duplication pattern detected across FR levels: `True`

### MB
| Level | n | A win rate (%) | Mean survivors A | Median end_tick | Mean Cut_T | Mean Pocket_T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 36 | 75 | 31.250 | 300 | 139.818 | 193.667 |
| 5 | 36 | 50 | 28.750 | 300 | 138.364 | 186.833 |
| 8 | 36 | 25 | 26.917 | 300 | 128.750 | 187.667 |
- No observable main effect metrics: `median_end_tick`
- Duplication pattern detected across MB levels: `False`

### PD
- Status: not testable (single level: 5).

## 3. Opponent Hardness Table
| Opponent | n | A win rate all (%) | A win rate v1 (%) | A win rate v3a (%) | Median end_tick | Mean survivors A | Mean survivors B |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bittenfeld | 18 | 33.3 | 66.7 | 0 | 300 | 26.333 | 30 |
| reinhard | 18 | 33.3 | 33.3 | 33.3 | 300 | 27.667 | 28.833 |
| muller | 18 | 50 | 66.7 | 33.3 | 300 | 27 | 28.333 |
| reuenthal | 18 | 50 | 33.3 | 66.7 | 300 | 29.667 | 28 |
| kircheis | 18 | 66.7 | 66.7 | 66.7 | 300 | 31.833 | 26.167 |
| mittermeyer | 18 | 66.7 | 33.3 | 100 | 300 | 31.333 | 27.833 |

## 4. Censoring/Cap Sensitivity Note
- Observed max end_tick: `300`
- Runs at observed max end_tick: `108/108` (`100%`)
- Duration metrics low sensitivity: `True`
- Recommendation: prioritize event-time metrics (contact/kill/cut/pocket) over duration-only comparisons.
