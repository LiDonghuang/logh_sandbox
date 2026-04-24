# PR9 Phase II Local Desire Signal Domain and Silent Fallback Cleanup Note 20260419

Status: engineering note for governance review only

Scope:

- document-only
- no runtime change
- no harness execution behavior change
- no baseline replacement

## 1. Purpose

This note records two linked findings from the fifth-slice follow-up review:

1. the current `local_desire` activation regime is not primarily blocked by a small
   `attack_range`; its main blocker is signal-domain collapse caused by the already
   accepted same-tick fire-cone-constrained target-selection path
2. the current maintained path still contains multiple active silent fallback
   surfaces that are inconsistent with:
   - `AGENTS.md` `R-08 - No Silent Fall Back Rule`
   - `test_run/AGENTS.md` `T-03 - Validation and Failure Discipline for Launcher Settings`
   - `test_run/AGENTS.md` `T-07 - Ownership Truth and Active Surface Honesty`

This note is intended to give Governance a clean review surface before any cleanup
wave is opened.

## 2. Active Truth Correction

### 2.1 Maintained battle `attack_range` is `20.0`, not `3.0`

Current maintained battle active truth:

- [test_run/test_run_v1_0.runtime.settings.json](E:/logh_sandbox/test_run/test_run_v1_0.runtime.settings.json) sets:
  - `unit.attack_range = 20.0`
- `prepare_active_scenario(...)` reads that through `_build_unit_cfg(...)` at:
  - [test_run/test_run_scenario.py](E:/logh_sandbox/test_run/test_run_scenario.py:423)
- baseline replay payload also records:
  - `runtime_cfg["contact"]["attack_range"] = 20.0`

The earlier engineering mention of `3.0` came from reading a fallback/helper
default path rather than the current maintained battle path. That was incorrect
for active battle reality and should not be used as the maintained read.

### 2.2 Why this correction matters

The current fifth-slice activation logic inside:

- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1659)

uses:

- `near_contact_start = attack_range * 0.35`
- `near_contact_full = attack_range * 0.20`

With the true maintained `attack_range = 20.0`, this means:

- `near_contact_start = 7.0`
- `near_contact_full = 4.0`

So the earlier suggestion that the main problem was a tiny near-contact window
caused by `attack_range = 3.0` was wrong.

## 3. Main Local-Desire Finding

### 3.1 The main blocker is signal-domain collapse, not attack-range size

Current same-tick target identity is produced by:

- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:3396)

That path already filters candidate targets by:

- `fire_cone_half_angle_deg`

before nearest-target selection.

Current maintained fire-cone half-angle is:

- `30.0 deg`

Therefore the selected target used downstream by `local_desire` is already
constrained to lie within the current unit facing cone.

### 3.2 Current fifth-slice turn-need read

Inside:

- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1816)

the current heading activation read is:

```text
turn_need_raw = clamp01((1 - unit_facing_alignment) * 0.5)
heading_turn_need = smoothstep01((turn_need_raw - turn_need_onset) / (1 - turn_need_onset))
local_heading_bias_weight =
    heading_bias_cap * near_contact_gate * front_bearing_need * heading_turn_need
```

This means the current activation chain depends on:

1. selected target entering the near-contact regime
2. selected target also requiring substantial extra turn relative to current unit facing
3. fleet-front lateral need also being nonzero

### 3.3 Maintained baseline evidence

Using the current Phase II primary baseline:

- `battle_36v36`

and reading only target-line-active samples:

- `contact_samples = 4088`
- `attack_range = 20.0`
- `near_contact_start = 7.0`
- `near_contact_full = 4.0`

Observed current-slice factors:

- `near_gate_nonzero_ratio = 0.093933`
- `front_need_nonzero_ratio = 1.0`
- `heading_turn_nonzero_ratio = 0.0`
- `weight_nonzero_ratio = 0.0`

Observed current-slice turn-need domain:

