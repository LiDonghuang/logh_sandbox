# Movement v3a Baseline Evaluation Report

## Scope
- Candidate: `movement_model=v3a`, `movement_v3a_experiment=exp_precontact_centroid_probe`, `centroid_probe_scale=0.5`, `bridge_theta_split=1.7`, `bridge_theta_env=0.5`
- Grid: FR x MB x PD = 3 x 3 x 3, opponents = first six canonical archetypes, models = v1/v3a
- Total runs: 324
- Yang not used

## Runtime Alignment
- Source settings: `analysis/test_run_v1_0.settings.json`
- DOE overrides only: `boundary_enabled=false`, `boundary_soft_strength=1.0`, `boundary_hard_enabled=false`, `runtime_decision_source_effective=v2`
- Fixed paired seeds: random=`1981813971`, background=`897304369`, metatype=`3095987153`

## Standards Compliance
- Standards version: `DOE_Report_Standard_v1.0 / BRF_Export_Standard_v1.0`
- Script version: `movement_v3a_baseline_evaluation_v1`
- Deviations: none

## Determinism Check
| model | rep1 | rep2 | pass |
| --- | --- | --- | --- |
| v1 | `1e9b4cc71610d35b21874c405489ca53fef0cb395f24d0840ce1f70b904e0f94` | `1e9b4cc71610d35b21874c405489ca53fef0cb395f24d0840ce1f70b904e0f94` | True |
| v3a | `f1936dad5cc2d15b478a8174fc228b616f57059c985bf8a4a76e5543332ce07b` | `f1936dad5cc2d15b478a8174fc228b616f57059c985bf8a4a76e5543332ce07b` | True |

## Overall Comparison
| metric | v1 | v3a | delta |
| --- | ---: | ---: | ---: |
| precontact_persistent_outlier_p90_mean | 3.7309 | 0.0062 | -3.7247 |
| precontact_max_persistence_max_mean | 42.4568 | 0.4815 | -41.9753 |
| precontact_wedge_p10_A_mean | 0.7755 | 1.0250 | 0.2496 |
| precontact_ar_p90_A_mean | 2.1842 | 2.1702 | -0.0140 |
| precontact_split_p90_A_mean | 1.8538 | 1.7192 | -0.1346 |
| first_contact_tick_mean | 106.7593 | 110.5432 | 3.7840 |
| cut_exists_rate | 1.0000 | 1.0000 | 0.0000 |
| pocket_exists_rate | 1.0000 | 1.0000 | 0.0000 |

