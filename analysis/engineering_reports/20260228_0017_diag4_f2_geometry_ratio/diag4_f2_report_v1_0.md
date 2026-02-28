# Engineering Report v1.0 - DIAG4-F2 Geometry Density Scan

Engine Version: v5.0-alpha1
Target Scenario: Phase V Reference Scenario Alpha
Modified Layer: none (diagnostic run only)
Cross-Dimension Coupling: none
Behavioral Modification: none
Determinism sanity (F2_M): PASS

## Key Result
- Mechanism label stable across scan: True
- Labels by case: ['persistent_isolation_absorbing', 'persistent_isolation_absorbing', 'persistent_isolation_absorbing']
- Conclusion: Mechanism remains isolation-absorbing across geometry ratio scan.

## Cases
- F2_L: ratio=12.00, persistent=9, absorb=0.667, isolation=0.749, blockage=0.075, label=persistent_isolation_absorbing
- F2_M: ratio=15.00, persistent=7, absorb=0.857, isolation=0.719, blockage=0.074, label=persistent_isolation_absorbing
- F2_H: ratio=18.00, persistent=8, absorb=0.625, isolation=0.723, blockage=0.073, label=persistent_isolation_absorbing

## Artifacts
- diag4_f2_summary.json
- diag4_f2_table.csv
- diag4_f2_timeseries_mid.csv
