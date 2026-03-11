# Governance Total Report - Movement Pre-Contact Geometry Causal Validation
Date: 2026-03-07  
Phase Label: Movement Pre-Contact Geometry / Causal Validation Phase  
Engine Baseline: v5.0-alpha5  
Scope: movement-layer experiment and analysis only

## 1. Executive Summary
Since the latest Governance instruction (A-line only), engineering has:
1. Consolidated runtime experimental path to A-line probe only.
2. Completed bounded causal sweep and two convergence rounds (CV-2/CV-3).
3. Preserved cross-layer boundaries (no FR/MB/PD semantics change; no cohesion/collapse/combat/targeting schema change).
4. Renamed probe knob to neutral naming (`centroid_probe_scale`) with compatibility mapping.

Core finding:
- Reducing centroid restoration weight mitigates persistent outlier symptoms and wedge tendency.
- Effect is non-monotonic in AR (U-shape behavior), and overly low scale (`0.40`) causes event timing drift risk.

## 2. What Was Executed
## 2.1 Runtime/Config Consolidation
- Kept only:
  - `movement_v3a_experiment = base`
  - `movement_v3a_experiment = exp_precontact_centroid_probe`
- Removed B/C experiment logic from runtime execution path.
- Added neutral knob:
  - `runtime.centroid_probe_scale`
- Compatibility preserved:
  - legacy settings key `precontact_centroid_probe_scale` accepted
  - legacy engine attribute fallback retained
  - run snapshot keeps legacy alias field for one-cycle compatibility

Touched files:
- `runtime/engine_skeleton.py`
- `analysis/test_run_v1_0.py`
- `analysis/test_run_v1_0.settings.json`

## 2.2 Causal Sweep and Convergence
Script:
- `analysis/engineering_reports/developments/20260305/phase_viiid2_movement_precontact_explore/run_movement_precontact_explore.py`

Runs completed:
- Phase 2 sweep: 90 runs
- CV-2 dense local sweep: 54 runs
- CV-3 stability recheck: 108 runs

## 3. Evidence Package
Phase 2 outputs:
- `movement_precontact_causal_sweep_run_table.csv`
- `movement_precontact_causal_sweep_delta_table.csv`
- `movement_precontact_causal_sweep_summary_by_mb.csv`
- `movement_precontact_causal_sweep_determinism_check.md`
- `movement_precontact_causal_sweep_report.md`

CV-2 / CV-3 outputs:
- `movement_precontact_cv2_run_table.csv`
- `movement_precontact_cv2_score_table.csv`
- `movement_precontact_cv2_summary.md`
- `movement_precontact_cv3_run_table.csv`
- `movement_precontact_cv3_watch_drift.csv`
- `movement_precontact_cv3_summary.md`

Mechanism memo:
- `movement_v3a_mechanism_formula_memo_20260307.md`

## 4. Key Quantitative Findings
From Phase 2 report:
- Monotonic checks:
  - AR non-increasing: False
  - Wedge p10 non-decreasing: True
  - Persistent outlier p90 non-increasing: True
  - Max persistence non-increasing: True

- Mild timing gate (Governance thresholds):
  - `|Δfirst_contact| <= 5`
  - `p50|Δcut| <= 40`
  - `p50|Δpocket| <= 40`

Gate results:
- `scale=0.80`: PASS
- `scale=0.60`: PASS
- `scale=0.40`: FAIL (`p50|Δcut|` breach)

CV-2 ranking (geometry score, lower better):
1. `0.65`
2. `0.70`
3. `0.75`

CV-3 stability:
- Determinism: 54/54 PASS
- Mirror/jitter drift metrics: small and stable for `0.65` and `0.70`

## 5. Clarification on Current Probe Semantics
`centroid_probe_scale` is currently continuous across all ticks (not pre-contact gated).  
`precontact` remains an analysis-window concept:
- analysis window = `min(first_contact_tick - 1, 100)`
- runtime does not switch this mechanism off/on at contact boundary

This is intentional for continuity and auditable causality.

## 6. Risks and Open Questions
1. U-shape AR response indicates non-linear regime behavior.
2. Very low scale (`0.40`) can improve geometry symptoms but reorders tactical timing.
3. MB-subdomain sensitivity exists; aggregated metrics can hide MB-specific drift.

## 7. Candidate Governance Discussion Topics (No Implementation Requested)
1. Contact-aware/anticipatory phase logic:
   - Not current implementation.
   - Concept: use predicted near-future engagement instead of strict current-contact only.
2. Whether tactical pre-contact formation adaptation should be governed via:
   - MB/FR only, or
   - broader persona channels (for example ODW-related policy layer), under separate approval.
3. U-shape interpretation policy:
   - distinguish desirable tactical shaping vs undesired artifact.

## 8. Engineering Recommendation
For next bounded iteration, keep A-line only and prioritize `scale=0.70` as safer candidate, with `0.65` as secondary comparison, while enforcing per-MB timing checks.

## 9. Compliance Statement
- No runtime baseline switch decision made.
- No cross-layer coupling introduced.
- No BRF schema change.
- Work remains in experimental movement branch and analysis artifacts.
