# Test Run A5 Governance Request (2026-03-20)

Status: governance-facing engineering report  
Scope: test-only / harness-only cleanup status, blocker escalation, and requested governance decisions

## 1. Purpose

This document reports the current state of the `Phase A / A5` `test_run` cleanup effort after multiple subtraction-focused rounds.

It exists because the remaining high-value cleanup is no longer a clearly safe local refactor.

The current blocker is not a runtime bug.  
The blocker is that the remaining visible weight is concentrated in a public harness entrypoint that is already consumed by multiple external scripts.

## 2. Working Rules Used During These Rounds

Engineering worked under the repo AI contract and the local `test_run` rules:

- subtraction first
- no silent fallback
- no silent refactor
- routine cleanup uses 3-run anchor validation
- do not count helper growth as simplification
- do not silently drift into runtime / observer / viz / battle-report redesign

The acceptance standard used for simplification claims was:

- smaller human-facing entrypoint
- narrower interface
- quieter default stdout
- less fallback / wrapper / parameter shuttling

## 3. Method Used Across These Rounds

The overall method across the recent A5 rounds was:

1. Tighten repo-side engineering discipline first.
2. Audit `test_run/` and classify which files are true A5 launcher/plumbing problems.
3. Apply subtraction-first cleanup in `test_run/test_run_main.py`.
4. Stabilize routine regression validation so future cleanup does not keep rebuilding the comparator from scratch.
5. Enter a bounded multi-file round limited to `test_run/test_run_main.py` and `test_run/test_run_experiments.py`.
6. Stop once the next meaningful reduction appeared to require a public interface decision rather than a local cleanup decision.

## 4. Concrete Progress

### A. Discipline Hardening

Repo-side engineering discipline was hardened so future A5 work is judged more strictly.

This includes:

- root execution contract hardening
- local `test_run/` cleanup rules
- operational simplification acceptance checklist

### B. `test_run_main.py` Cleanup Progress

`test_run/test_run_main.py` has been the main A5 target.

Observed progress:

- file total reduced from `1109` lines to `706` lines
- repeated launcher-side parameter transport was reduced
- repeated `settings_api.get(...)` call noise was reduced through grouped access
- default routine validation is now able to run quietly against a fixed anchor script
- no viz / battle-report file body rewrite was mixed into this work

Important limitation:

- the main human-facing entrypoint did **not** become clearly lighter
- `main()` moved from `490` lines to `559` lines

Engineering assessment:

- this is not safe to report as `accepted simplification`
- at best, this area currently counts as `partial cleanup` plus substantial boundary clarification

### C. Anchor Regression Stabilization

Routine A5 validation has now been fixed into a reusable script:

- `test_run/test_run_anchor_regression.py`

This removed the previous failure mode where engineering had to keep rebuilding the routine comparator.

The fixed routine behavior now is:

- load `docs/a5_iteration0_baseline_anchor_20260318.json`
- use the first three rows for fixture `neutral_close_100v100`
- compare the established routine modes:
  - `off`
  - `hybrid_v2`
  - `intent_unified_spacing_v1`

Current routine validation command:

```powershell
python test_run/test_run_anchor_regression.py
```

Current result:

```text
[off] ok
[hybrid_v2] ok
[intent_unified_spacing_v1] ok
mismatch_count=0
```

### D. `test_run_experiments.py` Multi-File Round

A bounded multi-file round was started in:

- `test_run/test_run_experiments.py`

What was done:

- kept the public `run_simulation(...)` signature unchanged
- reduced repeated engine-attribute assignment boilerplate
- reduced repeated per-fleet container initialization boilerplate
- reduced repeated telemetry append / normalization boilerplate
- preserved routine regression behavior

Important limitation:

- file total increased from `1379` lines to `1393` lines
- `run_simulation()` increased from `648` lines to `662` lines

Engineering assessment:

- this result is **not** accepted simplification
- it is more accurately `refactor without accepted simplification`

## 5. Key Problem Now

The remaining visible weight is concentrated in:

- `test_run/test_run_experiments.py`
- especially `run_simulation(...)`

The central problem is no longer just local repetition.

The remaining weight is strongly tied to the public function surface itself:

