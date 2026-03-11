Engine Version: v5.0-alpha5+v4c-shadow
Modified Layer: Cohesion observer (shadow only)
Affected Parameters: None (observer-only)
New Variables Introduced: cohesion_v3 shadow observables (LCC, C_conn, R, R_ref, rho, C_scale, C_v3)
Cross-Dimension Coupling: No
Mapping Impact: None
Governance Impact: None (diagnostic only)
Backward Compatible: Yes (decision path unchanged)

Summary:
1. Implemented cohesion_v3 as snapshot observer: C_v3 = clip(C_conn * C_scale, 0, 1).
2. Connectivity uses existing adjacency rule with separation_radius.
3. Scale uses R_ref = min_unit_spacing * sqrt(N), no arena-size dependency.
4. Window constants fixed for this shadow run: rho_low=0.35, rho_high=1.15, k=6.0.
5. Generated required early-tick 3x3x3 CSV and two full 0..200 case CSVs.
6. Added tick0/tick1 summary with dominant cause (conn-drop vs scale-penalty).
7. Determinism check (FR8_MB8_PD5 double-run digest): PASS.
8. Collapse/movement/PD/combat logic unchanged.
