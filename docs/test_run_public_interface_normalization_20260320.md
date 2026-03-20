# Test Run Public Interface Normalization (2026-03-20)

Status: major item record  
Scope: harness-only / public interface normalization  
Classification: non-runtime-semantic / non-canonical / non-baseline-replacement

## 1. Identity

This record covers a bounded `Phase A / A5.1` change:

- `test_run` public harness interface normalization

This change is:

- not a runtime semantics change
- not an observer doctrine change
- not a baseline replacement
- not a canonical/governance rewrite

## 2. Problem Being Solved

The remaining A5 blocker was no longer ordinary launcher cleanup.

The main public problem had become:

- `test_run/test_run_experiments.py::run_simulation(...)` exposed a very wide scalar public interface
- `test_run/test_run_main.py` still had visible parameter shuttle because of that wide public surface
- temporary direct callers under `analysis/engineering_reports/developments/...` had historical dependency on that scalar surface

## 3. New Public Interface

`run_simulation(...)` now uses a grouped harness interface:

- `initial_state`
- `engine_cls`
- `execution_cfg`
- `runtime_cfg`
- `observer_cfg`

The grouped inputs are defined in `test_run/test_run_experiments.py` as plain semantic mappings:

- `execution_cfg`
- `runtime_cfg`
- `observer_cfg`

`runtime_cfg` is further grouped into:

- `movement`
- `contact`
- `boundary`

`observer_cfg` is further grouped into:

- `bridge`
- `collapse_shadow`

These groups were chosen because they reflect real execution semantics:

- execution / orchestration
- runtime movement/contact/boundary
- observer / bridge / collapse-shadow diagnostics

This round explicitly did **not** use:

- one mega-dict
- `**kwargs` soup
- a new long-term compatibility wrapper

## 4. Surface That Was Removed or Narrowed

The old public scalar surface included many direct scalar parameters such as:

- `steps`
- `capture_positions`
- `observer_enabled`
- `runtime_decision_source`
- `movement_model`
- `bridge_theta_split`
- `bridge_theta_env`
- `bridge_sustain_ticks`
- collapse-shadow scalar thresholds
- contact/boundary scalars
- movement experiment scalars
- diagnostic toggles

That scalar surface is no longer the public call shape.

Current public narrowing outcome:

- `run_simulation(...)` no longer exposes a long scalar signature
- `test_run_main.py` now passes existing grouped settings structures instead of re-spelling a wide constructor surface
- temporary `analysis/engineering_reports/developments/...` callers are no longer treated as a maintained compatibility target

## 5. Files Changed

### Core Harness Files

- `test_run/test_run_experiments.py`
- `test_run/test_run_main.py`
- `test_run/test_run_v1_0.py`

### Historical Temporary Direct Callers

- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/run_phase1_contact_impedance_doe.py`
- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/run_fr_authority_doe.py`
- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/run_frontcurv_mirrored_distance_aspect_size_sep_range_doe.py`
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/run_runtime_collapse_source_confirmation.py`
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/run_cohesion_source_doe.py`
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/run_odw_posture_doe.py`
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/run_odw_clip_micro_doe.py`
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/run_cohesion_collapse_semantics_microbatch.py`
- `analysis/engineering_reports/developments/20260308/phase_cohesion_component_diagnostic/run_cohesion_component_diagnostic.py`
- `analysis/engineering_reports/developments/20260305/phase_viiid_movement_3b_doe_validation/run_movement_3b_doe.py`
- `analysis/engineering_reports/developments/20260305/phase_viiid1_movement_3b1_targeted_doe/run_movement_3b1_targeted_doe.py`
- `analysis/engineering_reports/developments/20260305/phase_viiid2_movement_precontact_explore/run_movement_precontact_explore.py`
- `analysis/engineering_reports/developments/20260305/phase_viiic_followup_movement_geometry/build_phase_viiic_followup.py`

## 6. Compatibility Surface Decision

Long-term dual interface support was **not** kept.

Engineering decision in this round:

- normalize the maintained harness surface inside `test_run/`
- avoid preserving the old wide scalar public call as a second public surface

Temporary caller note:

- `analysis/engineering_reports/developments/...` scripts are historical experiment artifacts
- they are not part of the maintained public harness surface going forward

## 7. Measured Outcome

Measured current state versus `HEAD`:

- `test_run/test_run_main.py`
  - total lines: `1109 -> 656`
  - largest function `main()`: `493 -> 512`
- `test_run/test_run_experiments.py`
  - total lines: `1379 -> 1400`
  - largest function `run_simulation()`: `647 -> 651`

Interpretation:

- public interface narrowing succeeded
- `test_run_main.py` parameter shuttle visibly narrowed
- the short-lived typed dataclass surface was removed in favor of lighter grouped mappings
- total file weight in `test_run_experiments.py` is still slightly above `HEAD`
- `main()` in `test_run_main.py` is still too heavy to count as fully accepted simplification

## 8. Validation

### A. Static / Compile Validation

Validated with:

```powershell
python -m py_compile `
  test_run/test_run_experiments.py `
  test_run/test_run_main.py `
  test_run/test_run_v1_0.py `
  test_run/test_run_anchor_regression.py
```

Result:

- pass

### B. Anchor Regression

Validated with:

```powershell
python test_run/test_run_anchor_regression.py
```

Result:

```text
[off] ok
[hybrid_v2] ok
[intent_unified_spacing_v1] ok
mismatch_count=0
```

### C. Direct Caller Smoke Validation

Current maintained-surface rule:

- temporary `analysis/engineering_reports/developments/...` scripts are no longer part of the maintained validation target

Result:

- no direct-caller smoke is required for the maintained `test_run/` surface in the current state

## 9. Honest Classification

Checklist classification for this round:

- `Partial Cleanup`

Reason:

- public interface narrowing is real
- routine anchor regression stayed stable
- no long-term compatibility surface was left behind
- temporary development scripts were explicitly de-scoped from maintained compatibility
- however, `test_run_main.py::main()` is still too heavy for `Accepted Simplification`
- total file weight in `test_run/test_run_experiments.py` also did not decrease overall

## 10. Non-Claim Statement

This record does **not** claim:

- runtime mechanism improvement
- observer semantics redesign
- movement/combat behavior change
- battle-report doctrine change

This record claims only:

- bounded public harness interface normalization
- removal of the short-lived typed grouped surface in favor of lighter grouped mappings
- stable non-semantic validation outcome
