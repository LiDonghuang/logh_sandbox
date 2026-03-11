# Movement 3B DOE Comparison Report

## Scope
- DOE grid: FR in {2,5,8}, MB in {2,5,8}, PD=5, opponents=first six archetypes.
- Models: v1, v3a, v3b.
- Total runs: 162 (9 cells x 6 opponents x 3 models).
- Isolation: runtime decision source fixed to `v2` for all models.

## Overall Means
| metric | v1 | v3a | v3b |
| --- | ---: | ---: | ---: |
| win_rate_A | 0.519 | 0.648 | 0.426 |
| first_contact_tick_mean | 107.26 | 107.72 | 107.76 |
| cut_tick_T_mean | 153.04 | 160.43 | 154.72 |
| AR_p90_A_mean | 2.225 | 2.051 | 2.191 |
| Wedge_p50_A_mean | 0.986 | 1.000 | 0.984 |

## Notes
- `movement_3b_doe_delta_table.csv` provides pairwise deltas per (cell, opponent).
- Focus metric for 3B objective: `delta_ar_p90_A_v3b_minus_v3a` (expect negative in high-FR cells).

## Artifacts
- movement_3b_doe_run_table.csv
- movement_3b_doe_delta_table.csv
- movement_3b_doe_cell_summary.csv
- movement_3b_doe_determinism_check.md