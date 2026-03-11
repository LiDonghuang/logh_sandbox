# Governance Submit - Phase VI Event Detector Calibration (Formation Metrics Distribution)
Engine Version: v5.0-alpha5 (runtime path unchanged)
Scope: Observer/Analysis only (no event detector code changes applied)

## Explicit Assumptions
- FR/MB/PD tuple is applied symmetrically to A/B in each listed case.
- Non-scanned ten-parameter dimensions are fixed at 5.0.
- Run horizon is fixed at 300 ticks for comparability.

## Determinism Spot-check
- Case: FR8_MB8_PD5
- Digest run1: `e0bd469ddafda3476f71ccbdffd5c10810d0aa391c882734226e1be55fc94f5d`
- Digest run2: `e0bd469ddafda3476f71ccbdffd5c10810d0aa391c882734226e1be55fc94f5d`
- Result: **PASS**

## Cases Executed
- A_FR8_MB8_PD5: FR=8.0, MB=8.0, PD=5.0
- B_FR5_MB5_PD5: FR=5.0, MB=5.0, PD=5.0
- C_FR5_MB2_PD5: FR=5.0, MB=2.0, PD=5.0
- C_FR5_MB5_PD5: FR=5.0, MB=5.0, PD=5.0
- C_FR5_MB8_PD5: FR=5.0, MB=8.0, PD=5.0
- D_FR2_MB5_PD5: FR=2.0, MB=5.0, PD=5.0
- D_FR5_MB5_PD5: FR=5.0, MB=5.0, PD=5.0
- D_FR8_MB5_PD5: FR=8.0, MB=5.0, PD=5.0

## Non-activation Diagnosis
- Split mean coverage: 100.00% (too loose)
- Enveloping mean coverage: 36.46% (plausible)
- Line mean coverage: 0.00% (too strict)
- Interpretation: Tier-2 N/A behavior is primarily threshold-range mismatch under current observed metric distributions.

## Proposed Adjustments (Documentation Only, Not Applied)
- split_separation: 1.20 -> 1.715
- angle_coverage: 0.50 -> 0.583
- AR(line): 3.00 -> 2.200
- compact AreaScale quantile: q30 -> q35
- rectangle wedge tolerance: 0.20 -> 0.25

## Artifacts
- `analysis/engineering_reports/developments/20260304/20260304_0155_phase_vi_event_detector_calibration/formation_metric_distributions.csv`
- `analysis/engineering_reports/developments/20260304/20260304_0155_phase_vi_event_detector_calibration/formation_metric_threshold_coverage.csv`
- `analysis/engineering_reports/developments/20260304/20260304_0155_phase_vi_event_detector_calibration/formation_metric_distribution_report.md`
- `analysis/engineering_reports/developments/20260304/20260304_0155_phase_vi_event_detector_calibration/phase_vi_event_calibration_governance_submit.md`

## Explicit Constraints Reconfirmed
- No runtime behavior code modified.
- No BRF template schema modified.
- Observer -> Events -> BRF contract preserved.