- `turn_raw_mean = 0.028409`
- `turn_raw_p90 = 0.060121`
- `turn_raw_p99 = 0.066222`
- `turn_raw_max = 0.066982`

Equivalent target-bearing-vs-facing domain:

- `angle_deg_mean = 17.090213`
- `angle_deg_p90 = 28.386725`
- `angle_deg_p99 = 29.824107`
- `angle_deg_max = 29.998801`

### 3.4 Interpretation

These numbers line up exactly with the already accepted target-selection owner:

- because selected targets are already filtered by a `30 deg` fire cone
- the downstream `unit facing -> selected target bearing` turn domain is capped near `30 deg`
- therefore the current fifth-slice default `turn_need_onset = 0.45` is not merely "cold"
- it is effectively outside the domain that the active selected-target carrier can reach

So the current maintained read is:

- near-contact gating is not the only problem
- the larger issue is that the chosen turn-need signal is heavily pre-compressed by
  the upstream fire-cone-constrained target-selection path

## 4. Mechanism Read: Is `local_desire` Reasonable?

### 4.1 Structurally reasonable

The current `local_desire` line is structurally consistent with the accepted
Phase II owner/path cleanup wave:

- it lives downstream of same-tick target selection
- it remains inside same-tick `unit_desire_by_unit`
- it still only supplies:
  - `desired_heading_xy`
  - `desired_speed_scale`
- locomotion still realizes desire
- combat execution still owns re-check / fire / damage / engagement writeback

So the current layer placement is reasonable.

### 4.2 Content read is currently weak / partially misaligned

The current content read is less convincing:

- it asks the `local_desire` seam to activate from a signal that upstream target
  selection has already narrowed sharply
- that makes the default activation regime effectively dormant on maintained battle
  baselines
- even moderate parameter heating does not materially change the maintained battle
  baseline

This suggests the next mechanism-content question is not just "turn the knobs up".

It is also:

- whether the chosen activation signal is the right one for this seam under the
  already accepted owner/path discipline

## 5. Silent Fallback Audit

### 5.1 Why this matters now

The active maintained path still uses many `get(..., default)` reads for behavior
bearing runtime surfaces.

This creates two problems:

1. engineering can accidentally reason from a fallback default rather than the
   maintained active configuration
2. missing required configuration can silently continue, which conflicts with the
   current repo rules

The `attack_range = 3.0` confusion above is itself an example of why these
fallback surfaces are now too risky.

### 5.2 Audit scope

This audit is limited to the current maintained active path:

- `test_run/settings_accessor.py`
- `test_run/test_run_scenario.py`
- `test_run/test_run_execution.py`
- `runtime/engine_skeleton.py`

It does not attempt to clean archive docs, historical DOE scripts, or older
non-maintained experiment surfaces.

## 6. Fallback Surfaces Found

### 6.1 Public runtime / scenario-builder fallbacks in `test_run/test_run_scenario.py`

High-risk behavior-bearing fallbacks:

- [test_run/test_run_scenario.py](E:/logh_sandbox/test_run/test_run_scenario.py:423)
  - `_build_unit_cfg(...)`
  - `unit_speed`
  - `unit_max_hit_points`
  - `attack_range`
  - `damage_per_tick`
- [test_run/test_run_scenario.py](E:/logh_sandbox/test_run/test_run_scenario.py:500)
  - `_build_movement_cfg(...)`
  - `v4a_restore_strength`
  - `v4a_reference_surface_mode`
  - `v4a_soft_morphology_relaxation`
  - `v4a_shape_vs_advance_strength`
  - `v4a_heading_relaxation`
  - battle relation / hold / approach / near-contact knobs
  - engagement motion knobs
  - `movement_model`
  - `symmetric_movement_sync_enabled`
- [test_run/test_run_scenario.py](E:/logh_sandbox/test_run/test_run_scenario.py:728)
  - `_build_boundary_cfg(...)`
  - `boundary_enabled`
  - `boundary_hard_enabled`
  - `boundary_soft_strength`
