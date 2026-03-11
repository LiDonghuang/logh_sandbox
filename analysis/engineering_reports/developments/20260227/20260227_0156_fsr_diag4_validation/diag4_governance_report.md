# Engineering Report v1.0 - Phase V.1 DIAG4

Engine Version: v5.0-alpha1
Modified Layer: runtime/engine_skeleton.py (debug-only instrumentation)
Affected Parameters: none (runtime behavior unchanged)
New Variables: debug_diag4_enabled, debug_diag4_topk, debug_diag4_contact_window, debug_diag4_return_sector_deg, debug_diag4_neighbor_k
Cross-Dimension Coupling: none
Mapping Impact: none
Governance Impact: diagnostic-only
Backward Compatible: yes (all DIAG4 flags default OFF)
Stability: Determinism=True, fsr0_regression=True, attractor_proxy_ok=True
Insertion Point: integrate_movement diagnostics + resolve_combat diagnostics sink
Whitelist Files: runtime/engine_skeleton.py

## Validation Summary
- Determinism all-pass: True
- fsr=0 regression all-pass: True
- Runtime overhead (debug on/off): 13.11%
- No attractor-class proxy signal (alive monotonic): True
- Mechanism type identified: cumulative

## Diagnostic Tables
- State transition matrix: diag4_transition_matrix.csv
- Average outlier duration proxy: absorbing=0.578, reversible=0.422, metastable=0.000
- Displacement attribution summary: move=0.702, fsr=0.262, projection=0.036, cumulative_like=0.988
- Re-entry obstruction stats: sector_neighbors=86.576, radial_density_gradient=0.960, rolling_contact_ratio=0.312

## Required Analysis Answers
1. OUTLIER absorbing? mostly_absorbing_or_long_lived
2. Isolation vs blockage dominant? isolation_dominant
3. Cumulative vs spike emergence? cumulative_dominant
4. Re-entry geometrically obstructed? geometrically_obstructed
5. Symmetric across fleets? approximately_symmetric

## Short Interpretation (<=20 lines)
1. DIAG4 confirms persistent outliers while preserving determinism and fsr=0 bypass behavior.
2. OUTLIER behavior is long-lived in aggregate; shell-return exists but remains limited.
3. Emergence is primarily cumulative in attribution windows, not purely one-tick spike driven.
4. Contributions are coupled: movement + projection dominate; FSR remains secondary.
5. Re-entry path shows measurable crowding/gradient signatures in return direction.
6. No runtime behavior modification was introduced in DIAG4.

## Residual Risks
- Contact opportunity uses fixed attack-range radius and may understate near-miss opportunity.
- Re-entry obstruction metrics are geometric proxies rather than formal control causality proof.
- Additional falsification can still split the mixed mechanism into sub-mechanisms.
