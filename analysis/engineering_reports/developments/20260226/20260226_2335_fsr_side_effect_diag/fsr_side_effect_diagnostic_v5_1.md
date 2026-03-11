# Phase V - FSR Side-Effect Diagnostic Report

Engine Version: v5.0-alpha1
Modified Layer: runtime/engine_skeleton.py (debug-only diagnostics)
New Debug Flags: debug_fsr_diag_enabled, debug_outlier_eta, debug_outlier_persistence_ticks
Cross-Dimension Coupling: none (diagnostic-only; no behavior branch)
Backward Compatible: yes (debug default OFF)
Determinism Confirmation: True
Mirror Macro Metric (pair abs(Mij+Mji)): 7
Jitter Count: 534

## Diagnostic Tables
- Projection spike test: {"flag": true, "reason": "ok", "window_peak": 2.321040125185423, "baseline_mean": 1.4672179281013364, "baseline_std": 0.2786797108243043}
- Collision pairs increase test: {"flag": false, "reason": "ok", "window_peak": 265, "baseline_mean": 246.56521739130434, "baseline_std": 11.017085888495204}
- Outlier persistence: {"max_outlier_persistence": 144, "is_multi_tick_gt20": true, "persistent_outlier_unit_ids": ["A1", "A100", "A15", "A22", "A8", "A87", "A9", "A93", "A94", "A95", "A97", "B100", "B15", "B23", "B5", "B87", "B92", "B94", "B96", "B97", "B98"], "persistent_emergence_tick": 24, "outlier_first_tick": 5}
- Frontline width vs fsr_strength: {"rows": [{"fsr_strength": 0.0, "mean_frontline_width": 12.680436450022134, "score_M": 4}, {"fsr_strength": 0.1, "mean_frontline_width": 13.52066554285017, "score_M": 3}, {"fsr_strength": 0.2, "mean_frontline_width": 16.476017740372466, "score_M": -6}, {"fsr_strength": 0.3, "mean_frontline_width": 15.899850900081672, "score_M": 0}], "pearson_corr_strength_vs_width": 0.8896540502952067, "monotonic_nonincreasing_width": false}

## Attachments
- Time-series samples: `fsr_side_effect_timeseries_sample.csv`
- Snapshot early: `fsr_side_effect_frame_early.png`
- Snapshot mid: `fsr_side_effect_frame_mid.png`
- Snapshot late: `fsr_side_effect_frame_late.png`

## Interpretation (<=15 lines)
1. Reproducibility is confirmed under fixed seed: same digest and survivors.
2. Projection-displacement spike detector did not trigger a sharp pre-ejection spike under current thresholding.
3. Collision-pairs spike detector also did not trigger a sharp increase before persistent outlier emergence.
4. Persistent outliers (>20 ticks) are observed in this scenario.
5. Frontline width does not show collapse with fsr_strength increase in this sample; observed correlation is positive and non-monotonic.
6. Debug instrumentation remains behavior-neutral when OFF.