- [test_run/test_run_scenario.py](E:/logh_sandbox/test_run/test_run_scenario.py:735)
  - `_build_local_desire_cfg(...)`
  - `local_desire_turn_need_onset`
  - `local_desire_heading_bias_cap`
  - `local_desire_speed_brake_strength`
- [test_run/test_run_scenario.py](E:/logh_sandbox/test_run/test_run_scenario.py:761)
  - `_resolve_v4a_reference_cfg(...)`
  - `min_unit_spacing`
- [test_run/test_run_scenario.py](E:/logh_sandbox/test_run/test_run_scenario.py:1104)
  - `prepare_active_scenario(...)`
  - `fire_quality_alpha`
  - `fire_optimal_range_ratio`
  - `fire_cone_half_angle_deg`
  - `contact_hysteresis_h`
  - `alpha_sep`
- [test_run/test_run_scenario.py](E:/logh_sandbox/test_run/test_run_scenario.py:1288)
  - `prepare_neutral_transit_fixture(...)`
  - neutral read still carries fallback defaults for fire / contact / separation terms

Medium-risk scenario-shape fallbacks:

- fleet archetype ids
- fleet sizes / aspect ratios / facing angles
- neutral fixture size / aspect / stop radius / facing angle

These are not always "runtime mechanism" in the narrow sense, but they still
shape the maintained scenario surface and should not silently disappear.

### 6.2 Bridge-side fallbacks in `test_run/test_run_execution.py`

High-risk bridge re-injection:

- [test_run/test_run_execution.py](E:/logh_sandbox/test_run/test_run_execution.py:658)
  - `SYMMETRIC_MOVEMENT_SYNC_ENABLED`
- [test_run/test_run_execution.py](E:/logh_sandbox/test_run/test_run_execution.py:662)
  - hostile-contact impedance hybrid parameters
- [test_run/test_run_execution.py](E:/logh_sandbox/test_run/test_run_execution.py:696)
  - `local_desire_turn_need_onset`
  - `local_desire_heading_bias_cap`
  - `local_desire_speed_brake_strength`

If scenario preparation already guarantees these keys, the bridge should not
reintroduce silent defaults.

Lower-risk orchestration defaults that are probably acceptable as explicit
launcher behavior, not mechanism fallback:

- `capture_hit_points`
- `tick_timing_enabled`
- `post_elimination_extra_ticks`

These are not the main cleanup target in this note.

### 6.3 Runtime-side re-defaulting in `runtime/engine_skeleton.py`

High-risk runtime re-defaulting:

- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:584)
  - `_movement_surface` constructor seeds `local_desire` defaults
- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1681)
  - `_compute_unit_desire_by_unit(...)` re-reads:
    - `local_desire_turn_need_onset`
    - `local_desire_heading_bias_cap`
    - `local_desire_speed_brake_strength`
  - using `.get(..., default)`
- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:3096)
  - `integrate_movement(...)` falls back from `unit_desire_by_unit` to:
    - `movement_direction`
    - `1.0`

This last case is somewhat different:

- it is carrier defensiveness rather than public settings fallback
- but after the accepted desire-bridge slices, it should likely be hardened too if
  `unit_desire_by_unit` is now considered mandatory inside the maintained v4a path

## 7. Why These Fallbacks Exist

The current engineering read is that these fallback defaults are historical
carry-over from earlier phases where:

- the maintained path was still being stabilized
- runtime/public settings surfaces were not yet fully frozen into one explicit
  required set
- harness convenience defaults were used to keep active-surface bootstrap simple

This may have been understandable during earlier transition periods, but it is
now increasingly inconsistent with the current repo contract.

So the note does not defend these fallbacks as correct. It explains why they are
still present and why they should now be cleaned.

## 8. Recommended Cleanup Plan

### Phase A. Harden public maintained settings reads first

