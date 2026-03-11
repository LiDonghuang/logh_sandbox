# Engineering Report v1.0 - DIAG4-RPG Alignment

Engine Version: v5.0-alpha1
Modified Layer: runtime debug instrumentation only (diagnostic path)
Affected Parameters: debug-only (`debug_diag4_rpg_enabled`, `debug_diag4_rpg_window`)
New Variables: none in behavior path
Cross-Dimension Coupling: none
Mapping Impact: none
Governance Impact: diagnostic-only
Backward Compatible: yes
Stability: determinism=PASS
Insertion Point: `integrate_movement` diagnostic block only
Whitelist Files: `runtime/engine_skeleton.py`

## Acceptance Gates
1. Determinism: PASS
2. fsr=0 regression: PASS
3. kappa distribution: count=18, p10=1.000000, p50=1.000000, p90=1.238446
4. g_i distribution: count=18, p10=0.334479, p50=0.685210, p90=1.518056
5. Windowed P_return: window=20, value=0.312682
6. No new attractor signal: PASS

## Canonical Separation (Required)
- Projection suppression candidates (`v_tilde_r>0` and `v_r<=0`): 0
- Movement outward bias (`v_tilde_r<=0`): 7
- Inward free & effective (`v_tilde_r>0` and `v_r>0`): 11
- RPG outlier sample count: 18

## Notes
- Radial convention follows Governance Option A.
- R_shell uses RMS radius; delta = 0.1 * separation_radius.
- No behavior patch is proposed in this submission.
- Debug overhead sample: 18.94%.

## Artifacts
- diag4_rpg_summary.json
- diag4_rpg_metrics.csv
