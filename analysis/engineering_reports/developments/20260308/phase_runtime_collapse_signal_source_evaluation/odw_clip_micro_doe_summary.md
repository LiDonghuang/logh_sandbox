# ODW Clip Micro DOE Summary

Scope:
- controlled neutral Side B (all parameters fixed at 5)
- Side A varies only `ODW in {2, 8}`
- fixed `odw_posture_bias_k = 0.5`
- vary only `odw_posture_bias_clip_delta in {0.2, 0.4, 0.6, 0.8, 1.0}`

## Table

| ODW_A | ClipDelta | first_deep_pursuit_A | pct_deep_pursuit_A | mean_enemy_collapse_signal_A | AR_p90_A | Wedge_p10_A | CenterWingGapAbs_p90_A | anomaly |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 0.2 | 210 | 7.97 | 0.2389 | 2.0435 | 0.8850 | 0.0234 | none |
| 2 | 0.4 | 211 | 8.79 | 0.2544 | 2.0275 | 0.8988 | 0.0262 | none |
| 2 | 0.6 | 211 | 8.79 | 0.2544 | 2.0275 | 0.8988 | 0.0262 | none |
| 2 | 0.8 | 211 | 8.79 | 0.2544 | 2.0275 | 0.8988 | 0.0262 | none |
| 2 | 1.0 | 211 | 8.79 | 0.2544 | 2.0275 | 0.8988 | 0.0262 | none |
| 8 | 0.2 | 242 | 25.34 | 0.3384 | 2.0213 | 0.7456 | 0.0074 | none |
| 8 | 0.4 | 265 | 14.88 | 0.3083 | 2.0249 | 0.7049 | 0.0078 | none |
| 8 | 0.6 | 265 | 14.88 | 0.3083 | 2.0249 | 0.7049 | 0.0078 | none |
| 8 | 0.8 | 265 | 14.88 | 0.3083 | 2.0249 | 0.7049 | 0.0078 | none |
| 8 | 1.0 | 265 | 14.88 | 0.3083 | 2.0249 | 0.7049 | 0.0078 | none |