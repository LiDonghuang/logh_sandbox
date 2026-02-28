# Governance Submission - Phase V.1 DIAG4-RPG Alignment

Engine Version: v5.0-alpha1  
Modified Layer: runtime debug instrumentation only (diagnostic path)  
Affected Parameters: `debug_diag4_rpg_enabled` (default `false`), `debug_diag4_rpg_window` (default `20`)  
New Variables: none in behavior path  
Cross-Dimension Coupling: none  
Mapping Impact: none  
Governance Impact: diagnostic-only, no patch request  
Backward Compatible: yes  
Stability: determinism PASS  
Insertion Point: `runtime/engine_skeleton.py:integrate_movement` diagnostic block  
Whitelist Files: `runtime/engine_skeleton.py`

## Evidence
- Canonical alignment implemented:
  - `d_hat=(C_f-x_i)/||C_f-x_i||` (inward)
  - inward criterion: `v_tilde_r_i > 0`
  - `R_shell = R_rms`
  - `epsilon=1e-12`, `delta=0.1*separation_radius`
- Determinism gate: PASS.
- `fsr=0` regression gate: PASS (diag OFF vs diag ON digest identical).
- No new attractor signal proxy: PASS (Alpha baseline survivors/contact tick unchanged).
- Required separation counts (main run, tick=300):
  - projection suppression candidates (`v_tilde_r>0` and `v_r<=0`): `0`
  - movement outward bias (`v_tilde_r<=0`): `7`
  - inward free & effective (`v_tilde_r>0` and `v_r>0`): `11`
  - RPG outlier count: `18`
- `kappa` distribution (main run snapshot):
  - count `18`, p10 `1.0000`, p50 `1.0000`, p90 `1.2384`
- `g_i` distribution (main run snapshot):
  - count `18`, p10 `0.3345`, p50 `0.6852`, p90 `1.5181`
- Windowed `P_return`:
  - overall `0.3127` (`window=20`, success `323`, fail `710`)
  - fleet A `0.3775`, fleet B `0.2505`

## Hypothesis
- Under current Alpha setting, dominant separated class at late stage is movement outward bias rather than projection suppression.
- No formal absorbing-geometry proof is claimed from this single scenario; submission is metric-alignment completion plus gate evidence.

## Required Additional Evidence
- Expand DIAG4-RPG to boundary pockets (M1..M5) to verify whether suppression class appears in mixed regime.
- Add scenario-level confidence intervals for `P_return` across seeds/cases (still deterministic per seed).
- Reduce debug overhead to governance target (`<= +10%`).

## Risk If Wrong
- If single-scenario inference is over-generalized, mechanism attribution may be biased.
- If overhead issue is ignored, future diagnostic submissions may be blocked procedurally.

## Decision (Engineering Recommendation)
- DIAG4-RPG alignment **complete and compliant** for diagnostic phase gates.
- Keep phase as diagnostic-only; do not propose behavior patch.
- Request Governance approval for next diagnostic step: multi-pocket RPG sweep + overhead-thinning pass.

## Residual Risks (<=3)
1. Debug overhead sample currently `+18.94%` (above `+10%` target).
2. Current quantitative interpretation is based on Alpha main scenario only.
3. Absorbing condition is not yet formally verified across the mixed boundary domain.

## Artifacts
- `diag4_rpg_summary.json`
- `diag4_rpg_metrics.csv`
- `diag4_rpg_report_v1_0.md`
