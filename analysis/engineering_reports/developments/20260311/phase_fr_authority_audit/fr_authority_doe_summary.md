# FR Authority DOE Summary - Controlled Isolation Baseline

## Standards Compliance
- Standards version: `DOE_Report_Standard_v1.0 + BRF_Export_Standard_v1.0`
- Stats script: `doe_postprocess.py v1.0.0`
- Deviations: `ODW is retained only as a support split; time-resolved alive trajectories are stored in a companion CSV.`

## 1. Cell-level Main Effects
| Cell | n | A win rate (%) | Mean survivors A | Mean survivors B | Median end_tick | Mean Cut_T | Mean Pocket_T | Delta end (v3a-v1) | Delta Cut_T (v3a-v1) | Delta Pocket_T (v3a-v1) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| FR2_MB2_PD2 | 36 | 50 | 4 | 5.500 | 492 | 131.500 | 137 | N/A | N/A | N/A |
| FR2_MB2_PD5 | 36 | 50 | 2 | 7.500 | 505.500 | 131.500 | 137 | N/A | N/A | N/A |
| FR2_MB2_PD8 | 36 | 100 | 11 | 0 | 493.500 | 132 | 136.500 | N/A | N/A | N/A |
| FR2_MB5_PD2 | 36 | 0 | 0 | 9.500 | 499 | 133 | 137.500 | N/A | N/A | N/A |
| FR2_MB5_PD5 | 36 | 0 | 0 | 7.500 | 524.500 | 133 | 137.500 | N/A | N/A | N/A |
| FR2_MB5_PD8 | 36 | 0 | 0 | 18 | 435 | 131.500 | 137 | N/A | N/A | N/A |
| FR2_MB8_PD2 | 36 | 0 | 0 | 20.500 | 441 | 131.500 | 145 | N/A | N/A | N/A |
| FR2_MB8_PD5 | 36 | 0 | 0 | 19.500 | 453 | 131.500 | 145 | N/A | N/A | N/A |
| FR2_MB8_PD8 | 36 | 0 | 0 | 20.500 | 446 | 144 | 137 | N/A | N/A | N/A |
| FR5_MB2_PD2 | 36 | 50 | 13.500 | 12 | 434.500 | 129 | 135 | N/A | N/A | N/A |
| FR5_MB2_PD5 | 36 | 0 | 0 | 12 | 508.500 | 129 | 135 | N/A | N/A | N/A |
| FR5_MB2_PD8 | 36 | 0 | 0 | 25 | 446.500 | 129.500 | 135 | N/A | N/A | N/A |
| FR5_MB5_PD2 | 36 | 50 | 4.500 | 5 | 521.500 | 129 | 137 | N/A | N/A | N/A |
| FR5_MB5_PD5 | 36 | 50 | 10.500 | 1.500 | 524.500 | 129 | 137 | N/A | N/A | N/A |
| FR5_MB5_PD8 | 36 | 0 | 0 | 11.500 | 533.500 | 129.500 | 135.500 | N/A | N/A | N/A |
| FR5_MB8_PD2 | 36 | 50 | 6 | 13 | 463 | 129.500 | 137 | N/A | N/A | N/A |
| FR5_MB8_PD5 | 36 | 0 | 0 | 13.500 | 495 | 129.500 | 137 | N/A | N/A | N/A |
| FR5_MB8_PD8 | 36 | 0 | 0 | 11 | 518 | 129.500 | 136.500 | N/A | N/A | N/A |
| FR8_MB2_PD2 | 36 | 100 | 27 | 0 | 411 | 128 | 136 | N/A | N/A | N/A |
| FR8_MB2_PD5 | 36 | 100 | 13 | 0 | 505 | 128 | 136 | N/A | N/A | N/A |
| FR8_MB2_PD8 | 36 | 100 | 12.500 | 0 | 495 | 128 | 139 | N/A | N/A | N/A |
| FR8_MB5_PD2 | 36 | 100 | 28 | 0 | 396.500 | 127.500 | 135.500 | N/A | N/A | N/A |
| FR8_MB5_PD5 | 36 | 100 | 13 | 0 | 471.500 | 127.500 | 135.500 | N/A | N/A | N/A |
| FR8_MB5_PD8 | 36 | 50 | 7 | 6 | 482 | 128 | 139 | N/A | N/A | N/A |
| FR8_MB8_PD2 | 36 | 50 | 10 | 1 | 514 | 128 | 137.500 | N/A | N/A | N/A |
| FR8_MB8_PD5 | 36 | 100 | 22.500 | 0 | 415.500 | 128 | 137.500 | N/A | N/A | N/A |
| FR8_MB8_PD8 | 36 | 100 | 16.500 | 0 | 450.500 | 128 | 143 | N/A | N/A | N/A |

