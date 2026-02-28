# Engineering Report v1.0 - DIAG4-F4 Boundary Differential

Engine Version: v5.0-alpha1
Target Scenario: Phase V Reference Scenario Alpha
Modified Layer: none (diagnostic-only)
Behavioral Modification: none
Cross-Dimension Coupling: none
Backward Compatible: yes
Determinism: PASS

## Evidence
- Base mixed pockets confirmed: 5 / 5
- Boundary label flips under +/-0.5 local FR perturbation: 8
- Label counts (all F4 cases): {'persistent_isolation_absorbing': 9, 'reversible_or_mixed': 7}
- Debug overhead sample (Alpha): 12.43%

## Base Pocket Readout
- M1: base_label=reversible_or_mixed, absorbing=0.250, persistent=4, isolation=0.681, blockage=0.116
- M2: base_label=reversible_or_mixed, absorbing=0.333, persistent=3, isolation=0.695, blockage=0.105
- M3: base_label=reversible_or_mixed, absorbing=0.200, persistent=5, isolation=0.774, blockage=0.050
- M4: base_label=reversible_or_mixed, absorbing=0.333, persistent=3, isolation=0.709, blockage=0.063
- M5: base_label=reversible_or_mixed, absorbing=0.333, persistent=6, isolation=0.779, blockage=0.039

## Boundary Differential
- M1: M1_BASE -> M1_dA_plus_0p5 flip (reversible_or_mixed -> persistent_isolation_absorbing)
- M2: M2_BASE -> M2_dA_plus_0p5 flip (reversible_or_mixed -> persistent_isolation_absorbing)
- M3: M3_BASE -> M3_dA_plus_0p5 flip (reversible_or_mixed -> persistent_isolation_absorbing)
- M3: M3_BASE -> M3_dB_minus_0p5 flip (reversible_or_mixed -> persistent_isolation_absorbing)
- M4: M4_BASE -> M4_dA_plus_0p5 flip (reversible_or_mixed -> persistent_isolation_absorbing)
- M4: M4_BASE -> M4_dB_plus_0p5 flip (reversible_or_mixed -> persistent_isolation_absorbing)
- M5: M5_BASE -> M5_dA_plus_0p5 flip (reversible_or_mixed -> persistent_isolation_absorbing)
- M5: M5_BASE -> M5_dB_minus_0p5 flip (reversible_or_mixed -> persistent_isolation_absorbing)

## Hypothesis
- Mechanism is a narrow topology-transition boundary between:
  - absorbing isolation dominant branch
  - reversible return branch
- Outlier persistence change is driven primarily by return probability shift (absorbing_ratio), not by blockage takeover.

## Falsifiable Chain
1. If local FR perturbation increases return opportunities, `OUTLIER->SHELL` transitions rise and mixed labels appear.
2. If perturbation reduces return opportunities, absorbing_ratio rises and labels return to persistent_isolation_absorbing.
3. If this chain is wrong, label flips should not co-occur with absorbing_ratio transition in boundary pairs.

## Governance Questions Answered (DIAG4 continuity)
1. Absorbing state dominant? yes on most cases, no on all mixed pockets.
2. Isolation vs blockage dominant? isolation remains dominant; blockage is secondary.
3. Cumulative vs spike? cumulative displacement remains dominant (move component largest).
4. Re-entry obstructed geometrically? yes; open_path_ratio stays 0.0 while blocked_path_ratio stays 1.0 in sampled windows.
5. Symmetry across fleets? persistent units remain predominantly fleet A in this local domain.

## Artifacts
- diag4_f4_summary.json
- diag4_f4_table.csv
- diag4_f4_boundary_diff.csv
- diag4_f4_timeseries_sample.csv



## Residual Risks
- Debug overhead sample is +12.43%, above Governance +10% target.
- blocked_path_ratio discriminator is saturated (near 1.0), so fine-grained obstruction stratification remains limited.
