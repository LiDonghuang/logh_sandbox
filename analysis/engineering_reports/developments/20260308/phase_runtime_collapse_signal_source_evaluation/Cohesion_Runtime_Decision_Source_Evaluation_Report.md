# Cohesion Runtime Decision Source Evaluation Report

## Scope
- Evaluation type: runtime collapse signal source replacement only (`v2` vs `v3_test`)
- Movement baseline frozen: `v3a` + `exp_precontact_centroid_probe` + `centroid_probe_scale=0.5`
- Event bridge frozen: `theta_split=1.7`, `theta_env=0.5`
- Boundary override for DOE: `enabled=false`, `soft_strength=1.0`, `hard_enabled=false`
- Opponents: first six canonical archetypes (excluding `yang` / `default`)
- Controlled persona: FR/MB/PD cell injection; other seven parameters fixed at 5; FCR fixed at 5

## Fixed Seed Discipline
- `SP01`: random=1981813971, background=897304369, metatype=3095987153
- `SP02`: random=104729, background=130363, metatype=181081

## Preflight
- Cells: `FR2_MB2_PD2`, `FR5_MB5_PD5`, `FR8_MB8_PD8`
- Opponents: first two canonical archetypes
- Sources: `v2` vs `v3_test`
- Total runs: 12

- Condition 1 (`effective == requested`): **True**
- Condition 2 (`cohesion_v2` differs from `cohesion_v3_shadow`): **True**
- Condition 3 (observable runtime-path difference exists): **True**

## Main DOE
- Total runs: 648
- Grid: FR x MB x PD = 3 x 3 x 3
- Opponents: 6
- Sources: 2
- Seed profiles: 2

## Overall Source Comparison
| source | n_runs | first_contact_mean | cut_exists_rate | pocket_exists_rate | first_deep_pursuit_A_mean | first_deep_pursuit_B_mean | mean_enemy_collapse_signal_A | mean_enemy_collapse_signal_B |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v2 | 324 | 110.5432 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.8923 | 0.8958 |
| v3_test | 324 | 109.2160 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.6681 | 0.6819 |

## Runtime-Path Delta Summary (`v3_test - v2`)
- `first_contact_tick` mean delta: -1.3272
- `first_kill_tick` mean delta: -1.1173
- `first_deep_pursuit_tick_A` mean delta: 0.0000
- `first_deep_pursuit_tick_B` mean delta: 0.0000
- `mean_enemy_collapse_signal_A` mean delta: -0.2242
- `mean_enemy_collapse_signal_B` mean delta: -0.2139
- `mean_pursuit_intensity_A` mean delta: -0.3359
- `mean_pursuit_intensity_B` mean delta: -0.3645

## Event Integrity
- Missing cut count: `0`
- Pocket without cut count: `0`
- Event order anomaly count: `78`

## Geometry Delta Summary (`v3_test - v2`)
- `AR_forward p90 A` mean delta: -0.0641
- `WedgeRatio p10 A` mean delta: -0.0906
- `SplitSeparation p90 A` mean delta: 0.0035

## Human Sample BRFs
- Deterministic sample seed: `2026030801`
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/brf_samples/cohesion_source_v2_FR5_MB5_PD5_mittermeyer_SP01_Battle_Report_Framework_v1.0.md`
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/brf_samples/cohesion_source_v3_test_FR5_MB5_PD5_mittermeyer_SP01_Battle_Report_Framework_v1.0.md`
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/brf_samples/cohesion_source_v2_FR8_MB8_PD8_kircheis_SP01_Battle_Report_Framework_v1.0.md`
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/brf_samples/cohesion_source_v3_test_FR8_MB8_PD8_kircheis_SP01_Battle_Report_Framework_v1.0.md`
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/brf_samples/cohesion_source_v2_FR8_MB2_PD8_reinhard_SP01_Battle_Report_Framework_v1.0.md`
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/brf_samples/cohesion_source_v3_test_FR8_MB2_PD8_reinhard_SP01_Battle_Report_Framework_v1.0.md`
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/brf_samples/cohesion_source_v2_FR5_MB2_PD5_kircheis_SP01_Battle_Report_Framework_v1.0.md`
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/brf_samples/cohesion_source_v3_test_FR5_MB2_PD5_kircheis_SP01_Battle_Report_Framework_v1.0.md`
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/brf_samples/cohesion_source_v2_FR8_MB8_PD5_muller_SP01_Battle_Report_Framework_v1.0.md`
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/brf_samples/cohesion_source_v3_test_FR8_MB8_PD5_muller_SP01_Battle_Report_Framework_v1.0.md`
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/brf_samples/cohesion_source_v2_FR5_MB5_PD8_reinhard_SP02_Battle_Report_Framework_v1.0.md`
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/brf_samples/cohesion_source_v3_test_FR5_MB5_PD8_reinhard_SP02_Battle_Report_Framework_v1.0.md`

## Engineering Recommendation
- Use the attached DOE evidence to decide whether `v3_test` should replace `v2` as runtime collapse signal source.
- This report does not treat the change as a full cohesion mechanism replacement.