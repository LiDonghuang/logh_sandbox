# PR9 Phase II - Subtraction Cleanup Implementation and No-Drift Report

Date: 2026-04-22  
Scope: subtraction-only structural cleanup  
Status: completed

## 1. Battle-Read Result

This cleanup was not intended to improve or weaken battle behavior. It only
removed or narrowed structural surfaces that could obscure owner/path truth.

Observed validation result:

- maintained default posture remained behavior-identical to its refreshed
  pre-cleanup baselines
- experimental behavior-line posture remained behavior-identical to its
  refreshed pre-cleanup baselines
- battle and neutral frames did not drift in unit positions, orientation,
  velocity, HP, target lines, or fleet-body summaries

The only intentional visible-surface change is debug naming/content for the
local maneuver / back-off diagnostic field.

## 2. Exact Cleanup Edits

Runtime cleanup:

- retired `_select_targets_same_tick(...)`
- changed the post-movement combat call site to call
  `_compute_unit_intent_target_by_unit(...)` directly
- changed same-tick target carrier reads from quiet `.get(...)` reads to
  fail-fast key checks
- preserved explicit `None` as the valid meaning of "no selected target"
- kept the experimental Unit-local maneuver / back-off behavior inline
- added no new helper extraction

Debug-surface cleanup:

- replaced the stale visible `relation_violation_severity` debug export with
  `late_reopen_persistence`
- kept the visible local maneuver debug set minimal:
  `early_embargo_permission` and `late_reopen_persistence`

Harness cleanup:

- updated the focus-indicator export to read the same current debug field
  (`late_reopen_persistence`)
- did not move runtime ownership into `test_run`
- did not add fallback or compatibility aliases

## 3. Compile Check

Passed:

```powershell
python -m py_compile runtime\engine_skeleton.py test_run\settings_accessor.py test_run\test_run_scenario.py test_run\test_run_execution.py test_run\test_run_entry.py
```

## 4. No-Drift Comparison

Comparison anchors:

- [prestart dual-posture refresh record](pr9_phase2_subtraction_cleanup_prestart_dual_posture_baseline_refresh_record_20260422.md)
- [dual posture baseline manifest](../../../reference_notes/eng_dev-v2.1-formation-only_a4b5ce2b7dba_dirty_pre_subtraction_cleanup_dual_posture_baseline_manifest_20260422.json)

Compared for every posture and scenario:

- position frames with runtime debug removed
- runtime debug after removing only the declared local-desire debug field change
- combat telemetry
- observer telemetry excluding `tick_elapsed_ms`
- initial state
- execution / runtime / observer configs

Result table:

| Posture | Scenario | No-drift result |
|---|---|---|
| `switch=false` | `battle_36v36` | pass |
| `switch=false` | `battle_100v100` | pass |
| `switch=false` | `neutral_36` | pass |
| `switch=false` | `neutral_100` | pass |
| `switch=true` | `battle_36v36` | pass |
| `switch=true` | `battle_100v100` | pass |
| `switch=true` | `neutral_36` | pass |
| `switch=true` | `neutral_100` | pass |

No behavior drift was detected.

## 5. Explicit Debug-Surface Change

The local maneuver / back-off debug surface changed intentionally:

- before: `early_embargo_permission`, `relation_violation_severity`
- after: `early_embargo_permission`, `late_reopen_persistence`

This is a diagnostic payload change only. It does not alter the runtime
mechanism path, the Unit desire carrier shape, target ownership, locomotion
realization, or combat resolution.

## 6. No New Helper / Fallback / Compatibility Path

Confirmed:

- no new helper was added
- no fallback path was added
- no compatibility alias was added
- no wrapper replaced `_select_targets_same_tick(...)`
- no `v4a.engagement` wiring move was made
- no module split was made

## 7. Fail-Fast Wiring Result

The new fail-fast reads did not surface a missing-carrier or missing-key bug in
the validation set.

If a future run misses `unit_intent_target_by_unit` or a per-Unit selected-target
key, it will now fail explicitly rather than silently reading that case as "no
target."