- wide scalar argument list
- wide telemetry assembly responsibilities
- many direct callers outside `test_run_main.py`

Because of that, significant additional reduction likely requires one or more of:

- grouped context / dict interface
- narrower public launcher/experiment interface
- direct-caller migration plan
- explicit compatibility policy

Those are governance-sensitive decisions, not safe silent cleanup.

## 6. Why Engineering Is Stopping Here

Engineering is stopping because the next likely high-value cut appears to cross from:

- local subtraction-first cleanup

into:

- public interface redesign

That boundary matters because `run_simulation(...)` is already called directly by multiple non-`test_run_main.py` scripts under `analysis/...`.

Therefore, continuing without governance direction would risk:

- silent interface drift
- hidden caller breakage
- accidental promotion of an A5 cleanup turn into a broader major item

## 7. Governance Decisions Requested

Governance review is requested on the following points:

1. May `test_run/test_run_experiments.py::run_simulation(...)` be redesigned from a wide scalar public interface into grouped context/dict inputs?
2. If yes, should direct callers under `analysis/...` be migrated in the same change, or is a temporary compatibility surface authorized?
3. Should that work be classified under `R-11 - Major Change Recording` because it affects the public `test_run` interface?
4. If governance does **not** authorize public interface change yet, should A5 remain focused only on launcher-level cleanup in `test_run/test_run_main.py`, even if visible gains are now marginal?

## 8. Repo Paths for Governance Review

### Core Rules / Context

- `AGENTS.md`
- `test_run/AGENTS.md`
- `docs/engineering/SIMPLIFICATION_ACCEPTANCE_CHECKLIST.md`
- `docs/phase_a_governance_update_20260319.md`
- `docs/phase_a_thread_reading_list_20260319.md`

### Current A5 Validation / Records

- `docs/a5_iteration0_baseline_anchor_20260318.md`
- `docs/a5_iteration0_baseline_anchor_20260318.json`
- `docs/test_run_anchor_regression_policy_20260319.md`
- `docs/test_run_harness_cleanup_record_20260319.md`
- `docs/test_run_a5_governance_request_20260320.md`

### Current Working Files

- `test_run/test_run_main.py`
- `test_run/test_run_experiments.py`
- `test_run/test_run_anchor_regression.py`
- `test_run/test_run_v1_0.py`
- `test_run/settings_accessor.py`
- `test_run/test_run_v1_0.runtime.settings.json`
- `test_run/test_run_v1_0.testonly.settings.json`
- `test_run/test_run_v1_0.settings.comments.json`

### Sample Direct Callers That Make `run_simulation(...)` Governance-Relevant

- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/run_phase1_contact_impedance_doe.py`
- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/run_fr_authority_doe.py`
- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/run_frontcurv_mirrored_distance_aspect_size_sep_range_doe.py`
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/run_runtime_collapse_source_confirmation.py`
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/run_odw_posture_doe.py`
- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/run_cohesion_source_doe.py`
- `analysis/engineering_reports/developments/20260308/phase_cohesion_component_diagnostic/run_cohesion_component_diagnostic.py`
- `analysis/engineering_reports/developments/20260305/phase_viiid_movement_3b_doe_validation/run_movement_3b_doe.py`
- `analysis/engineering_reports/developments/20260305/phase_viiid1_movement_3b1_targeted_doe/run_movement_3b1_targeted_doe.py`
- `analysis/engineering_reports/developments/20260305/phase_viiid2_movement_precontact_explore/run_movement_precontact_explore.py`
- `analysis/engineering_reports/developments/20260305/phase_viiic_followup_movement_geometry/build_phase_viiic_followup.py`

## 9. Current Engineering Classification

Current honest classification of the latest state:

- `test_run/test_run_main.py`: `partial cleanup`
- `test_run/test_run_experiments.py`: `refactor without accepted simplification`
- fixed routine comparator: successful and reusable
- next meaningful reduction: blocked on governance decision

## 10. Non-Claim Statement

This report does **not** claim:

- runtime mechanism redesign success
- observer semantics redesign
- accepted simplification of `run_simulation(...)`
- authority to change public interface without approval

This report exists to hand governance a concrete decision point, not to overstate progress.
