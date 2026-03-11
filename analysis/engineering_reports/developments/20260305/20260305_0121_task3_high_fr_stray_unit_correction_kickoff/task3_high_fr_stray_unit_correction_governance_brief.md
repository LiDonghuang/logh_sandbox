# Governance Brief - Task 3 High-FR Stray Unit Correction Kickoff
Engine Version: v5.0-alpha5
Scope: Task3 execution kickoff package (planning + run matrix)

## Summary
1. Phase VIII-C decision keeps `movement_model=v1` as canonical default.
2. Task3 starts as a targeted correction workflow for high-FR stray behavior in v3a branch.
3. This kickoff package contains no runtime code changes.

## Kickoff Artifacts
1. `task3_high_fr_stray_unit_correction_execution_spec.md`
2. `task3_high_fr_stray_unit_correction_run_matrix.csv`

## Governance-Relevant Guardrails
1. Runtime default unchanged (`v1`).
2. Task3 patching, when started, will be confined to v3a branch and test_mode=2 path.
3. No combat/targeting/PD/collapse formula changes.
4. BRF schema unchanged.

## Next Engineering Action
Run T3-1 baseline matrix and deliver observer-rich run table + summary for patch-entry decision.
