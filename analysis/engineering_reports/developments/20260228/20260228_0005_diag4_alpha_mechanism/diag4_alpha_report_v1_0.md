# Engineering Report v1.0 - DIAG4 Alpha Mechanism Deep Dive

Engine Version: v5.0-alpha1
Modified Layer: none (diagnostic execution only; existing debug instrumentation reused)
Affected Parameters: none
New Variables: none
Cross-Dimension Coupling: none
Mapping Impact: none
Governance Impact: diagnostic-only
Backward Compatible: yes
Stability: Reference determinism=PASS
Insertion Point: none
Whitelist Files: none

## Key Findings
- Persistent units: 7
- Absorbing/Reversible/Metastable ratio: 0.857 / 0.143 / 0.000
- Isolation vs blockage ratio: 0.719 vs 0.074
- Displacement totals (move/fsr/proj): 49.000 / 4.569 / 4.294
- Dominant component counts: {'move': 7, 'fsr': 0, 'projection': 0, 'mixed': 0}
- Debug overhead (on/off, Alpha, 300 ticks): +14.44%
- Mechanism label: persistent_isolation_absorbing

## Interpretation
1. Persistent outlier behavior in Alpha is mainly long-lived and isolation-dominant.
2. Emergence is cumulative with movement contribution dominant; FSR is secondary, projection is tertiary.
3. This supports a topological isolation + cumulative displacement mechanism on Alpha scenario.

## Artifacts
- diag4_alpha_summary.json
- diag4_alpha_timeseries.csv
- diag4_alpha_persistent_units.csv
