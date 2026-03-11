# Movement Pre-Contact Geometry - Causal Validation Phase (A-line only)

## Scope
- Movement model: `v3a`
- Runtime decision source: `v2` (frozen)
- Variant set: `base` + `exp_precontact_centroid_probe` with scales 1.00 / 0.80 / 0.60 / 0.40
- Grid: FR=8, MB in {2,5,8}, PD=5, opponents=first six archetypes
- Pre-contact window: `min(first_contact_tick-1, 100)`

## Phase 2 Monotonic Trend Check (scale 1.00 -> 0.40)
- AR non-increasing: **False**
- WedgeRatio p10 non-decreasing: **True**
- Persistent outlier p90 non-increasing: **True**
- Max persistence non-increasing: **True**

| scale | mean AR p90 A | mean Wedge p10 A | mean persistent p90 | mean max persistence | geometry_score (lower better) |
| --- | --- | --- | --- | --- | --- |
| 1.00 | 2.1360 | 0.6342 | 2.9556 | 41.1111 | 0.0000 |
| 0.80 | 1.9793 | 0.7178 | 0.3333 | 16.8333 | -27.1403 |
| 0.60 | 2.0385 | 0.8078 | 0.0000 | 0.4444 | -43.8934 |
| 0.40 | 2.1410 | 1.0657 | 0.0000 | 0.0000 | -44.4933 |

## Constraint Drift (Mild Timing Gate)
- Gate thresholds: `|delta first_contact| <= 5`, `p50|delta cut| <= 40`, `p50|delta pocket| <= 40`

| scale | mean |delta first_contact| | p50 |delta cut| | p50 |delta pocket| | pass |
| --- | --- | --- | --- | --- |
| 1.00 | 0.0000 | 0.0000 | 0.0000 | True |
| 0.80 | 1.2222 | 2.0000 | 28.5000 | True |
| 0.60 | 2.3889 | 8.5000 | 27.5000 | True |
| 0.40 | 4.2778 | 59.5000 | 31.5000 | False |

## Geometry Improvement + Event-Reorder Risk Watch
| scale | cut_precontact_count | pocket_precontact_count | total_runs | risk_flag |
| --- | --- | --- | --- | --- |
| 1.00 | 0 | 0 | 18 | LOW |
| 0.80 | 0 | 0 | 18 | LOW |
| 0.60 | 0 | 0 | 18 | LOW |
| 0.40 | 0 | 0 | 18 | GEOMETRY_IMPROVES_BUT_TIMING_DRIFT_RISK |

## Artifacts
- movement_precontact_causal_sweep_run_table.csv
- movement_precontact_causal_sweep_delta_table.csv
- movement_precontact_causal_sweep_summary_by_mb.csv
- movement_precontact_causal_sweep_determinism_check.md
- movement_precontact_causal_sweep_report.md

## Standards Compliance
- standards_version: `DOE_Report_Standard_v1.0`
- script: `run_movement_precontact_explore.py`
- deviations: `No deviations`