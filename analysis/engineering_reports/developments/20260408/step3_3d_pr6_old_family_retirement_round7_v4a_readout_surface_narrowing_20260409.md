# Step3 3D PR6 - Old Family Retirement Round 7 - v4a Readout Surface Narrowing - 2026-04-09

## Scope

- baseline/runtime: no mechanism change
- target line: human-facing default readout surfaces for active `v4a`
- files:
  - `test_run/test_run_entry.py`
  - `test_run/test_run_v1_0_viz.py`
  - `test_run/battle_report_builder.py`

## Problem

After active `v4a` stopped depending on several legacy `v3a` movement support surfaces, the default human-facing readouts still exposed old-family values on `v4a` runs:

- `cohesion_decision_source_effective`
- `v3_connect_radius_multiplier_effective`
- `odw_posture_bias_*`
- collapse-source lines in the v4a-facing BRF run snapshot

This kept old-family interpretation visible by default even when those values no longer explained active `v4a` movement behavior.

## Decision

Shrink the default readout surface for `v4a`:

- keep legacy `v3*` readouts visible on `v3a`
- stop surfacing them by default on `v4a`

## Implementation

### `test_run/test_run_entry.py`

- `render_debug_context` now only carries:
  - `cohesion_decision_source_effective`
  - `v3_connect_radius_multiplier_effective`
  - `odw_posture_bias_*`

  when `movement_model_effective == "v3a"`

- battle BRF/run snapshot now only includes:
  - `runtime_decision_source_effective`
  - `collapse_decision_source_effective`

  when `movement_model_effective == "v3a"`

### `test_run/test_run_v1_0_viz.py`

- the default runtime debug block now reads:
  - `mode=... mov=v4a`
  - `sm=...`
  - event line

  on `v4a`

- the old `coh/csrc/odw/v3_connect` lines remain only for `v3a`

### `test_run/battle_report_builder.py`

- run configuration snapshot only emits the old runtime/collapse decision rows when the movement model is `v3a`

## Current read

This round is a true human-facing surface reduction:

- active `v4a` readout is smaller
- default interpretation surface is more honest
- no mechanism behavior changed
- no compatibility wrapper or fallback was added
