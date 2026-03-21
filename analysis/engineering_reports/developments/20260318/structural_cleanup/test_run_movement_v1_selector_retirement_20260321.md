# test_run movement_model=v1 Selector Retirement

Status: major item record  
Scope: test-only / harness-only  
Date: 2026-03-21

## Summary

The maintained `test_run` path no longer accepts `runtime.selectors.movement_model=v1`.

This round removes the remaining `test_run`-side compatibility residue after runtime-side `MOVEMENT_MODEL == "v1"` retirement:

- `test_run/test_run_scenario.py` no longer remaps `v1` to `v3a`
- `test_run/test_run_execution.py` now treats `v3a` as the only maintained effective movement model
- `test_run/test_run_v1_0.settings.comments.json` no longer advertises `v1` as a selector option

## Classification

This is a test-run / harness interface retirement record.

It is:

- not a runtime semantics change
- not a baseline replacement
- not a canonical rewrite

## Result

The maintained `test_run` movement selector surface is now:

- `baseline`
- `v3a`

If `v1` is requested, `test_run` now fails fast instead of silently remapping.
