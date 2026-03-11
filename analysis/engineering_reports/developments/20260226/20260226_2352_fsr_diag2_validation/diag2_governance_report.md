# Phase V.1-DIAG2 Engineering Validation Report

## Governance Constraints Acknowledged
- Scope: multi-scenario validation only.
- Behavioral modification: none.
- PATCH1 status: not implemented; remains proposal-only until DIAG2 gate is satisfied.

## Acceptance Priority (Adopted)
1. Determinism
2. fsr=0 regression
3. Outlier persistence reduction
4. Mirror macro non-worsening
5. Jitter non-worsening
6. Runtime overhead <= +10%

## Evidence
- Scenario grid: FR_A=[0.7, 0.8, 0.9, 1.0], FR_B=[0.6, 0.7, 0.8, 0.9], fsr_strength=0.2, seed=20260227.
- Determinism all-pass: True.
- fsr=0 regression all-pass: True.
- Persistent outlier scenarios (>20 ticks): 16/16.
- Projection-spike support ratio on persistent scenarios: 0.000.
- Collision-pair-spike support ratio on persistent scenarios: 0.625.
- Mirror macro mean |M(i,j)+M(j,i)|: 3.062.
- Jitter mean: 522.000.

## Hypothesis
- H1: Projection displacement spike is the primary precursor of persistent outliers.
- H2: Collision-pair spike is the primary precursor of persistent outliers.

## Required Additional Evidence
- For patch authorization: require H1 support ratio >= 0.70 on persistent scenarios.
- Require H2 not dominant (support ratio clearly below H1).
- Require no attractor-risk proxy trigger.

## Risk If Wrong
- If H1 is false and clamp is applied, patch may suppress symptoms while leaving root cause unchanged.
- Potential side effect: geometric deformation compensation shifts to other stages and harms mirror/jitter.

## Proposed Minimal Intervention
- Stability Safeguard (proposal-only): single-tick projection displacement clamp.
- Clamp bound must derive from existing physical scale (attack_range or separation_radius).
- No new tunable parameter; default behavior unchanged unless safeguard is activated by approved condition.

## Decision Branch
- If confirmed (H1 supported=True): proceed to Governance review for Phase V.1-PATCH1 proposal package.
- If not confirmed (H1 supported=False, current DIAG2 result): reject projection-primary hypothesis and open alternative diagnostics before any patch.

## Attractor Question (Mandatory)
- Proxy result (monotonic alive sequences): risk_flag=False.
- Engineering interpretation: no new attractor-class signal detected under current proxy; formal attractor proof remains out of scope.

## Artifacts
- diag2_scenario_table.csv
- diag2_summary.json
