# pr9_reference_axis_reverse_command_decoupling_record_20260418

## Scope

- runtime
- active battle / neutral movement-command semantics
- no public settings surface change

## What changed

The maintained runtime now decouples:

- fleet-level reference / coarse-body direction carrier
- signed movement command carrier

Active runtime owner:

- `runtime/engine_skeleton.py::_evaluate_target_with_v4a_bridge(...)`
- `runtime/engine_skeleton.py::_prepare_v4a_bridge_state(...)`

Current maintained read:

- `last_target_direction` now remains the unsigned fleet-level reference axis
- `movement_command_direction` now carries the signed command vector used for
  actual movement realization, including reverse command during post-contact
  spacing recovery

## Why this record exists

This is a major item because it materially changes active runtime interpretation
boundary between:

- reference-surface ownership
- movement-command ownership

It should therefore be recorded independently rather than silently folded into
older notes.

## Human-facing intent

This slice exists to prevent battle-side reverse / retreat command from flipping
the maintained reference frame together with it.

In plain language:

- fleets may be told to move backward
- but that backward command should not automatically become the new reference
  forward axis for formation reconstruction

## Boundary

This slice does **not** yet add a new explicit “backward retreat without
turning” low-level locomotion policy.

It only separates reference-axis ownership from reverse movement-command
ownership.

## Files in scope

- `runtime/engine_skeleton.py`