## 2. Factor Main-Effect Check
### FR
| Level | n | A win rate (%) | Mean survivors A | Median end_tick | Mean Cut_T | Mean Pocket_T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 324 | 22.2 | 1.889 | 465.500 | 133.278 | 138.833 |
| 5 | 324 | 22.2 | 3.833 | 487.500 | 129.278 | 136.111 |
| 8 | 324 | 88.9 | 16.611 | 435.500 | 127.889 | 137.667 |
- No observable main effect metrics: `none`
- Duplication pattern detected across FR levels: `False`

### MB
| Level | n | A win rate (%) | Mean survivors A | Median end_tick | Mean Cut_T | Mean Pocket_T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 324 | 61.1 | 9.222 | 467 | 129.611 | 136.278 |
| 5 | 324 | 38.9 | 7 | 485.500 | 129.778 | 136.833 |
| 8 | 324 | 33.3 | 6.111 | 446 | 131.056 | 139.500 |
- No observable main effect metrics: `none`
- Duplication pattern detected across MB levels: `False`

### PD
| Level | n | A win rate (%) | Mean survivors A | Median end_tick | Mean Cut_T | Mean Pocket_T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 324 | 50 | 10.333 | 455 | 129.667 | 137.500 |
| 5 | 324 | 44.4 | 6.778 | 487.500 | 129.667 | 137.500 |
| 8 | 324 | 38.9 | 5.222 | 466.500 | 131.111 | 137.611 |
- No observable main effect metrics: `none`
- Duplication pattern detected across PD levels: `False`

## 3. Opponent Hardness Table
| Opponent | n | A win rate all (%) | A win rate v1 (%) | A win rate v3a (%) | Median end_tick | Mean survivors A | Mean survivors B |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| controlled_baseline_B | 972 | 44.4 | N/A | 44.4 | 471.500 | 7.444 | 8.148 |

## 4. Censoring/Cap Sensitivity Note
- Observed max end_tick: `638`
- Runs at observed max end_tick: `18/972` (`1.9%`)
- Duration metrics low sensitivity: `True`
- Recommendation: prioritize event-time metrics (contact/kill/cut/pocket) over duration-only comparisons.

## 5. Interpretable Readout Addendum
- Variable side is `A`; opponent `B` is the controlled isolation baseline.
- Time-resolved alive-unit trajectories are stored separately in `fr_authority_doe_alive_trajectory.csv`.
- Readout emphasis follows governance: `outcome + time-resolved battle trajectory`, not outcome alone.
- Coherent A-side penetration wedges observed: `0` runs.

### FR Readout
- FR=2: A win rate=`22.2%`, WedgePresent rate=`0.0%`, StructuralFragility rate=`66.7%`, PostureCoherence rate=`0.0%`, mean `first_major_divergence_tick`=`212.3`, mean `fire_eff_contact_to_cut_A`=`0.4993`
- FR=5: A win rate=`22.2%`, WedgePresent rate=`27.8%`, StructuralFragility rate=`83.3%`, PostureCoherence rate=`0.0%`, mean `first_major_divergence_tick`=`148.1`, mean `fire_eff_contact_to_cut_A`=`0.3061`
- FR=8: A win rate=`88.9%`, WedgePresent rate=`88.9%`, StructuralFragility rate=`50.0%`, PostureCoherence rate=`0.0%`, mean `first_major_divergence_tick`=`188.2`, mean `fire_eff_contact_to_cut_A`=`0.2527`

### ODW Support Split
- ODW=2: A win rate=`40.7%`, WedgePresent rate=`25.9%`, StructuralFragility rate=`88.9%`, PostureCoherence rate=`0.0%`, mean `runtime_c_conn_A`=`0.8172`
- ODW=8: A win rate=`48.1%`, WedgePresent rate=`51.9%`, StructuralFragility rate=`44.4%`, PostureCoherence rate=`0.0%`, mean `runtime_c_conn_A`=`0.9036`

### FR x ODW Interaction Focus
- FR=2: `ODW 2 -> 8` changes A-side WedgePresent rate from `0.0%` to `0.0%`, StructuralFragility rate from `66.7%` to `66.7%`, PostureCoherence rate from `0.0%` to `0.0%`, mean `first_major_divergence_tick` from `175.2` to `245.2`
- FR=5: `ODW 2 -> 8` changes A-side WedgePresent rate from `0.0%` to `55.6%`, StructuralFragility rate from `100.0%` to `66.7%`, PostureCoherence rate from `0.0%` to `0.0%`, mean `first_major_divergence_tick` from `147.1` to `149.1`
- FR=8: `ODW 2 -> 8` changes A-side WedgePresent rate from `77.8%` to `100.0%`, StructuralFragility rate from `100.0%` to `0.0%`, PostureCoherence rate from `0.0%` to `0.0%`, mean `first_major_divergence_tick` from `172.8` to `203.6`
