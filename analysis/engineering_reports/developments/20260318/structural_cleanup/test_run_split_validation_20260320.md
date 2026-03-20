# Test Run Split Validation Report (2026-03-20)

Status: split validation  
Scope: maintained spine boundary review after helper migration and old-launcher deletion  
Classification: structural validation / non-runtime-semantic

## 1. Boundaries Reviewed

This report reviews the boundaries currently retained in the maintained `test_run` surface:

- `test_run/test_run_entry.py`
- `test_run/test_run_scenario.py`
- `test_run/test_run_execution.py`
- `test_run/test_run_telemetry.py`
- active auxiliary surface:
  - `test_run/battle_report_builder.py`
  - `test_run/brf_narrative_messages.py`
  - `test_run/test_run_v1_0_viz.py`

Deleted old launcher / transitional shells:

- `test_run/test_run_main.py` already deleted before this round
- `test_run/test_run_v1_0.py` deleted in this round
- `test_run/test_run_experiments.py` deleted in this round

## 2. Four-Question Validation

### Q1. Did maintained launcher / maintained hot path get lighter?

Yes.

Concrete gains:

- `test_run/test_run_entry.py` no longer imports `test_run_v1_0 as core`
- the maintained launcher no longer routes through any old launcher shell
- old launcher files were physically removed instead of being kept as ambiguous shells

### Q2. Did import / dependency burden get lighter?

Yes, with one important nuance.

Positive change:

- the old `entry -> core` and `scenario -> core` dependency pattern is gone
- canonical ownership is now direct:
  - entry -> scenario / execution / BRF / viz
  - scenario -> execution constants/class only

Nuance:

- `test_run/test_run_execution.py` became heavier because it absorbed `TestModeEngineTickSkeleton`

Engineering judgment:

- this is an acceptable trade if the result is one canonical engine-adjacent host instead of one more historical helper shell

### Q3. Did old-host removability improve?

Yes.

This round achieved the strongest possible answer:

- the old hosts were removed

Specifically:

- `test_run_v1_0.py` is no longer “closer to deletable”; it is deleted
- `test_run_experiments.py` is no longer “closer to deletable”; it is deleted

### Q4. Was duplicated logic / duplicated ownership introduced?

No deliberate duplicated ownership remains in the maintained path.

Canonical ownership after the round:

- launcher/export/viz orchestration -> `test_run_entry.py`
- scenario/archetype/build helper surface -> `test_run_scenario.py`
- engine-adjacent harness skeleton and execution host -> `test_run_execution.py`
- telemetry/observer-side collection -> `test_run_telemetry.py`
- BRF assembly -> `battle_report_builder.py`
- BRF narrative library -> `brf_narrative_messages.py`
- renderer -> `test_run_v1_0_viz.py`

## 3. Keep / Reject Decision By Boundary

### Keep

- `entry` vs `scenario`
  - kept because the launcher no longer carries archetype/build helper ownership
- `execution` vs `telemetry`
  - kept because it remains the approved and useful structural boundary
- active auxiliary surface vs maintained launcher
  - kept because BRF and viz are now treated as active auxiliary surface rather than as old launcher debt

### Reject / Retire

- transitional helper host pattern
  - rejected by deleting `test_run_v1_0.py`
- transitional compatibility shell pattern
  - rejected by deleting `test_run_experiments.py`

## 4. Honest Cost

This round did not make every maintained file smaller.

Current line counts after migration:

- `test_run/test_run_entry.py`: `464`
- `test_run/test_run_scenario.py`: `781`
- `test_run/test_run_execution.py`: `1726`
- `test_run/test_run_telemetry.py`: `535`

So this round should not be described as “everything got shorter”.

It should be described more precisely as:

- old launcher / transitional shells were eliminated
- canonical ownership became explicit
- maintained hot path lost an unnecessary historical host

## 5. Overall Validation Result

Under the tightened governance rule:

- keep splits only if they reduce maintained hot-path burden or sharpen an approved boundary

current judgment is:

- retained splits are justified

Reason:

- old-host removability is no longer hypothetical; it has been achieved
- the maintained launcher path is now direct and single-ground-truth
- the most problematic historical helper host has been removed

No runtime semantics changed in this turn.
