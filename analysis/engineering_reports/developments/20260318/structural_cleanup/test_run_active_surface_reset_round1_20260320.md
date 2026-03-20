# test_run Active Surface Reset Round 1

Date: 2026-03-20  
Status: Harness-only major item record  
Scope: active surface reset / minimal maintained spine implementation  
Classification: Partial Cleanup  

---

## 1. Identity

This round is the first code implementation step after the approved structural reset preparation.

It is:

- harness-only
- active-surface reset work
- non-runtime-semantic
- non-canonical
- non-viz-modernization

It is not:

- a runtime semantics rewrite
- a movement redesign
- a combat redesign
- a battle-report redesign
- a visualization modernization round

---

## 2. Active Spine Implemented

The maintained hot path now has a new minimal spine:

- `test_run/test_run_entry.py`
  - thin maintained entry
  - routine run orchestration only
- `test_run/test_run_scenario.py`
  - settings resolve
  - initial state build
  - grouped execution/runtime/observer config preparation
- `test_run/test_run_execution.py`
  - battle execution
  - maintained outputs
- `test_run/test_run_telemetry.py`
  - observer / bridge / collapse-shadow collection

Routine regression now runs through that spine:

- `test_run/test_run_anchor_regression.py`

---

## 3. Legacy Demotion Applied

The following files were demoted from primary maintained hosts:

- `test_run/test_run_experiments.py`
  - reduced to a thin transitional re-export shell
- `test_run/test_run_v1_0.py`
  - now forwards `main()` to `test_run/test_run_entry.py`
- `test_run/test_run_main.py`
  - remains available as a legacy full launcher surface
  - no longer defines the maintained hot path for routine run/regression

This round did not physically delete legacy heavy paths.

Status change applied first:

- primary maintained path moved off old mixed hosts
- legacy full-launcher path remains present
- viz / battle-report paths remain outside the maintained spine

---

## 4. Visible Structural Results

### A. Routine regression takeover

`test_run/test_run_anchor_regression.py` no longer patches old `test_run_main.py`.

It now calls:

- `test_run/test_run_entry.py::run_active_surface(...)`

That means the fixed routine `3-run` anchor now validates the new maintained spine directly.

### B. Old mixed execution host demoted

`test_run/test_run_experiments.py` line count:

- before: `1313`
- after: `38`

The heavy mixed execution/telemetry body moved out of that historical host.

### C. Maintained hot path detached from heavy optional paths

The maintained spine files do not import or depend on:

- `test_run/test_run_v1_0_viz.py`
- `test_run/battle_report_builder.py`
- `test_run/brf_narrative_messages.py`

### D. Default maintained run path switched

`test_run/test_run_v1_0.py::main()` now points to the new maintained entry:

- `test_run/test_run_entry.py`

This is an explicit active-surface reset decision.

---

## 5. Files Added

- `test_run/test_run_entry.py`
- `test_run/test_run_scenario.py`
- `test_run/test_run_execution.py`
- `test_run/test_run_telemetry.py`
- `analysis/engineering_reports/developments/20260318/structural_cleanup/test_run_active_surface_reset_round1_20260320.md`

## 6. Files Changed

- `test_run/test_run_anchor_regression.py`
- `test_run/test_run_experiments.py`
- `test_run/test_run_v1_0.py`

## 7. Files Left As Legacy / Transitional

- `test_run/test_run_main.py`
- `test_run/test_run_v1_0_viz.py`
- `test_run/battle_report_builder.py`
- `test_run/brf_narrative_messages.py`

---

## 8. Validation

### Static checks

Passed:

- `python -m py_compile test_run\test_run_telemetry.py test_run\test_run_scenario.py test_run\test_run_execution.py test_run\test_run_entry.py test_run\test_run_anchor_regression.py test_run\test_run_experiments.py test_run\test_run_v1_0.py test_run\test_run_main.py`

### Routine regression

Passed:

- `python test_run\test_run_anchor_regression.py`

Observed result:

- `[off] ok`
- `[hybrid_v2] ok`
- `[intent_unified_spacing_v1] ok`
- `mismatch_count=0`

### Maintained entry smoke

Passed:

- `python test_run\test_run_v1_0.py`

This now exercises the new maintained entry path rather than the old full launcher path.

---

## 9. Boundary Notes

This round did not split execution and telemetry into fully independent runtime packages.

What it did do:

- separate maintained entry from old launcher
- separate scenario build from old launcher
- separate execution host from old mixed `test_run_experiments.py`
- separate telemetry collection into its own module

That is enough to establish a new maintained spine for routine run and routine regression.

---

## 10. Classification Rationale

This round is recorded as `Partial Cleanup`.

Reason:

- the maintained hot path is now genuinely smaller and cleaner
- the old mixed execution host was materially demoted
- routine regression now validates the new spine directly

But:

- `test_run/test_run_main.py` still exists as a large legacy full launcher
- legacy heavy files are still present physically
- this is not yet a full deletion/freeze completion round

---

## 11. Explicit Non-Change Statement

No runtime semantics changed in this turn.
