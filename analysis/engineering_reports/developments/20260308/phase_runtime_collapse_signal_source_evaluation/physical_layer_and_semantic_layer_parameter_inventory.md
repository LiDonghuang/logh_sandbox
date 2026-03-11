# Physical Layer and Semantic Layer Parameter Inventory

## Purpose

This note inventories low-level runtime parameters and constants that are currently relevant to:

- physical spacing
- movement separation
- post-move projection
- fire-control low-level behavior
- cohesion / collapse semantics

The goal is classification, not refactor.

## Scope Boundary

- No runtime change is authorized by this note.
- This note does not redefine parameter semantics.
- This note separates:
  - already-exposed settings
  - hidden engine constants
  - semantic multipliers introduced only in the experimental harness

## Layer Classification

### Physical Layer

Parameters/constants that directly influence motion, spacing, collision avoidance, fire-quality, or battlefield constraints.

### Semantic Layer

Parameters/constants that define how runtime or observer systems interpret geometry, fragmentation, cohesion, or collapse.

### Cross-Layer Reuse Risk

Parameters that currently serve both physical and semantic roles.

## Inventory

### A. Already Exposed in `test_run/test_run_v1_0.settings.json`

#### `battlefield.min_unit_spacing`

- Current role: cross-layer reused
- Physical usage:
  - initial deployment spacing
  - movement `separation_radius`
  - post-move minimum spacing threshold
- Semantic usage:
  - `cohesion_v2` fragmentation graph radius
  - `cohesion_v3_shadow` / `v3_test` `c_conn` graph radius
  - `cohesion_v3_shadow` scale reference base `r_ref`
- Code references:
  - `test_run/test_run_v1_0.py`
  - `runtime/engine_skeleton.py:222`
  - `runtime/engine_skeleton.py:341`
  - `runtime/engine_skeleton.py:358`
  - `runtime/engine_skeleton.py:499`
- Classification:
  - `cross-layer reuse risk`

#### `runtime.physical.fire_control.fire_quality_alpha`

- Current role: exposed physical / combat-adjacent low-level parameter
- Meaning:
  - directional fire-quality coefficient
- Code references:
  - `test_run/test_run_v1_0.py`
  - `runtime/engine_skeleton.py:2208`
  - `runtime/engine_skeleton.py:2418`
- Classification:
  - `physical layer`

#### `runtime.physical.fire_control.alpha_safe_max`

- Current role: documented safety reference only
- Meaning:
  - governance / engineering safe upper bound for `fire_quality_alpha`
- Code references:
  - `test_run/test_run_v1_0.settings.json`
- Classification:
  - `reference-only guardrail`

#### `runtime.physical.contact_model.contact_hysteresis_h`

- Current role: exposed runtime low-level parameter
- Meaning:
  - contact hysteresis band ratio
- Code references:
  - `test_run/test_run_v1_0.py`
  - `runtime/engine_skeleton.py:2197`
- Classification:
  - `physical/contact model`

#### `runtime.physical.contact_model.fsr_strength`

- Current role: exposed runtime low-level parameter
- Meaning:
  - FSR relaxation strength
- Code references:
  - `test_run/test_run_v1_0.py`
  - `runtime/engine_skeleton.py:1018`
- Classification:
  - `physical/contact model`

#### `runtime.physical.boundary.enabled`

- Current role: exposed runtime low-level switch
- Meaning:
  - master boundary mechanism switch
- Code references:
  - `test_run/test_run_v1_0.py`
  - `runtime/engine_skeleton.py:850`
- Classification:
  - `physical layer`

#### `runtime.physical.boundary.soft_strength`

- Current role: exposed runtime low-level parameter
- Meaning:
  - soft boundary force multiplier
- Code references:
  - `test_run/test_run_v1_0.py`
  - `runtime/engine_skeleton.py:522`
  - `runtime/engine_skeleton.py:868`
- Classification:
  - `physical layer`

#### `runtime.physical.boundary.hard_enabled`

- Current role: exposed runtime low-level switch
- Meaning:
  - hard boundary clamp switch
- Code references:
  - `test_run/test_run_v1_0.py`
- Classification:
  - `physical layer`

#### `runtime.physical.movement_low_level.alpha_sep`

- Current role:
  - exposed low-level movement coefficient
  - weight for soft separation and boundary contribution inside movement vector composition
