# PR9 Phase II - Subtraction Cleanup Prestart Dual-Posture Baseline Refresh Record

Date: 2026-04-22  
Scope: baseline refresh before subtraction-only structural cleanup  
Status: completed

## 1. Exact Anchor State

These baselines were captured before the authorized subtraction-only cleanup.

- branch: `eng/dev-v2.1-formation-only`
- commit: `a4b5ce2b7dba`
- workspace: `dirty`
- anchor label: `a4b5ce2b7dba_dirty_pre_subtraction_cleanup`

This refresh is for **no-drift structural cleanup validation** only. It is not a
new behavior proposal, baseline promotion, or mechanism acceptance record.

## 2. Refreshed Baselines

Maintained default posture:

- switch: `runtime.physical.local_desire.experimental_signal_read_realignment_enabled = false`
- [battle_36v36](../../../reference_notes/eng_dev-v2.1-formation-only_a4b5ce2b7dba_dirty_pre_subtraction_cleanup_default_switch_false_battle_36v36_baseline_20260422.json)
- [battle_100v100](../../../reference_notes/eng_dev-v2.1-formation-only_a4b5ce2b7dba_dirty_pre_subtraction_cleanup_default_switch_false_battle_100v100_baseline_20260422.json)
- [neutral_36](../../../reference_notes/eng_dev-v2.1-formation-only_a4b5ce2b7dba_dirty_pre_subtraction_cleanup_default_switch_false_neutral_36_baseline_20260422.json)
- [neutral_100](../../../reference_notes/eng_dev-v2.1-formation-only_a4b5ce2b7dba_dirty_pre_subtraction_cleanup_default_switch_false_neutral_100_baseline_20260422.json)

Current behavior-line experimental posture:

- switch: `runtime.physical.local_desire.experimental_signal_read_realignment_enabled = true`
- [battle_36v36](../../../reference_notes/eng_dev-v2.1-formation-only_a4b5ce2b7dba_dirty_pre_subtraction_cleanup_experimental_switch_true_battle_36v36_baseline_20260422.json)
- [battle_100v100](../../../reference_notes/eng_dev-v2.1-formation-only_a4b5ce2b7dba_dirty_pre_subtraction_cleanup_experimental_switch_true_battle_100v100_baseline_20260422.json)
- [neutral_36](../../../reference_notes/eng_dev-v2.1-formation-only_a4b5ce2b7dba_dirty_pre_subtraction_cleanup_experimental_switch_true_neutral_36_baseline_20260422.json)
- [neutral_100](../../../reference_notes/eng_dev-v2.1-formation-only_a4b5ce2b7dba_dirty_pre_subtraction_cleanup_experimental_switch_true_neutral_100_baseline_20260422.json)

Manifest:

- [dual posture manifest](../../../reference_notes/eng_dev-v2.1-formation-only_a4b5ce2b7dba_dirty_pre_subtraction_cleanup_dual_posture_baseline_manifest_20260422.json)

## 3. Refresh Summary

Maintained default posture:

- `battle_36v36`: `500` frames, first contact / damage `61 / 61`
- `battle_100v100`: `500` frames, first contact / damage `58 / 58`
- `neutral_36`: `447` frames, objective reached tick `427`
- `neutral_100`: `448` frames, objective reached tick `428`

Current behavior-line experimental posture:

- `battle_36v36`: `500` frames, first contact / damage `61 / 61`
- `battle_100v100`: `500` frames, first contact / damage `58 / 58`
- `neutral_36`: `447` frames, objective reached tick `427`
- `neutral_100`: `448` frames, objective reached tick `428`

Each refreshed baseline preserves:

- `initial_state`
- `execution_cfg`
- `runtime_cfg`
- `observer_cfg`
- `fleet_labels`
- `fleet_colors`
- `observer_telemetry`
- `combat_telemetry`
- full per-tick `position_frames`

## 4. No-Drift Use

These eight files are the comparison anchors for the authorized cleanup. Runtime
behavior must remain unchanged against the matching posture and scenario.
Debug-surface shape may change only if documented in the post-cleanup report.
