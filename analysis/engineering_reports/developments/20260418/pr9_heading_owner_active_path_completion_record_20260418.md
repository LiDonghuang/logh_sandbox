# PR9 Heading Owner Active Path Completion Record 20260418

## Scope

- Type: runtime boundary-lock completion record
- Layer: runtime active path
- Branch context: `eng/dev-v2.1-formation-only`

## Change

The maintained heading-memory owner in the active `v4a` bridge path has been re-locked from the harness bundle carrier back to runtime state.

Current active read:

- runtime-owned heading state: `BattleState.coarse_body_heading_current`
- compatibility / diagnostic mirror only: `bundle["movement_heading_current_xy"]`

Relevant path:

- `runtime/engine_skeleton.py::_prepare_v4a_bridge_state(...)`

## Why This Record Exists

The earlier heading-owner relock note captured the intended boundary, but current code truth had drifted:

- the hot path still read heading memory from `bundle["movement_heading_current_xy"]`
- `BattleState.coarse_body_heading_current` existed in schema and symmetric merge, but was not the active owner

This record marks the active-path completion of that relock.

## Resulting Boundary

- `last_target_direction`: reference / coarse-body axis input
- `coarse_body_heading_current`: runtime-owned fleet heading memory
- `movement_command_direction`: signed movement command
- `movement_heading_current_xy`: retained as a mirrored bundle/debug surface, not the active owner

## Validation

- `python -m py_compile runtime/engine_skeleton.py runtime/runtime_v0_1.py test_run/test_run_execution.py test_run/test_run_scenario.py test_run/test_run_entry.py`
- `battle` short smoke: `tick=1`, `coarse_body_heading_current` populated
- `neutral` short smoke: `tick=1`, `coarse_body_heading_current` populated