Target files:

- `test_run/test_run_scenario.py`
- `test_run/settings_accessor.py`
- maintained runtime settings JSON

Recommended action:

- replace behavior-bearing `get_runtime(..., default)` and `get_unit(..., default)`
  reads with:
  - `settings_api.MISSING`
  - explicit fail-fast `ValueError`

Minimum required explicit keys should include:

- unit:
  - `unit_speed`
  - `unit_max_hit_points`
  - `attack_range`
  - `damage_per_tick`
- movement low-level:
  - `max_accel_per_tick`
  - `max_decel_per_tick`
  - `max_turn_deg_per_tick`
  - `turn_speed_min_scale`
- v4a movement / battle / engagement:
  - the currently maintained active knobs already used by `_build_movement_cfg(...)`
- fire / contact:
  - `fire_quality_alpha`
  - `fire_optimal_range_ratio`
  - `fire_cone_half_angle_deg`
  - `contact_hysteresis_h`
  - `alpha_sep`
- local desire:
  - `local_desire_turn_need_onset`
  - `local_desire_heading_bias_cap`
  - `local_desire_speed_brake_strength`
- selectors / scenario-shaping keys where maintained scenario identity depends on them:
  - `movement_model`
  - fleet size / aspect / facing

Reason:

- the scenario builder is the most honest place to fail fast on missing required
  maintained configuration

### Phase B. Remove bridge-side default re-injection

Target file:

- `test_run/test_run_execution.py`

Recommended action:

- once Phase A guarantees presence, replace bridge-side `movement_cfg.get(..., default)`
  and `contact_cfg.get(..., default)` for required maintained keys with direct indexed reads

Reason:

- the execution bridge should pass truth to the active owner
- it should not silently author replacement truth

### Phase C. Remove runtime-side re-defaulting for required maintained surfaces

Target file:

- `runtime/engine_skeleton.py`

Recommended action:

- for required maintained surface keys already guaranteed by the bridge, replace:
  - `movement_surface.get(..., default)`
  - `combat_surface.get(..., default)`
with:
  - direct indexed reads
  - explicit invariant checks if needed

Reason:

- once a key is required by the maintained active path, the runtime should not
  silently synthesize it again

### Phase D. Review carrier-defensive fallbacks separately

Examples:

- `unit_desire_by_unit.get(..., movement_direction)`
- `unit_desire_by_unit.get(..., 1.0)`

Recommended action:

- review these as part of a narrower carrier-hardening pass
- do not mix them into the public settings cleanup unless Governance wants the two
  concerns merged

Reason:

- these fallbacks are real, but they are not the same class of problem as missing
  runtime settings

### Phase E. Validate with negative tests, not only positive battle replay

Required cleanup validation should include:

1. compile check
2. one maintained positive smoke
3. one maintained battle baseline replay
4. one maintained neutral baseline replay
5. negative tests that deliberately remove required keys and confirm fail-fast behavior

Without negative tests, fallback cleanup is easy to over-report.

## 9. Governance-Relevant Conclusions

### Conclusion A

The fifth-slice default regime is not primarily blocked by a tiny `attack_range`.

The main blocker is:

- fire-cone-constrained selected-target geometry compressing the downstream
  `unit facing -> target bearing` turn-need signal into a domain that the current
  activation onset barely or never sees.

### Conclusion B

The current maintained path still contains enough silent fallback surfaces that
they now meaningfully interfere with engineering clarity and rule compliance.

### Conclusion C

The next cleanup wave should likely be read as:

- settings / bridge / runtime fail-fast hardening

not as:

- a new doctrine slice
- a new locomotion rewrite
- a module split

## 10. Explicit Out of Scope

This note does not authorize or implement:

- mode introduction
- retreat activation
- persistent target memory
- broad locomotion redesign
- Formation / FR combat-adaptation owner flow-back
- skeleton/unit file split
- automatic change to maintained baseline
