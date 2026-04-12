# PR6 Old-Family Retirement Round 1 - Restore Bridge Surface Removal

Status: bounded retirement record  
Date: 2026-04-05  
Scope: subtraction-first removal of stale `restore_strength` bridge surface after native `v4a` decoupling  
Authority: engineering working record; not broad retirement approval

## 1. Intent

This round removes one old-family residue that became stale immediately after the
native `v4a` `restore_strength` decoupling.

This is not a broad `v3a` / `v3_test` retirement round.

It is one bounded subtraction step.

## 2. What was removed

Removed stale summary/launcher surface:

- `battle_restore_bridge_active`

Files:

- `test_run/test_run_execution.py`
- `test_run/test_run_scenario.py`

## 3. Why this was safe to remove

Before decoupling, the label was intended to describe the active `v4a` reuse of
the old centroid-probe bridge.

After the decoupling implementation:

- active `v4a` now uses native runtime `v4a_restore_strength`
- active `v4a` no longer runs through:
  - `v3a_experiment = exp_precontact_centroid_probe`
  - `centroid_probe_scale = restore_strength`

So keeping a summary flag named `battle_restore_bridge_active` would now be a
stale old-family surface.

## 4. Honest classification

This round is:

- `Partial Cleanup`

Reason:

- one stale old bridge surface was removed
- active summary truth is narrower
- but no broad old-family retirement happened yet

## 5. Current post-round ownership read

Current active read is:

- targeting owner:
  - `runtime/engine_skeleton.py::resolve_combat()`
- active `restore_strength` owner:
  - `runtime.movement.v4a.restore_strength`
  - native runtime seam in `runtime/engine_skeleton.py`
- old `v3a.experiment` / `v3a.centroid_probe_scale`:
  - still live for `v3a`
  - no longer active `v4a` bridge surfaces

## Bottom Line

Round 1 retirement removed one stale bridge-era flag after decoupling.

The old families are not retired broadly yet, but one no-longer-true bridge
surface is now gone from the active launcher summary path.
