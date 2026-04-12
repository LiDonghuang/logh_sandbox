# step3_3d_pr6_neutral_battle_mechanism_unification_cleanup_record_20260408

## Scope
- test_run harness only
- active movement mechanism cleanup
- no runtime formula change
- no targeting change

## Intent
Apply the agreed rule:

- neutral uses battle's movement mechanism family
- not the reverse
- neutral-only legacy carriers should be deleted from the active v4a path

## Changes
1. `test_run/test_run_execution.py`
- `v4a` neutral transit no longer uses `_evaluate_target_with_fixture_objective()` as its active target / arrival carrier.
- For `v4a`, neutral fixture objective now enters `_evaluate_target_with_pre_tl_substrate()` and is treated as the same target-relation family with a different objective source.

2. `test_run/test_run_execution.py`
- neutral fixture objective support was added to `_evaluate_target_with_pre_tl_substrate()`:
  - objective source comes from fixture objective point
  - relation / close / brake / hold writeback stays on the shared battle-family surface
  - stop radius is consumed as the objective-side target front-gap semantic, not via the old neutral-only arrival path

3. `test_run/test_run_execution.py`
- the neutral fixture loop no longer force-clears:
  - `formation_terminal_active`
  - `formation_hold_active`
  - related latched state fields

## Explicit non-changes
- did not revert neutral to old arrival-only movement
- did not delete battle transition mechanisms
- did not reopen terminal/hold redesign
- did not modify runtime `engine_skeleton.py`

## Current read
- the old `v4a` neutral target/arrival special path has been removed from the active path
- neutral now enters the battle-family target relation carrier
- remaining battle/neutral behavioral differences, if still observed, are no longer explained by the removed neutral arrival path alone

