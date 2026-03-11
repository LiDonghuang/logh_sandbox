# Movement Pre-contact Explore Summary

## Scope
- FR fixed 8, MB in {2,5,8}, opponents=first six archetypes.
- Models: v3a baseline vs v3b1/v3b2/v3b3/v3b4/v3b5.
- Total runs: 108 (3 cells x 6 opponents x 6 models).
- Runtime decision source fixed: `v2`.

## Mean Delta vs v3a
- v3b1:
  - delta precontact_ar_p90_A: 0.1558
  - delta precontact_ar_max_A: 0.1747
  - delta precontact_wedge_p10_A: -0.0062
  - delta overall_ar_p90_A: 0.0503
  - delta end_tick: -25.1111
- v3b2:
  - delta precontact_ar_p90_A: 0.0512
  - delta precontact_ar_max_A: 0.0280
  - delta precontact_wedge_p10_A: -0.0155
  - delta overall_ar_p90_A: -0.0218
  - delta end_tick: -28.7778
- v3b3:
  - delta precontact_ar_p90_A: 0.0217
  - delta precontact_ar_max_A: -0.0025
  - delta precontact_wedge_p10_A: -0.0098
  - delta overall_ar_p90_A: -0.0423
  - delta end_tick: -24.3333
- v3b4:
  - delta precontact_ar_p90_A: -0.0855
  - delta precontact_ar_max_A: -0.0766
  - delta precontact_wedge_p10_A: -0.0069
  - delta overall_ar_p90_A: -0.0455
  - delta end_tick: 2.0556
- v3b5:
  - delta precontact_ar_p90_A: -0.1603
  - delta precontact_ar_max_A: -0.0766
  - delta precontact_wedge_p10_A: 0.0106
  - delta overall_ar_p90_A: -0.1320
  - delta end_tick: -33.8333

## Artifacts
- movement_precontact_explore_run_table.csv
- movement_precontact_explore_delta_table.csv
- movement_precontact_explore_model_summary.csv
- movement_precontact_explore_determinism_check.md