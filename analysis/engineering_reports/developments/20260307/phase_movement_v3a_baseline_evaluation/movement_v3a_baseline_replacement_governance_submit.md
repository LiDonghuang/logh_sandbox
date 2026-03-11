# Movement v3a Baseline Replacement Request

Engine Version: v5.0-alpha5  
Modified Layer: Movement  
Affected Parameters: `movement_model`, `movement_v3a_experiment`, `centroid_probe_scale`  
New Variables Introduced: None  
Cross-Dimension Coupling: None at canonical parameter-semantics level; observed effect is movement-layer geometry and mild contact-timing drift  
Mapping Impact: None  
Governance Impact: Runtime movement baseline replacement request, `v1 -> v3a`  
Backward Compatible: Yes at interface level; `test_mode` semantics remain unchanged

## Summary

1. Engineering requests baseline replacement of `movement v1` with `movement v3a`.
2. The evaluated candidate is frozen as:
   - `movement_model = v3a`
   - `movement_v3a_experiment = exp_precontact_centroid_probe`
   - `centroid_probe_scale = 0.5`
3. Event-layer thresholds were held fixed during evaluation:
   - `bridge_theta_split = 1.7`
   - `bridge_theta_env = 0.5`
4. These threshold values are treated as frozen evaluation context, not as the scope of the replacement request.
5. Full paired evaluation completed over `FR x MB x PD = 3 x 3 x 3`, opponents = first six canonical archetypes, models = `v1` vs `v3a`, total `324` runs.
6. Determinism passed for both models.
7. `Formation Cut` and `Pocket Formation` remained fully detectable under the frozen Channel-T semantics.
8. Pre-contact persistent outlier burden dropped sharply under `v3a`.
9. Mirror/jitter watch metrics improved rather than regressed.
10. Mean first-contact timing drift was mild (`+3.78` ticks).
11. No runtime cap hits occurred.
12. Engineering recommendation: `ACCEPT`.

## Evidence Anchor

Primary evaluation pack:

`analysis/engineering_reports/developments/20260307/phase_movement_v3a_baseline_evaluation`

Key files:
- `Movement_v3a_Baseline_Evaluation_Report.md`
- `movement_v3a_baseline_evaluation_run_table.csv`
- `movement_v3a_baseline_evaluation_delta_table.csv`
- `movement_v3a_baseline_evaluation_determinism_check.md`

Key aggregate results:
- `precontact_persistent_outlier_p90_mean`: `3.7309 -> 0.0062`
- `precontact_max_persistence_max_mean`: `42.4568 -> 0.4815`
- `precontact_wedge_p10_A_mean`: `0.7755 -> 1.0250`
- `precontact_ar_p90_A_mean`: `2.1842 -> 2.1702`
- `precontact_split_p90_A_mean`: `1.8538 -> 1.7192`
- `first_contact_tick_mean`: `106.7593 -> 110.5432`
- `cut_exists_rate`: `1.0000 -> 1.0000`
- `pocket_exists_rate`: `1.0000 -> 1.0000`
- `mirror_ar_gap_mean` delta: `-0.1209`
- `jitter_ar_A_mean` delta: `-0.0087`

## Scope Clarification

This request is a single-layer runtime baseline replacement for the movement layer only.

Not part of this replacement request:
- cohesion runtime source replacement
- collapse runtime replacement
- event schema replacement
- observer/report semantics replacement
- parameter semantic reinterpretation

Frozen but out-of-scope evaluation context:
- `bridge_theta_split = 1.7`
- `bridge_theta_env = 0.5`

These were held constant to preserve event interpretation during comparison.

## Engineering Recommendation

Requested decision class:

`ACCEPT`

Reason:
- motivating geometry problem materially improved
- event chain preserved
- determinism preserved
- no major stability regression detected

## Execution Delta On ACCEPT

If Governance accepts replacement, Engineering should apply the following minimum changes.

### 1. Primary Runtime Default Switch

Update movement default/fallback from `v1` to `v3a` in:
- `runtime/engine_skeleton.py`
- `analysis/test_run_v1_0.py`

### 2. Active Default Documentation / Settings Alignment

Update baseline wording and default snapshots in:
- `analysis/test_run_v1_0.settings.json`
- `analysis/phase_v_default.settings.json`
- `analysis/phase_v_reference_scenario_alpha_v2.json`

Notes:
- `analysis/test_run_v1_0.settings.json` already runs `v3a` locally, but its comment still describes `v1` as canonical baseline.
- `phase_v_default` and `reference_scenario_alpha_v2` still encode `movement_model = v1` and would need recapture/update on acceptance.

### 3. Interface Stability

Keep user-facing execution interface stable:
- `test_mode` meanings unchanged
- only internal movement baseline changes

### 4. Legacy Cleanup

Per `Baseline_Replacement_Protocol_v1.0`, old baseline `v1` should leave:
- primary runtime path
- default human test paths

Historical references may remain only in archive/reference context after the replacement is executed.

## Current Status

This submission prepares formal baseline replacement.

No replacement code has been applied in this step.