## Cell-Level Main Effects
| FR | MB | PD | d_outlier | d_persist | d_wedge | d_AR | d_split | d_contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 2 | 2 | -1.0000 | -23.6667 | 0.0230 | 0.0495 | 0.0093 | 2.3333 |
| 2 | 2 | 5 | -0.8333 | -23.3333 | 0.0263 | 0.0177 | 0.0033 | 1.5000 |
| 2 | 2 | 8 | -0.6667 | -22.3333 | 0.0096 | 0.0128 | 0.0030 | 1.8333 |
| 2 | 5 | 2 | -0.8333 | -24.8333 | 0.0279 | 0.0545 | 0.0069 | 2.5000 |
| 2 | 5 | 5 | -0.8333 | -22.3333 | -0.0305 | 0.0095 | 0.0016 | 1.5000 |
| 2 | 5 | 8 | -0.8500 | -22.6667 | -0.0210 | 0.0089 | 0.0040 | 1.8333 |
| 2 | 8 | 2 | -1.1667 | -24.6667 | 0.0473 | 0.0472 | 0.0043 | 2.3333 |
| 2 | 8 | 5 | -0.6667 | -21.8333 | -0.0140 | 0.0305 | 0.0074 | 1.8333 |
| 2 | 8 | 8 | -0.8333 | -23.3333 | -0.0108 | 0.0217 | 0.0084 | 1.5000 |
| 5 | 2 | 2 | -5.8333 | -50.6667 | 0.5298 | 0.0276 | -0.0158 | 5.3333 |
| 5 | 2 | 5 | -2.1833 | -32.5000 | 0.3641 | 0.1750 | -0.0134 | 4.5000 |
| 5 | 2 | 8 | -1.6667 | -29.6667 | 0.3288 | 0.1649 | -0.0153 | 4.1667 |
| 5 | 5 | 2 | -6.6667 | -52.3333 | 0.5034 | 0.1132 | -0.0871 | 5.1667 |
| 5 | 5 | 5 | -2.3500 | -35.5000 | 0.4352 | 0.1823 | -0.0185 | 4.5000 |
| 5 | 5 | 8 | -1.7000 | -30.8333 | 0.3494 | 0.1712 | -0.0181 | 4.3333 |
| 5 | 8 | 2 | -6.8333 | -57.3333 | 0.4570 | 0.1775 | -0.2510 | 4.5000 |
| 5 | 8 | 5 | -3.1667 | -38.5000 | 0.4991 | 0.2054 | -0.0412 | 3.8333 |
| 5 | 8 | 8 | -2.1833 | -34.6667 | 0.4334 | 0.1785 | -0.0259 | 3.5000 |
| 8 | 2 | 2 | -7.8333 | -74.3333 | 0.2596 | -0.6323 | -0.6629 | 6.3333 |
| 8 | 2 | 5 | -5.6667 | -54.3333 | 0.4607 | -0.1830 | -0.0231 | 4.1667 |
| 8 | 2 | 8 | -5.3333 | -50.3333 | 0.4528 | -0.0673 | -0.0148 | 3.8333 |
| 8 | 5 | 2 | -7.9000 | -71.6667 | 0.2076 | -0.5277 | -0.9687 | 6.0000 |
| 8 | 5 | 5 | -6.3333 | -62.1667 | 0.3041 | -0.1275 | -0.0220 | 5.0000 |
| 8 | 5 | 8 | -6.5000 | -57.0000 | 0.3063 | -0.0562 | -0.0159 | 3.6667 |
| 8 | 8 | 2 | -6.8667 | -68.1667 | 0.1526 | -0.4569 | -1.3667 | 7.6667 |
| 8 | 8 | 5 | -7.0333 | -64.5000 | 0.3282 | -0.0103 | -0.0919 | 4.6667 |
| 8 | 8 | 8 | -6.8333 | -59.8333 | 0.3080 | 0.0349 | -0.0311 | 3.8333 |

## Factor Main-Effect Check
| factor | v1 variation | v3a variation |
| --- | --- | --- |
| FR | True | True |
| MB | True | True |
| PD | True | True |

## Opponent Hardness
| opponent | v1 win_rate_A | v3a win_rate_A | v1 median_end_tick | v3a median_end_tick |
| --- | ---: | ---: | ---: | ---: |
| bittenfeld | 0.4815 | 0.6667 | 457.0000 | 469.0000 |
| kircheis | 0.7407 | 0.6667 | 451.0000 | 463.0000 |
| mittermeyer | 0.5926 | 0.5556 | 448.0000 | 447.0000 |
| muller | 0.7037 | 0.7778 | 461.0000 | 454.0000 |
| reinhard | 0.5556 | 0.5185 | 445.0000 | 462.0000 |
| reuenthal | 0.2222 | 0.1852 | 467.0000 | 459.0000 |

## Mirror / Jitter Watch
| metric | v1 | v3a | delta |
| --- | ---: | ---: | ---: |
| mirror_ar_gap_mean | 0.2058 | 0.0849 | -0.1209 |
| mirror_wedge_gap_mean | 0.2195 | 0.2017 | -0.0178 |
| jitter_ar_A_mean | 0.0183 | 0.0096 | -0.0087 |
| jitter_wedge_A_mean | 0.0217 | 0.0158 | -0.0059 |

## Censoring / Cap Sensitivity
- Runtime cap hits: v1=`0`, v3a=`0`
- Effective runtime policy: `max_time_steps=-1`, terminate 10 ticks after elimination, hard cap 999

## Recommendation
- RECOMMEND V3A FOR BASELINE REPLACEMENT GATE