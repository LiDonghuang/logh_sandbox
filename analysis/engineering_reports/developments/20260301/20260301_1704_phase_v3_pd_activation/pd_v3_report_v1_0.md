# Engineering Report v1.0 - Phase V.3 PD Canonical Activation
Engine Version: v5.0-alpha5
Modified Layer: Movement Decision Layer (PD activation in integrate_movement)
Affected Parameters: pursuit_drive (PD)
New Variables Introduced: None (runtime-local only)
Cross-Dimension Coupling: No
Mapping Impact: None (uses canonical Mapping Snapshot v1.1)
Governance Impact: None
Backward Compatible: Yes (PD=5 neutral regimes validated)

## Matrix
- FR in {2,8}, MB in {2,8}, PD in {2,5,8}
- Fixed: attack_range=5, FSR=0.1 on, CH on, boundary off, steps=300

## Gate Snapshot
- Determinism: PASS
- PD=5 neutral regression: PASS
- Mirror degradation vs alpha4 subset: 22.6483% (FAIL)
- Jitter degradation vs alpha4 subset: -10.0900% (PASS)
- Runtime overhead vs alpha4 subset: -26.7574% (PASS)
- No new attractor proxy: PASS
- No stable geometric locking proxy: PASS
- No single-sided pocket permanence: FAIL

## Macro Metrics
- mirror_macro_all_12: 0.183143770
- jitter_macro_all_12: 5420.000
- per_tick_macro_all_12: 0.021294670

Artifacts:
- pd_v3_matrix_metrics_v5_0_alpha5.csv
- pd_v3_pocket_lifetime_distribution.csv
- pd_v3_summary_v5_0_alpha5.json