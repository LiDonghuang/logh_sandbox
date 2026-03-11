# Phase VIII-C Decision Brief - Movement 3A Adoption Gate
Engine Version: v5.0-alpha5
Scope: Decision-layer synthesis only (no runtime changes)
Source Package: `analysis/engineering_reports/developments/20260304/phase_viiiB_movement_3a_doe_validation/`

> [VOID NOTICE - 2026-03-05]
> Status: VOID (do not use for governance/runtime decisions).
> Reason: FR/FCR mapping error in upstream DOE interpretation lineage.
> FR must map to `formation_rigidity`; this brief's FR-based conclusions are invalid.

## 1. Readout Summary
1. DOE baseline is complete and deterministic per model (v1/v3a).
2. Duration metrics are fully censored at `end_tick=300` (`540/540` runs, 100%).
3. Therefore, default-switch judgement must rely on event-quality and tactical interpretability metrics.

## 2. Key Model-Level Metrics
- v1:
  - cut_exists_rate: 92.222%
  - pocket_no_cut_rate: 7.778%
  - precontact_geom_cut_any_rate: 76.667%
  - mean_delta_pocket_minus_cut: 17.060
- v3a:
  - cut_exists_rate: 85.556%
  - pocket_no_cut_rate: 14.444%
  - precontact_geom_cut_any_rate: 96.667%
  - mean_delta_pocket_minus_cut: 43.338

Interpretation:
1. v3a advances cut timing but weakens cut consistency in MB=5/8 regimes.
2. v3a increases pre-contact geometry-trigger prevalence, raising tactical semantic mismatch risk.
3. v1 remains more stable as default for current BRF/BEL interpretation contract.

## 3. Decision (Phase VIII-C)
Recommended runtime default policy:
1. Keep `movement_model=v1` as canonical default (mode 0/1).
2. Keep `v3a` as experimental branch under `test_mode=2`.
3. Do not promote v3a to default before Task 3 correction and a non-censored rerun.

## 4. Next Execution Step
Proceed to Task 3 (high-FR stray-unit correction) under experimental branch, with focused validation and unchanged combat/PD/collapse semantics.
