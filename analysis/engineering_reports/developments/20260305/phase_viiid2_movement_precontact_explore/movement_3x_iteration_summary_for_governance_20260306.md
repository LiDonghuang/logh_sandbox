# Movement 3X Iteration Summary for Governance (v3a -> v3b6)
Engine Version: v5.0-alpha5  
Date: 2026-03-06  
Scope: Engineering recap for movement-branch experiments only

## 1. Purpose
This note summarizes movement-model iterations from `v3a` onward, consolidates what is valid vs deprecated, and provides an engineering status snapshot for governance reference.

This summary does not request an immediate decision gate.  
It is intended to reduce context-switch cost before the next governance review.

## 2. Contract Check (Docs/Standards Re-verified)
Reviewed and aligned against:
1. `docs/architecture/LOGH_Analytical_Stack_Architecture_v1.0.md`
2. `docs/animation_contract_v1.md`
3. `analysis/engineering_reports/_standards/DOE_Report_Standard_v1.0.md`
4. `analysis/engineering_reports/_standards/BRF_Export_Standard_v1.0.md`

Confirmed constraints remained intact during these movement rounds:
1. Observer -> Events -> BRF contract preserved.
2. `t=0` treated as snapshot-only; event semantics use `t>=1`.
3. BRF schema unchanged.
4. Movement experimentation isolated to movement branch; no intentional PD/combat/collapse formula rewrites.

## 3. Timeline of Iterations and Evidence

### 3.1 v3a Kickoff (Completed)
Reference:
1. `analysis/engineering_reports/developments/20260304/20260304_1538_movement_3a_kickoff/movement_3a_kickoff_governance_submit.md`

Key points:
1. `movement_model` switch introduced (`v1` vs `v3a`).
2. Determinism passed per model in kickoff checks.
3. Early signal: engagement/event timing behavior changed, but artifact risk remained.

### 3.2 Early DOE and Invalidated Decision Gate
References:
1. `analysis/engineering_reports/developments/20260304/phase_viiiB_movement_3a_doe_validation/B2_DEPRECATED_FR_FCR_CONFUSION.md`
2. `analysis/engineering_reports/developments/20260305/20260305_0116_phase_viiic_movement_3a_decision_gate/phase_viiic_movement_3a_governance_submit.md`

Key points:
1. Initial Phase VIII-B interpretation was invalidated due FR/FCR naming/injection confusion.
2. Related decision-gate note is marked VOID and must not be cited for runtime adoption decisions.

### 3.3 Corrected Re-run (B3) and Main-Effect Recovery
Reference:
1. `analysis/engineering_reports/developments/20260305/phase_viiiB3_FR_MB_doe_rerun/doe_b3_summary.md`

Key points:
1. B3 enforced FR/FCR identity discipline and preflight assertions.
2. FR main effect reappeared under corrected setup.
3. FR x MB interaction remained non-uniform; pooling across models is unsafe for decisions.

### 3.4 Follow-up Geometry/Stray Diagnostics
Reference:
1. `analysis/engineering_reports/developments/20260305/phase_viiic_followup_movement_geometry/phase_viiic_followup_summary.md`

Key points:
1. Geometry diagnostics and stray-unit diagnostics were produced.
2. High-FR front-end outlier behavior remained a practical pain point in visual review.

### 3.5 Pre-contact 3B Family Exploration (v3b1..v3b5)
References:
1. `analysis/engineering_reports/developments/20260305/phase_viiid2_movement_precontact_explore/movement_precontact_explore_summary.md`
2. `analysis/engineering_reports/developments/20260305/phase_viiid2_movement_precontact_explore/movement_precontact_explore_determinism_check.md`

Key points:
1. Explored anti-stretch variants targeting pre-contact geometry.
2. Determinism checks passed for explored models.
3. v3b5 improved some split/AR-related metrics but did not reliably reduce persistent front outliers in animation/debug perception.

## 4. Current Technical Finding (Critical)
Root issue identified:
1. `SplitSeparation` and `persistent_outlier` are different observables and can diverge.
2. Split reduction does not guarantee reduction of persistent radial outliers.

Why divergence occurs:
1. Split is PCA-axis cluster-separation oriented.
2. Persistent outlier is radial-threshold + streak-duration oriented.
3. They are correlated only partially; optimizing one can worsen the other.

Implication:
1. Previous "pre-contact split suppression" objective was not perfectly aligned with human-observed front outlier symptom.
2. For this problem, optimization target should be explicitly `persistent_outlier` in the critical window.

## 5. Latest Engineering Probe: v3b6 (Minimal Single-Rule)
Status:
1. Added experimental `movement_model=v3b6` branch as a minimal pre-contact front-outlier suppression attempt.
2. Mechanism design intent: one rule only, focused on tick window ~80-100 and front radial outliers.

Quick local check (same current test settings, window 80-100):
1. `persist_mean`: `6.43` (v3b5) -> `4.14` (v3b6)  
2. `max_persist_mean`: `61.0` (v3b5) -> `49.86` (v3b6)  
3. Side effect observed: split-threshold exceedance increased in the same window.

Interpretation:
1. v3b6 moved in the correct direction for the primary symptom (persistent outliers).
2. Tradeoff emerged on split metric; this needs explicit balancing in next micro-iteration.

## 6. Validity / Deprecation Ledger
Valid for current reference:
1. v3a kickoff artifacts
2. B3 corrected DOE package
3. VIII-C follow-up geometry diagnostics
4. VIIID2 pre-contact exploration artifacts

Deprecated / non-citable for decisions:
1. Phase VIII-B2 (FR/FCR confusion)
2. Any decision claims derived from B2-era aggregated conclusions
3. Void-tagged decision-gate conclusions tied to invalid upstream interpretation

## 7. Engineering Recommendation (Next)
No governance escalation required yet unless requested.

Recommended next step:
1. Continue one-step micro-iteration after v3b6, with objective function centered on:
   - reduce `persistent_outlier_total` and `max_outlier_persistence` in pre-contact 80-100;
   - constrain collateral increase in split metrics.
2. Keep mechanism simple and auditable (single-rule style, no cross-layer coupling).
3. Re-run focused A/B checks (`v3b5` vs `v3b6` vs next variant) before any wider DOE.

## 8. Notes
1. This summary is an engineering synthesis, not a runtime adoption proposal.
2. Governance decision gate should be reopened only after the symptom-target metric and side-effects are jointly stable.
