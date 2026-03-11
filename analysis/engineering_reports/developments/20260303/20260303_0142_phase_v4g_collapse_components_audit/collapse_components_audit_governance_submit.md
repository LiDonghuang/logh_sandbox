# collapse_components_audit_governance_submit

Engine baseline: v5.0-alpha5 (observer-only; no decision-path switch)

## 1) C_conn_rel Semantic Audit
- Graph rule used in this audit: undirected relative-radius graph with edge(i,j) iff `dist(i,j) <= link_radius_live(t)`.
- `link_radius_live(t) = beta * d_ref_live(t)`, `beta=1.6`, `d_ref_live(t)=median(nearest-neighbor distance)` per side.
- `LCC` = largest connected component size, `C_conn_rel = LCC / N_alive` (degenerate `N<2 => C_conn_rel=1`).
- reference_alpha_AB t0: A C_conn_rel=1.000, B C_conn_rel=1.000; link_radius_live A=3.200, B=3.200
- FR8_MB8_PD5 t0: A C_conn_rel=1.000, B C_conn_rel=1.000; link_radius_live A=3.200, B=3.200

## 2) C_scale Anchor vs Live (Shadow Split)
- `C_scale_anchor`: reference uses `d_ref_anchor=tick0 median(d_i)`; `R_ref_anchor=d_ref_anchor*sqrt(N_alive(t))`.
- `C_scale_live`: reference uses `d_ref_live(t)=median(d_i)` each tick; `R_ref_live=d_ref_live(t)*sqrt(N_alive(t))`.
- Both variants exported side-by-side (`C_scale_anchor`, `C_scale_live`, plus `C_v3p1_anchor/live`).

## 3) ForceRatio Timing Alignment Audit
- Sampling point declared: `tick_end` for both `ForceRatio_tick_end` and `AttritionMomentum`.
- Audit columns include both `tick_start` and `tick_end` alive counts for traceability.

## 4) AttritionMomentum Early-Window Fix (Shadow)
- Legacy shadow: `AttritionMomentum=0` for `t<W`.
- Fixed shadow exported: `W_eff=min(W,t)` and windowed loss-rate difference (`AttritionMomentum_fixed`).

## 5) Determinism
- reference_alpha_AB digest run1/run2: e78061357a92502c9602639d2a2b5ca6939a8de33ac9d3f40b8a668fbd94570b / e78061357a92502c9602639d2a2b5ca6939a8de33ac9d3f40b8a668fbd94570b
- FR8_MB8_PD5 digest run1/run2: 077fb7ef99f911a070ab423a7634e627c280a6c5bd936a3b7e8403c61cdd1aa9 / 077fb7ef99f911a070ab423a7634e627c280a6c5bd936a3b7e8403c61cdd1aa9
- Determinism PASS: True

## Deliverables
- analysis/engineering_reports/20260303_0142_phase_v4g_collapse_components_audit/collapse_components_audit_governance_submit.md
- analysis/engineering_reports/20260303_0142_phase_v4g_collapse_components_audit/collapse_components_audit_FR8_MB8_PD5.csv
- analysis/engineering_reports/20260303_0142_phase_v4g_collapse_components_audit/collapse_components_audit_reference_alpha_AB.csv
