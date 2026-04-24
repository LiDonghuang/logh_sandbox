# PR9 Phase II - Post-Subtraction Cleanup Dual-Posture Structural Anchor Record

Date: 2026-04-22  
Scope: structural anchor after accepted no-drift cleanup  
Status: recorded

## 1. Battle / Structure Read

This anchor records the current code state after the accepted subtraction-only
cleanup. The battle behavior is not being promoted or reinterpreted here.

The useful read is narrower:

- the same battle behavior remains available in both postures
- the target-selection wrapper was removed
- same-tick carrier reads now fail fast on missing keys
- the local maneuver debug surface now points at the current late reopen-space
  indicator rather than the older violation indicator

This is a structural reference state, not a behavior proposal.

## 2. Exact Current State

- branch: `eng/dev-v2.1-formation-only`
- commit: `a4b5ce2b7dba`
- workspace: `dirty`
- structural state: post accepted subtraction-only cleanup

Relevant accepted cleanup files in this structural state:

- `runtime/engine_skeleton.py`
- `test_run/test_run_execution.py`
- [prestart dual-posture baseline refresh record](pr9_phase2_subtraction_cleanup_prestart_dual_posture_baseline_refresh_record_20260422.md)
- [subtraction cleanup implementation and no-drift report](pr9_phase2_subtraction_cleanup_implementation_and_no_drift_report_20260422.md)

## 3. Maintained Default Posture Anchor

Posture:

- `runtime.physical.local_desire.experimental_signal_read_realignment_enabled = false`

Reference read:

- maintained default remains the safe frozen path
- the cleanup made no behavior-bearing change under this posture
- no-drift validation passed for all four maintained scenarios

Baseline files used for no-drift validation:

- [battle_36v36](../../../reference_notes/eng_dev-v2.1-formation-only_a4b5ce2b7dba_dirty_pre_subtraction_cleanup_default_switch_false_battle_36v36_baseline_20260422.json)
- [battle_100v100](../../../reference_notes/eng_dev-v2.1-formation-only_a4b5ce2b7dba_dirty_pre_subtraction_cleanup_default_switch_false_battle_100v100_baseline_20260422.json)
- [neutral_36](../../../reference_notes/eng_dev-v2.1-formation-only_a4b5ce2b7dba_dirty_pre_subtraction_cleanup_default_switch_false_neutral_36_baseline_20260422.json)
- [neutral_100](../../../reference_notes/eng_dev-v2.1-formation-only_a4b5ce2b7dba_dirty_pre_subtraction_cleanup_default_switch_false_neutral_100_baseline_20260422.json)

## 4. Current Behavior-Line Experimental Posture Anchor

Posture:

- `runtime.physical.local_desire.experimental_signal_read_realignment_enabled = true`

Reference read:

- current behavior-line experimental posture remains test-only / experimental
- this posture is not promoted to maintained doctrine by this anchor
- the cleanup made no behavior-bearing change under this posture
- no-drift validation passed for all four maintained scenarios

Baseline files used for no-drift validation:

- [battle_36v36](../../../reference_notes/eng_dev-v2.1-formation-only_a4b5ce2b7dba_dirty_pre_subtraction_cleanup_experimental_switch_true_battle_36v36_baseline_20260422.json)
- [battle_100v100](../../../reference_notes/eng_dev-v2.1-formation-only_a4b5ce2b7dba_dirty_pre_subtraction_cleanup_experimental_switch_true_battle_100v100_baseline_20260422.json)
- [neutral_36](../../../reference_notes/eng_dev-v2.1-formation-only_a4b5ce2b7dba_dirty_pre_subtraction_cleanup_experimental_switch_true_neutral_36_baseline_20260422.json)
- [neutral_100](../../../reference_notes/eng_dev-v2.1-formation-only_a4b5ce2b7dba_dirty_pre_subtraction_cleanup_experimental_switch_true_neutral_100_baseline_20260422.json)

## 5. Anchor Boundary

This record means:

- current post-cleanup code state is the structural reference state for the
  next subtraction review
- both maintained and experimental postures have no-drift evidence against the
  pre-cleanup anchors
- debug-surface shape changed only as documented

This record does not mean:

- local maneuver / back-off behavior is maintained doctrine
- the experimental behavior-line family is accepted for promotion
- subtraction work is complete
- later structural rewiring, module split, or behavior optimization is
  authorized
