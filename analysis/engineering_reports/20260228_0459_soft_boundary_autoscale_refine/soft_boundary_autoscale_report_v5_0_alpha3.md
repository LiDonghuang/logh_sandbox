# Engineering Report v1.0 - Soft Boundary Auto-Scaling Refinement

Engine Version: v5.0-alpha3
Modified Layer: Movement (soft boundary width derivation) + diagnostic readouts
Affected Parameters: BOUNDARY_SOFT_ENABLED
Derived Width Formula: w = min(separation_radius, 0.05 * L)
No New Tunables: confirmed
Summary:
1. Determinism: PASS
2. Combat regression: PASS
3. Mirror non-worsening: PASS
4. No new attractor signal: PASS
5. Boundary penetration count: 0
6. Permanent boundary trap count: 0
7. RPG overhead <10%: PASS (7.21%)
8. Large arena non-regression delta (A/B/contact): 0/0/0
9. Small arena check: before/after survivors 8/16 vs 8/16
10. Small arena mean boundary band fraction before/after: 0.0200/0.0200

Artifacts:
- soft_boundary_autoscale_summary_v5_0_alpha3.json
- soft_boundary_autoscale_metrics_v5_0_alpha3.csv
