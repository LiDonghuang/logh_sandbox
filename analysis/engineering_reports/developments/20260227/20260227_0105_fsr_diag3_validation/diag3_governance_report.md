# Phase V.1-DIAG3 Engineering Validation Report

## Governance Constraints Acknowledged
- Scope: diagnostic-only; no structural expansion.
- Behavioral modification: none.
- FSR main structure: unchanged.
- Projection clamp / PATCH1: rejected, not implemented.

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
- H3 anisotropy precursor support ratio: 0.000.
- H4 contact-pressure precursor support ratio: 0.000.
- Control H1 projection support ratio: 0.125.
- Control H2 collision support ratio: 0.000.
- Mirror macro reference (DIAG2, unchanged-runtime assumption): 3.062.
- Jitter reference (DIAG2, unchanged-runtime assumption): 522.000.
- Runtime overhead (debug on/off, representative): 2.44%.

## Hypothesis
- H3: Formation anisotropy spike is the primary precursor of persistent outliers.
- H4: Contact-topology concentration (contact pressure) spike is the primary precursor of persistent outliers.

## Required Additional Evidence
- Any causal claim requires support ratio >= 0.70 on persistent scenarios.
- Candidate precursor should dominate controls (H1/H2) and keep gate order intact.

## Risk If Wrong
- Mis-identified cause can divert diagnostics and delay stabilization.
- False causal attribution may motivate invalid safeguards and increase attractor risk.

## Proposed Minimal Intervention
- None in DIAG3 (diagnostic-only phase).
- Keep runtime behavior unchanged; advance only with targeted falsification tests.

## Decision Branch
- If not confirmed (current result): reject single-factor causality and continue coupled diagnostics before any patch path.

## Attractor Question (Mandatory)
- Proxy result (monotonic alive sequences): risk_flag=False.
- Engineering interpretation: no new attractor-class signal detected under current proxy; formal attractor proof remains out of scope.

## Artifacts
- diag3_scenario_table.csv
- diag3_summary.json
- diag3_timeseries_sample.csv
