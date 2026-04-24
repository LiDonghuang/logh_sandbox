# PR6 / dev_v2.1 v4a Restore Direct Runtime Cleanup

Status: major item record  
Date: 2026-04-08  
Scope: runtime + truth surface only  
Authority: local implementation record, not merge approval

## Summary

This round narrows the active `v4a` restore seam to a direct runtime read:

- `restore_term = restore_strength * normalize(restore_vector)`

The active `v4a` movement hot path no longer enters the older movement-side
personality / pursuit scaffold by way of neutralized placeholder values.

## Runtime Change

Active file:

- `runtime/engine_skeleton.py`

Current `v4a_active` read:

- direct restore vector
- direct target-direction contribution
- separation
- boundary
- existing expected-position gating / deadband

Removed from the active `v4a` movement path:

- `formation_rigidity`
- `pursuit_drive`
- `mobility_bias`
- `enemy_cohesion`
- `deep_pursuit_mode`
- `forward_gain`
- `cohesion_gain`
- `extension_gain`

These legacy movement-side reads remain on the non-`v4a` path only.

## Truth Surface Update

Updated files:

- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`
- `analysis/engineering_reports/developments/20260404/step3_3d_pr6_active_ownership_map_20260404.md`

Updated read:

- `restore_strength` is the single active public seam for `v4a` restore strength
- no hidden native scale is applied
- no old personality multiplier is applied
- current `v4a` restore seam does not depend on `runtime.selectors.cohesion_decision_source`

## Out of Scope

This round does not:

- reopen terminal / hold latching
- remove later FSR use of `formation_rigidity`
- change Targeting
- start old-family retirement
- redefine battle / neutral movement-family alignment
