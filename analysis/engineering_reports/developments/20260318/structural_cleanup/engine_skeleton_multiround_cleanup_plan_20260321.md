# Engine Skeleton Multi-Round Cleanup Plan

Status: Phase 0 Preparation  
Date: 2026-03-21  
Scope: Human-in-Codex bounded cleanup campaign

## Campaign Rule

Each round must have:

- one primary target
- one delete list
- one success test
- one validation summary

Do not mix:

- `__init__` normalization
- movement legacy retirement
- combat hot-path cleanup
- debug family retirement

inside the same implementation round.

## Round A — Dead Variable / Zero Placeholder Deletion

### Primary target

- delete low-risk dead locals from `integrate_movement(...)` and `resolve_combat(...)`

### Files allowed

- `runtime/engine_skeleton.py`

### Delete list

- `major_hat_x`
- `major_hat_y`
- `ar_ratio`
- `ar_forward_ratio`
- `precontact_gate`
- `axial_pull_x`
- `axial_pull_y`
- `attackers_to_target`

### Do not touch

- movement semantics
- combat semantics
- branch retirement decisions

### Success standard

- visible subtraction in hot path
- no new helpers unless strictly necessary
- no semantic drift

## Round B — `__init__` Active Surface Normalization

### Primary target

- make `__init__` read as active runtime surface plus active debug/reference surface, not one flat bag

### Files allowed

- `runtime/engine_skeleton.py`
- `test_run/test_run_execution.py` only if maintained debug-output names must be updated to preserve caller compatibility

### Delete / tighten list

- any remaining top-level internal-only state
- any top-level field that is neither active runtime knob nor active maintained debug/reference output

### Do not touch

- runtime semantics
- retirement decisions for `v1`, `v1_debug`, `diag4`, `RPG`, or combat assert families

### Success standard

- clearer active/debug/reference/internal separation
- fewer top-level fields or clearly narrower top-level surface

## Round C — Retirement Decision Round

### Primary target

- decide which legacy/reference families remain active and which are retired

### Families to decide

- `MOVEMENT_MODEL == "v1"`
- `COHESION_DECISION_SOURCE == "v1_debug"`
- `diag4`
- `RPG diagnostics`
- combat assert family

### Files allowed

- no code by default
- decision/record docs only unless governance explicitly upgrades scope

### Success standard

- each family lands in exactly one bucket:
  - maintained
  - retained reference
  - retired / approved for deletion

## Round D — Movement Legacy / Reference Reduction

### Primary target

- remove whatever Round C explicitly retires from `integrate_movement(...)`

### Files allowed

- `runtime/engine_skeleton.py`
- `test_run/test_run_execution.py` only if maintained caller glue truly requires it

### Delete list

- only the retired movement/reference families approved in Round C

### Do not touch

- active v2 movement semantics
- combat logic

### Success standard

- movement hot path shorter
- fewer legacy/reference branches near maintained path
- no compatibility growth

## Round E — `resolve_combat(...)` Hot-Path Cleanup

### Primary target

- reduce combat hot-path burden after retirement decisions are settled

### Files allowed

- `runtime/engine_skeleton.py`

### Delete / tighten list

- dead locals still remaining after Round A
- retired debug/reference families explicitly approved in Round C
- duplicated local bookkeeping that survives without maintained value

### Do not touch

- target assignment semantics
- damage semantics
- combat order / attrition semantics

### Success standard

- maintained combat path visibly lighter
- fewer debug/reference branches interleaved with active combat execution

## Acceptance Standard For Every Round

A round is not a cleanup success unless all four answers are clear:

1. maintained hot path is lighter
2. retired mechanisms are fewer
3. compatibility debt is lower
4. validation shows no semantic drift
