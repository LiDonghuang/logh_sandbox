# Governance Submit - Movement 3A Kickoff (v1 vs v3a)
Engine Version: v5.0-alpha5
Scope: Movement layer only (controlled switch `runtime.movement_model`)
Result: Implemented comparison and determinism verification

## 1. Scope Compliance
1. Changed movement behavior only when `movement_model=v3a`.
2. `movement_model=v1` keeps legacy path.
3. No combat/targeting/PD/collapse formula changes.
4. Observer/event/BRF schema unchanged.

## 2. Comparison Cases
1. FR8_MB8_PD5
2. reference_alpha_AB (FR4_MB5_PD5)

## 3. Artifacts
1. `E:/logh_sandbox/analysis/engineering_reports/developments/20260304/20260304_1538_movement_3a_kickoff/movement_3a_v1_vs_v3a_comparison.csv`
2. `E:/logh_sandbox/analysis/engineering_reports/developments/20260304/20260304_1538_movement_3a_kickoff/movement_3a_determinism_check.md`
3. `E:/logh_sandbox/analysis/engineering_reports/developments/20260304/20260304_1538_movement_3a_kickoff/movement_3a_kickoff_governance_submit.md`

## 4. Determinism Status
1. v1: PASS
2. v3a: PASS
3. v1 digest: `db28cc1969a3c50239b42b1e551c5b74a2cc092f62db656a6ffbc5933c1129da`
4. v3a digest: `59e0c3f9d26a2dd71ee7e4328048abfe22bc0ed6502b6b217d9dc063d1a7bbc8`

## 5. High-level Delta (FR8_MB8_PD5)
1. End tick: v1=458 vs v3a=582
2. First contact: v1=107 vs v3a=107
3. First kill: v1=117 vs v3a=116
4. FormationCut: v1=126 vs v3a=126
5. PocketFormation: v1=202 vs v3a=240
