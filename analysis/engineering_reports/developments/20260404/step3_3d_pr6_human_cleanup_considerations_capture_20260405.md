# step3_3d_pr6 human cleanup considerations capture - 2026-04-05

Status: human direction capture  
Scope: current cleanup thread only  
Authority: explicit Human direction to be preserved for Engineering / Governance continuity; not canonical semantics authority

## Purpose

This note captures explicit Human judgments made during the current cleanup
thread so they do not remain only in chat context.

## Captured Human Direction

### 1. Simplicity is the highest-priority implementation constraint

Because the project contains a large amount of math-heavy and frequently revised
logic, Human explicitly judged that maintaining a simple code structure is more
important than preserving sprawling historical mechanism families.

Human also explicitly stated that prior uncontrolled code growth caused real
maintenance damage and should not be repeated.

### 2. Active mechanism retention rule

Human explicitly judged that what should basically remain in the active repo is:

- the mechanism actually used through the current `dev_v2.0` launcher path
- with the current `runtime.settings` and `testonly.settings` containers

Mechanisms outside that active read should be treated as old-family retirement
candidates, especially older 2D / pre-Panda3D families.

### 3. Settings/container truth rule

Human explicitly clarified the meaning of the layered settings files:

- `test_run/test_run_v1_0.runtime.settings.json`
  - current-value container for runtime-facing values
- `test_run/test_run_v1_0.testonly.settings.json`
  - current-value container for test-only values
- `test_run/test_run_v1_0.settings.comments.json`
  - authoritative comments surface

Human also explicitly required that:

- when old mechanisms/parameters are deleted, the corresponding settings keys must be deleted too
- JSON parameter values must truthfully connect to the active runtime mechanism
- parameters may move between `testonly` and `runtime` containers as ownership changes
- `settings.comments.json` must be updated in the same turn

### 4. Old mechanism retirement direction

Human explicitly judged that:

- `test_run/test_run_v1_0_viz.py` is an older 2D visual mechanism and should later be retired gradually where it is no longer on the current `v4a` hot path
- `runtime/engine_skeleton.py` still contains many old-mechanism residues and should later be retired gradually where they are no longer on the current `v4a` hot path
- `v3a` should be removed as soon as its supported-path / fallback role can be retired honestly

### 5. `test_mode` judgment

Human explicitly judged that:

- `test_mode = 2` is the only remaining mode worth preserving
- `test_mode != 2` no longer needs to be kept
- `test_mode` itself is now an old mechanism and should later be deleted rather than preserved indefinitely

## Engineering Interpretation

This Human direction means future cleanup should bias toward:

- smaller active public surface
- removal of legacy mode/fallback selectors once governance truth permits it
- synchronized code/settings/comments retirement
- gradual but real reduction of old `v3a` / old 2D residues

It also means future Engineering work should **not** interpret “legacy support”
as a default reason to keep historical surfaces alive.

