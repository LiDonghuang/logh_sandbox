# Governance Submission - Phase V.1 DIAG4-F4 (Boundary Differential)

Engine Version: v5.0-alpha1  
Modified Layer: none (diagnostic-only)  
Affected Parameters: runtime none; experiment sweep only (`fsr_strength`, `FR_A`, `FR_B`)  
New Variables: none  
Cross-Dimension Coupling: none  
Mapping Impact: none  
Governance Impact: mechanism clarification only, no patch request in this submission  
Backward Compatible: yes  
Stability: determinism PASS (M3 base repeated run digest identical)  
Insertion Point: none  
Whitelist Files: none

## Evidence
- Scope: 16 diagnostic runs around DIAG4-F3 mixed pockets (5 base mixed pockets + local perturbations +/-0.5 FR).
- Base mixed pockets reproduced: 5/5.
- Boundary flip observed: 8/10 base->perturb pairs switched label (`reversible_or_mixed` <-> `persistent_isolation_absorbing`).
- Label distribution (all 16): `persistent_isolation_absorbing=9`, `reversible_or_mixed=7`.
- Re-entry geometry signal:
  - `open_path_ratio=0.0` for all 16.
  - `blocked_path_ratio=1.0` for all 16.
- Topology signal:
  - `isolation_ratio` range: 0.656 to 0.780.
  - `blockage_ratio` max: 0.128.
  - Isolation remains dominant over blockage in all sampled cases.
- Displacement attribution:
  - `dominant_move_count == persistent_unit_count` in all 16 runs.
  - Cumulative move component remains primary in persistent emergence windows.
- Determinism gate: PASS (`M3_BASE`, run1 digest == run2 digest).
- Debug overhead sample (Alpha): +12.43% (above +10% governance limit).

## Hypothesis
- Persistent outlier mechanism in current local domain is a **narrow topology-transition boundary** between:
  - absorbing-isolation dominant branch, and
  - reversible-return mixed branch.
- Mechanism shift is primarily controlled by **return probability transition** (absorbing ratio change), not by blockage takeover.

## Required Additional Evidence
- Quantify return-path quality with a higher-resolution geometric discriminator (current `blocked_path_ratio` saturated at 1.0).
- Repeat boundary test on one symmetric counterpart domain to confirm cross-fleet mechanism symmetry/non-symmetry robustness.
- Re-measure DIAG overhead after instrumentation thinning to satisfy `<= +10%` governance constraint.

## Risk If Wrong
- If boundary interpretation is incorrect, governance may misclassify mechanism as globally stable, leading to invalid safeguard direction.
- If overhead issue is ignored, subsequent DIAG submissions risk procedural rejection despite correct mechanism evidence.
- If topology discriminator remains saturated, false confidence in obstruction causality may persist.

## Decision (Engineering Recommendation)
- `If confirmed`:
  - keep Phase V.1 as diagnostic-only; no behavior patch proposal yet.
  - proceed to DIAG4 continuation focused on re-entry geometry discriminator refinement + overhead control.
- `If not confirmed`:
  - revert boundary hypothesis and return to neutral mechanism state (`mixed unresolved`), then expand only diagnostic sampling grid.

## Validation Summary (<=25 lines)
1. Ran 16 DIAG4-F4 cases around F3 mixed pockets, no runtime behavior edits.
2. Reproduced 5/5 mixed base pockets.
3. Observed 8/10 label flips under local FR +/-0.5 perturbation.
4. Determinism PASS on representative mixed base case.
5. Isolation metric remains consistently above blockage metric.
6. Re-entry open-path metric stayed 0.0; blocked-path metric stayed 1.0 in sampled windows.
7. Persistent emergence remains cumulative-move dominated.
8. Debug overhead sample measured +12.43% (residual governance risk).
9. No combat/targeting/objective/strategy modifications introduced.
10. No new attractor class signal observed in this local boundary scan.

## Residual Risks (<=3)
1. Debug overhead currently exceeds governance cap (+12.43% > +10%).
2. Re-entry blockage discriminator saturation reduces fine-grained causal resolution.
3. Boundary conclusion currently validated on local domain; broader domain generalization still pending.

## Artifacts
- `diag4_f4_summary.json`
- `diag4_f4_table.csv`
- `diag4_f4_boundary_diff.csv`
- `diag4_f4_timeseries_sample.csv`
- `diag4_f4_report_v1_0.md`
