# PR9 Formation Cold-Shell Subtraction Shortlist Note

Status: current review note
Date: 2026-04-12
Scope: static cold-shell truth audit before any bounded subtraction on `eng/dev-v2.1-formation-only`
Authority: engineering review note only; not canonical semantics authority

## Purpose

This note converts the current formation cold-shell audit into a short bounded review artifact for `PR #9`.

It does not implement deletion.
It does not lock the coarse-body boundary yet.
It does not propose locomotion separation yet.

Its only job is to separate:

- safe bounded deletion candidates
- inactive or weakly-justified shells that should remain pending explicit decision

## Active owner baseline

The maintained active formation burden is still primarily runtime-owned in:

- `runtime/engine_skeleton.py::_resolve_v4a_reference_surface(...)`
- `runtime/engine_skeleton.py::_prepare_v4a_bridge_state(...)`
- `runtime/engine_skeleton.py::_evaluate_target_with_v4a_bridge(...)`

`test_run/test_run_execution.py` currently acts as bundle-preparation carrier, especially through:

- `_FixtureExecutionSupport.build_fixture_expected_reference_bundle(...)`

That harness path seeds initial formation-side bundle state, but it does not own the maintained per-tick evolution.

## Verified classification

### A. Safe bounded deletion candidates

#### 1. `band_identity_by_unit`

Static basis:

- computed in `test_run/test_run_execution.py` during fixture reference bundle construction
- stored into the returned bundle in the same file
- no maintained reader was verified by current repository search

Current read:

- this field matches the direction away from strong band identity and slot-style shaping residue

#### 2. `initial_material_forward_phase_by_unit`

Static basis:

- initialized in `test_run/test_run_execution.py` during fixture reference bundle construction
- no maintained reader was verified by current repository search

Current read:

- this field does not currently justify continued maintained surface area

#### 3. `initial_material_lateral_phase_by_unit`

Static basis:

- initialized in `test_run/test_run_execution.py` during fixture reference bundle construction
- no maintained reader was verified by current repository search

Current read:

- this field does not currently justify continued maintained surface area

### B. Not safe deletion candidates in the current truth state

#### 1. `formation_terminal_latched_tick`

Static basis:

- seeded as `None` in `test_run/test_run_execution.py`
- still written by maintained runtime logic in `runtime/engine_skeleton.py`

Current read:

- this is not in the same class as the safe deletion candidates above
- current audit does not justify calling it cold in the same sense as single-write / zero-reader residue

#### 2. `formation_hold_latched_tick`

Static basis:

- seeded as `None` in `test_run/test_run_execution.py`
- still written by maintained runtime logic in `runtime/engine_skeleton.py`

Current read:

- this is not currently justified as a bounded deletion candidate

#### 3. `formation_hold_*`

Static basis:

- maintained runtime code still reads and rewrites hold-state fields in `runtime/engine_skeleton.py`
- hold-state branches still affect axis, center, extent, and reference speed handling when activated
- no maintained true-writer was verified that turns hold active in the current audited path

Current read:

- `formation_hold_*` should currently be treated as a runtime formation-state shell
- it is weakly activated in current truth, but not safely classifiable as dead
- Human has also explicitly indicated that hold should remain available as a future mechanism family

#### 4. `frozen_terminal_*`

Static basis:

- maintained runtime code still reads fixture freeze fields from `TEST_RUN_FIXTURE_CFG`
- maintained harness code currently resets those fields to inactive / `None`
- no maintained true-writer was verified that turns the frozen-terminal frame active in the current audited path

Current read:

- `frozen_terminal_*` should currently be treated as a fixture expected-position frame-freeze shell
- it should not be collapsed into the same category as `formation_hold_*`
- it is pending further decision, not part of the first bounded deletion slice

## Resulting PR #9 shortlist

Safe first bounded deletion slice after Human approval:

- `band_identity_by_unit`
- `initial_material_forward_phase_by_unit`
- `initial_material_lateral_phase_by_unit`

Not in that first slice:

- `formation_terminal_latched_tick`
- `formation_hold_latched_tick`
- `formation_hold_*`
- `frozen_terminal_*`

## Boundary of this note

This note records only the cold-shell subtraction shortlist.

It does not yet answer:

- the explicit coarse-body ownership boundary
- the acceptable long-term formation surface
- how transition / compensation burden should later move toward locomotion responsibility

Those belong to the next formation-only review steps after this shortlist is accepted.
