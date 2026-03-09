# Runtime Collapse Source Replacement Confirmation

Engine Version: v5.0-alpha5
Modified Layer: Runtime collapse-signal source only
Affected Parameters: runtime decision source (`v2` vs `v3_test @ 1.1`)
New Variables Introduced: None
Cross-Dimension Coupling: None beyond previously approved `v3_connect_radius_multiplier = 1.1` freeze
Mapping Impact: None
Governance Impact: Replacement confirmation only
Backward Compatibility: `v2` retained as legacy reference

Summary
- Confirmation batch scope: 9 Side-A cells (`FR x MB`, `PD=5`) x 3 canonical opponents x 2 paired seed profiles x 2 sources = 108 runs.
- Frozen context preserved: movement baseline `v3a`, `exp_precontact_centroid_probe`, `centroid_probe_scale=0.5`, bridge thresholds `1.7 / 0.5`, physical spacing unchanged.
- Opponents used: `mittermeyer, muller, reinhard`.
- `v3_test` confirmation freeze: `v3_connect_radius_multiplier = 1.1`.
- Determinism preserved: `v2=True`, `v3_test@1.1=True`.
- Old early-saturation failure avoided: `True`.
- Event integrity counts: candidate `v3_test @ 1.1` has missing_cut=`0`, pocket_without_cut=`0`, event_order_anomaly=`0`; legacy `v2` anomalies=`14`.
- Collapse-signal jitter mean delta (`v3_test - v2`): A=`0.0378`, B=`0.0345`.
- Final recommendation: **ACCEPT**.

## Runtime-Path
| source | n_runs | first_deep_pursuit_A_mean | first_deep_pursuit_B_mean | pct_ticks_deep_pursuit_A_mean | pct_ticks_deep_pursuit_B_mean | mean_enemy_collapse_signal_A | mean_enemy_collapse_signal_B |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v2 | 54 | 1.00 | 1.00 | 98.60 | 99.38 | 0.8877 | 0.9064 |
| v3_test @ 1.1 | 54 | 211.56 | 133.24 | 12.21 | 27.55 | 0.2940 | 0.3001 |

## Event Integrity
- `First Contact` mean delta (`v3_test - v2`): -2.44
- `Formation Cut` mean delta (`v3_test - v2`): -12.74
- `Pocket Formation` mean delta (`v3_test - v2`): 20.44
- `v2` event_order_anomaly count: 14
- `v3_test @ 1.1` event_order_anomaly count: 0
- `v2` missing_cut / pocket_without_cut: 0 / 0
- `v3_test @ 1.1` missing_cut / pocket_without_cut: 0 / 0

## Stability
- Determinism spot-check passed for both sources.
- No obvious new jitter concern in sampled set: `True`.
- Mirror stability was judged qualitatively from asymmetric-opponent BRF samples; no new gross side-instability was observed.

## Human Sanity BRFs
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/brf_samples/confirm_v2_FR5_MB5_PD5_mittermeyer_SP01_Battle_Report_Framework_v1.0.md`
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/brf_samples/confirm_v3_test_FR5_MB5_PD5_mittermeyer_SP01_Battle_Report_Framework_v1.0.md`
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/brf_samples/confirm_v2_FR5_MB5_PD5_muller_SP01_Battle_Report_Framework_v1.0.md`
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/brf_samples/confirm_v3_test_FR5_MB5_PD5_muller_SP01_Battle_Report_Framework_v1.0.md`
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/brf_samples/confirm_v2_FR5_MB5_PD5_reinhard_SP01_Battle_Report_Framework_v1.0.md`
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/brf_samples/confirm_v3_test_FR5_MB5_PD5_reinhard_SP01_Battle_Report_Framework_v1.0.md`

## Recommendation
- **ACCEPT**