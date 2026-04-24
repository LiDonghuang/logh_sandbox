# PR9 Phase II alpha_safe_max Public Surface Removal Record 20260419

Date: 2026-04-19
Scope: harness/config public-surface cleanup only
Primary area: `test_run` public settings surface and active repo readme

## Purpose

This record captures the removal of `runtime.physical.fire_control.alpha_safe_max`
from the active public `test_run` configuration surface.

This is a public-surface cleanup.
It is not a runtime mechanism change.

## Verified Active Truth Before Removal

Current active code-path audit showed:

- `alpha_safe_max` was exposed in `test_run/settings_accessor.py`
- `alpha_safe_max` existed in `test_run/test_run_v1_0.runtime.settings.json`
- `alpha_safe_max` was described in `test_run/test_run_v1_0.settings.comments.json`
- `README.md` still listed it as a documented surface

But current active runtime did **not** read it.

Current active runtime instead clamps `fire_quality_alpha` directly to `[0.0, 1.0]`
inside `resolve_combat(...)`.

So `alpha_safe_max` had become a dormant public knob rather than an active mechanism input.

## Files Changed

- [test_run/settings_accessor.py](E:/logh_sandbox/test_run/settings_accessor.py)
- [test_run/test_run_v1_0.runtime.settings.json](E:/logh_sandbox/test_run/test_run_v1_0.runtime.settings.json)
- [test_run/test_run_v1_0.settings.comments.json](E:/logh_sandbox/test_run/test_run_v1_0.settings.comments.json)
- [README.md](E:/logh_sandbox/README.md)

## What Changed

- removed `alpha_safe_max` from the active runtime-facing settings path map
- removed `alpha_safe_max` from the maintained runtime settings JSON
- removed `alpha_safe_max` from the maintained settings comments JSON
- removed the active README mention

## What Did Not Change

- no runtime combat formula changed
- no `EngineTickSkeleton` behavior changed
- no `fire_quality_alpha` semantics changed
- no historical archive or old analysis document was back-edited
- no governance file was modified

## Scope Read

The correct read of this cleanup is:

- active public surface narrowing

not:

- runtime fire-control redesign
- combat semantics change
- retrospective rewriting of historical records
