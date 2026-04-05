# PR6 Old-Family Retirement Round 2 - V3A Summary Surface Narrowing

Status: bounded retirement record  
Date: 2026-04-05  
Scope: remove `v3a`-specific carrier fields from active `v4a` default summary / BRF surface  
Authority: engineering working record; not broad retirement approval

## 1. Intent

After native `v4a` `restore_strength` decoupling, the default active `v4a`
summary surface should stop exporting old `v3a` carrier state as if it were
part of the active maintained path.

This round narrows that surface without retiring `v3a` itself.

## 2. What changed

Updated:

- `test_run/test_run_entry.py`
- `test_run/battle_report_builder.py`

Current behavior:

- `movement_v3a_experiment_effective`
- `centroid_probe_scale_effective`

are exported only when:

- `movement_model_effective == "v3a"`

They are no longer emitted on the default active `v4a` path.

## 3. Why this counts as old-family retirement work

These two fields are still valid for `v3a`.

But after the `restore_strength` decoupling, they no longer describe active
`v4a` behavior.

Keeping them in the default `v4a` summary / BRF surface would preserve an
unnecessary old-family shadow in the maintained active path.

## 4. Honest classification

This round is:

- `Partial Cleanup`

Reason:

- active human-facing surface became narrower
- but the underlying `v3a` family still remains available

## Bottom Line

Round 2 did not retire `v3a` broadly.

It removed two `v3a`-specific carrier exports from the default active `v4a`
summary/report surface, which makes the maintained path more truthful and
smaller.