- Code references:
  - `test_run/test_run_v1_0.py`
  - `runtime/engine_skeleton.py:503`
  - `runtime/engine_skeleton.py:917`
  - `runtime/engine_skeleton.py:953`
  - `runtime/engine_skeleton.py:965`
- Classification:
  - `physical layer`

### B. Hidden Engine Constants / Internal Knobs (Not Exposed)

#### Penetration correction split factor `0.5`

- Current role:
  - equal split of hard projection correction across the two colliding units
- Code references:
  - `runtime/engine_skeleton.py:1198`
  - `runtime/engine_skeleton.py:1203`
- Operational meaning:
  - if post-move pair distance falls below `min_unit_spacing`, each unit receives half the correction
- Classification:
  - `physical layer`
- Status:
  - restored to hard-coded engine behavior after cleanup review

#### `rpg_delta = 0.1 * min_unit_spacing`

- Current role:
  - internal diagnostic / geometry threshold derived from spacing
- Code reference:
  - `runtime/engine_skeleton.py:1393`
- Classification:
  - `internal diagnostic / geometry heuristic`

### C. Experimental Semantics-Only Knobs (Harness-Level, Not Baseline)

These were introduced in `test_run/test_run_v1_0.py` during the cohesion-collapse semantics review.

#### `v2_connect_radius_multiplier`

- Current role:
  - rescales only the `cohesion_v2` fragmentation / LCC graph radius
- Code references:
  - `test_run/test_run_v1_0.py`
- Does not affect:
  - physical separation
  - projection
  - `dispersion`
  - `elongation`
  - `outlier_mass`
- Classification:
  - `semantic layer`

#### `v3_connect_radius_multiplier`

- Current role:
  - rescales only the `c_conn` graph radius inside `cohesion_v3_shadow`
- Code references:
  - `test_run/test_run_v1_0.py`
- Does not affect:
  - physical spacing
  - `rho`
  - `c_scale`
- Classification:
  - `semantic layer`

#### `v3_r_ref_radius_multiplier`

- Current role:
  - rescales only the `r_ref` term used by `rho / c_scale`
- Code references:
  - `test_run/test_run_v1_0.py`
- Status:
  - experimentally supported in harness
  - intentionally held at `1.0` in the current review
- Classification:
  - `semantic layer`

## Current Structural Problem

The current system still binds one variable chain:

`min_unit_spacing -> separation_radius -> semantic connectivity radius`

This causes a physical spacing parameter to also define:

- `cohesion_v2` fragmentation semantics
- `cohesion_v3_shadow` / `v3_test` connectivity semantics
- part of `v3` scale semantics

This is the core issue surfaced by the recent semantics review.

## Externalization Judgment

### Should Eventually Be Explicitly Visible

These are reasonable future externalization candidates:

- `separation_radius` as a distinct physical parameter
- semantic connectivity multipliers / semantic graph radii

Reason:

- they are low-level but structurally important
- they affect interpretation and debugging
- they are currently harder to audit than `fire_quality_alpha` or `boundary.soft_strength`

### Should Not Be Externalized Casually

- internal one-off heuristics whose semantics are not yet stable
- diagnostic-only derived thresholds that are not part of an approved public interface

## Recommended Future Structure

If future externalization is authorized, the cleaner target shape is:

- `runtime.physical`
  - spacing
  - separation
  - projection
  - fire-control low-level coefficients
  - boundary low-level coefficients
- `runtime.semantic`
  - cohesion-connectivity semantics
  - collapse-signal source semantics

This avoids mixing:

- physical motion constants
- semantic interpretation constants

inside one undifferentiated `runtime` surface.

## Engineering Judgment

1. `runtime.physical.fire_control.*` and `runtime.physical.contact_model.*` are already examples of visible low-level runtime controls.
2. `alpha_sep` is now exposed under `runtime.physical.movement_low_level`.
3. The penetration split factor has been restored to hard-coded `0.5` engine behavior.
4. Any future tuning of low-level movement physics should be treated as dedicated movement experimentation.

## Current Recommendation

- Keep current runtime baseline unchanged.
- Keep the currently hidden penetration split factor hard-coded at `0.5`.
- Avoid introducing additional low-level movement knobs unless a dedicated movement experiment requires them.
- Use this inventory as the reference for any future "physical layer parameter exposure" discussion.

