# Cohesion Component Diagnostic Report

- Runs: 66
- Cells: 11
- Opponents: reinhard, kircheis, reuenthal
- Sources: v2, v3_test
- Seed profile: SP01 (random=1981813971, background=897304369, metatype=3095987153)

## Global Findings

- `v2` pre-contact mean (Side A): 0.0391
- `v3_test-run` pre-contact mean `v2` score on realized geometry (Side A): 0.0566
- `v2` dominant penalty counts (Side A): elongation=0, dispersion=0, outlier_mass=0, fragmentation=33
- `v3_test-run` dominant penalty counts (Side A): elongation=0, dispersion=0, outlier_mass=0, fragmentation=33
- `v2` Side A mean `c_conn`: 0.2130
- `v2` Side A mean `c_scale`: 1.0000
- `v2` Side A mean rho band percentages: lt_low=0.00%, in_band=100.00%, gt_high=0.00%
- `v3_test-run` Side A mean `c_conn`: 0.2460
- `v3_test-run` Side A mean `c_scale`: 1.0000
- `v3_test-run` Side A mean rho band percentages: lt_low=0.00%, in_band=100.00%, gt_high=0.00%

## Paired Source Effects

- Mean Δ first_contact_tick (v3_test - v2): -1.333
- Mean Δ cut_tick (v3_test - v2): -5.727
- Mean Δ pocket_tick (v3_test - v2): +5.091
- Mean Δ A_v2_mean on realized geometry: +0.0176
- Mean Δ A_fragmentation_mean: -0.0329
- Mean Δ A_dispersion_mean: -0.0090
- Mean Δ A_outlier_mass_mean: +0.0000
- Mean Δ A_elongation_mean: -0.0708
- Mean Δ A_v3_mean on realized geometry: +0.0329
- Mean Δ A_c_scale_mean: +0.0000
- Mean Δ A_rho_mean: -0.0057

## Interpretation

- If `elongation` dominates the v2 penalty counts, low early `cohesion_v2` is mainly a shape-semantics issue rather than fragmentation.
- If `c_conn` stays near 1.0 while `c_scale` is materially below 1.0, low `cohesion_v3_shadow` is driven mainly by scale mismatch (`rho`), not by connectivity failure.
- The paired deltas above indicate whether switching the runtime source materially reshapes pre-contact geometry or mostly changes collapse/pursuit interpretation.

## Largest Paired Cases

- FR8_MB2_PD5 vs kircheis: ΔA_v2_mean=+0.0640, ΔA_v3_mean=+0.1382, Δcontact=-2.0
- FR8_MB5_PD5 vs kircheis: ΔA_v2_mean=+0.0639, ΔA_v3_mean=+0.2007, Δcontact=-3.0
- FR8_MB8_PD5 vs kircheis: ΔA_v2_mean=+0.0535, ΔA_v3_mean=+0.1795, Δcontact=-2.0
- FR5_MB5_PD2 vs kircheis: ΔA_v2_mean=+0.0533, ΔA_v3_mean=+0.1123, Δcontact=-2.0
- FR8_MB8_PD5 vs reinhard: ΔA_v2_mean=+0.0457, ΔA_v3_mean=+0.1038, Δcontact=-2.0

## Representative Timeline

- `cohesion_component_diagnostic_timeline_FR5_MB5_PD5_reinhard.csv`