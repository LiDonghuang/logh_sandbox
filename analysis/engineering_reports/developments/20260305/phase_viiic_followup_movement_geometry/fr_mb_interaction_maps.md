# FR x MB Interaction Maps (B3 Follow-up)

Run note: current environment has no `matplotlib`; therefore PNG plots are not generated in this run, and matrix CSVs are the authoritative heatmap artifacts.

## Win-rate Heatmaps
- `heatmap_win_rate_A_v1.png`
- `heatmap_win_rate_A_v3a.png`
- `heatmap_win_rate_delta_v3a_minus_v1.png`

## Event Timing Heatmaps (Cut_T)
- `heatmap_cut_tick_T_v1.png`
- `heatmap_cut_tick_T_v3a.png`
- `heatmap_cut_tick_T_delta_v3a_minus_v1.png`

## Geometry Heatmaps (AR p90, A side)
- `heatmap_ar_p90_A_v1.png`
- `heatmap_ar_p90_A_v3a.png`
- `heatmap_ar_p90_A_delta_v3a_minus_v1.png`

## CSV Fallback (always exported)
- `*.matrix.csv` files mirror all heatmaps in numeric matrix form.

Data source:
- outcome/event: `doe_b3_run_table.csv`
- geometry: replayed runs from B3 injection vectors via `run_simulation` (observer-only)
