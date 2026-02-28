# Engineering Report v1.0 - DIAG4-F3 Stability Domain

Engine Version: v5.0-alpha1
Target Scenario: Phase V Reference Scenario Alpha
Modified Layer: none (diagnostic-only runs)
Behavioral Modification: none
Determinism sanity center-case: PASS

## Grid
- fsr_strength: [0.0, 0.1, 0.2]
- FR_A(1-10): [3.0, 4.0, 5.0]
- FR_B(1-10): [1.0, 2.0, 3.0]
- case_count: 27

## Domain Result
- label_counts: {'persistent_isolation_absorbing': 22, 'reversible_or_mixed': 5}
- persistent_isolation_absorbing_ratio: 0.815
- stability_level: medium

## Conclusion
- mechanism_stable_domain_exists: True
- interpretation: Persistent isolation-absorbing mechanism is dominant on this local grid.

## Artifacts
- diag4_f3_summary.json
- diag4_f3_table.csv
