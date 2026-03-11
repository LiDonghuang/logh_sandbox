# Governance Submit - Phase VIII-B Movement 3A DOE Validation (v1 vs v3a)
Engine Version: v5.0-alpha5
Scope: DOE validation only (no runtime semantics changes)

> [VOID NOTICE - 2026-03-05]
> Status: VOID (do not use for governance/runtime decisions).
> Reason: FR/FCR mapping error identified in the controlled-cell lineage used for FR interpretation.
> Any FR-main-effect interpretation from this phase lineage must be treated as invalid until rerun with correct FR mapping (`formation_rigidity`).

## Execution Summary
- Total runs completed: 540 (expected 540).
- Factors: movement_model in {v1,v3a}, FR in {2,5,8}, MB in {2,5,8}, PD=5, replicates=30 per cell.
- Replicate semantics: deterministic ordered archetype-pair sampling from 8-archetype roster (30/56).

## Guardrail Compliance
- No runtime code changes during DOE window: PASS (hash check in determinism file).
- No PD/collapse formula tuning: PASS.
- No BRF template schema change: PASS.

## Determinism Spot-check
- v1 digest equality: True
- v3a digest equality: True

## Artifact Index
- phase_viiiB_doe_run_table.csv
- phase_viiiB_doe_cell_summary.csv
- phase_viiiB_doe_binned_distributions.csv
- phase_viiiB_doe_comparison_report.md
- phase_viiiB_doe_determinism_check.md
- brf_artifacts/ and brf_artifacts.zip

## Acceptance Check
- DOE run count complete (540): PASS
- Determinism per movement_model: PASS
- Cell-level and overall v1-v3a comparison included: PASS
