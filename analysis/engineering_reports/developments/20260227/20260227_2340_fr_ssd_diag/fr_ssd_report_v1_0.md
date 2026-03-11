# Engineering Report v1.0 - Phase V.1 FR-SSD

Engine Version: v5.0-alpha1
Modified Layer: none (diagnostic runs only)
Affected Parameters: FR/FSR run-time input only (experiment setup)
New Variables: none
Cross-Dimension Coupling: none
Mapping Impact: none
Governance Impact: diagnostic-only
Backward Compatible: yes
Stability: Determinism=True
Insertion Point: none (no code-path change)
Whitelist Files: none (report artifacts only)

## Validation Summary
- Determinism (A1 repeat): PASS
- Swap behavior observed: Yes
- FR monotonic direction correct: Yes
- FSR interaction amplifies/compresses FR scale: None

## Required Answers
1. Swap behavior observed? Yes
2. FR monotonic direction correct? Yes
3. FSR interaction amplifies/compresses FR scale? None

## Notes
- Experiment A/B used FSR OFF to isolate FR wiring and monotonicity.
- Experiment C isolates FSR interaction at FR_A=FR_B=0.5.
- Snapshots provided as frame IDs + frame digests (no rendering dependency).

## Artifacts
- fr_ssd_summary.json
- fr_ssd_metrics.csv
