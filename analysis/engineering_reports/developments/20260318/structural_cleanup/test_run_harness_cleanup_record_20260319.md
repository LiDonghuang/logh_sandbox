# Test Run Harness Cleanup Record (2026-03-19)

Scope: harness-only / `test_run` launcher layer

## Summary

This record captures a launcher-layer cleanup in `test_run/test_run_main.py`.

Changes made:

- Removed silent fallback behavior for invalid launcher-consumed settings.
- Switched affected settings handling to explicit fail-fast validation.
- Reduced default stdout run summary to a small, human-readable set of lines.

## Non-Goals

- No engine/runtime mechanism change
- No observer/viz payload redesign
- No battle report semantics change
- No historical `analysis` rewrite

## Validation

- `python -m py_compile test_run/test_run_v1_0.py test_run/test_run_main.py test_run/test_run_experiments.py test_run/settings_accessor.py`
- 9-run A5 baseline anchor regression against `analysis/engineering_reports/developments/20260318/structural_cleanup/a5_iteration0_baseline_anchor_20260318.json`
  - Result: `mismatch_count=0`
- Default routine regression policy has now been reduced to a 3-run smoke set.
  - See `analysis/engineering_reports/developments/20260318/structural_cleanup/test_run_anchor_regression_policy_20260319.md`

## Notes

- This is a public `test_run` harness behavior cleanup, not a baseline/runtime mechanism change.
- Remaining wide launcher interfaces should be reviewed in later A5/A4 cleanup rounds.
