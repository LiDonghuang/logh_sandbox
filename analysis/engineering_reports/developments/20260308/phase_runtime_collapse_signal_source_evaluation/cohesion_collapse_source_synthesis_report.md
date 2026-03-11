# Cohesion Collapse Source Synthesis Report

## Scope

This synthesis combines:

- the 648-run runtime collapse signal source DOE in `phase_runtime_collapse_signal_source_evaluation`
- the 66-run component diagnostic DOE in `phase_cohesion_component_diagnostic`
- human animation observations from supervised test runs

The scope is still:

`runtime collapse signal source evaluation only`

It is not a full cohesion redesign proposal.

## Evaluated Question

Should runtime collapse signal consumption remain:

`cohesion_v2`

or transition to:

`cohesion_v3_shadow`

## Baseline Context Frozen During Evaluation

- movement baseline: `v3a`
- `movement_v3a_experiment = exp_precontact_centroid_probe`
- `centroid_probe_scale = 0.5`
- bridge thresholds held fixed:
  - `bridge_theta_split = 1.7`
  - `bridge_theta_env = 0.5`
- paired fixed-seed discipline used in DOE

## Human Animation Observations

Manual observations reported during supervised test runs:

1. With `cohesion_decision_source = baseline` (`v2`), the displayed cohesion curve stays very low in the early phase, roughly around `0.1`, then rises only modestly and remains below `0.5`. One observed run ended around `t=536`.
2. With `cohesion_decision_source = v3_test` plotted in observe/test modes, the displayed cohesion starts around `0.5-0.7`, drops quickly during roughly `t=1..100`, then later recovers. One observed `mode=2` run ended around `t=447`.
3. This already suggested that:
   - `v2` may be numerically too harsh very early
   - `v3_test` is less harsh, but still not high enough to act like a conservative "intact formation" signal

The two DOE rounds were used to test those observations structurally.

## 648-Run DOE Summary

Primary artifact:

- `Cohesion_Runtime_Decision_Source_Evaluation_Report.md`

Design:

- `27` cells: `FR x MB x PD = 3 x 3 x 3`
- `6` canonical opponents
- `2` signal sources: `v2`, `v3_test`
- `2` paired seed profiles
- total: `648` runs

Key findings:

1. Event integrity remained intact under both sources.
   - `cut_exists_rate = 1.0`
   - `pocket_exists_rate = 1.0`
   - `missing_cut = 0`
   - `pocket_without_cut = 0`

2. `v3_test` materially reduced runtime collapse pressure intensity.
   - `mean_enemy_collapse_signal_A`: `0.8920 -> 0.6678`
   - `mean_enemy_collapse_signal_B`: `0.8959 -> 0.6824`
   - `mean_pursuit_intensity_A`: `0.6603 -> 0.3248`
   - `mean_pursuit_intensity_B`: `0.7977 -> 0.4334`

3. `first_deep_pursuit_tick` was still effectively saturated.
   - `first_deep_pursuit_tick = 1.0` for both sources

4. Contact and event timing shifted, but not catastrophically.
   - `first_contact_tick`: `110.54 -> 109.21`
   - `cut_tick`: `137.94 -> 132.53`
   - `pocket_tick`: `139.02 -> 146.55`

5. Event-order anomalies persisted, though less often under `v3_test`.
   - anomalies total: `78`
   - prior engineering read: all observed anomalies were `pocket_before_cut`
   - distribution:
     - `v2`: `50`
     - `v3_test`: `28`

Initial engineering conclusion after this DOE:

- `v3_test` is not a null change
- but runtime gate evidence is not clean enough for replacement, because the gate is already effectively open at `t=1`

That led to a HOLD recommendation.

## Why the 66-Run Diagnostic Was Needed

The unresolved question after the 648-run DOE was:

`why are both collapse-source signals already low enough to saturate the pursuit gate so early?`

The first engineering hypotheses were:

- `v2` might be low mainly because of `elongation`
- `v3_test` might be low mainly because of `rho / c_scale`

The 66-run diagnostic was specifically designed to test those hypotheses.

## 66-Run Component Diagnostic Summary

Primary artifact:

- `cohesion_component_diagnostic_report.md`

Design:

- `11` controlled cells
- `3` canonical opponents
- `2` sources: `v2`, `v3_test`
- `1` fixed seed profile
- total: `66` runs

The diagnostic reconstructed pre-contact component values directly from captured positions.

### Corrected Finding 1

`v2` is not primarily low because of elongation.

Measured Side-A pre-contact means in `v2` runs:

- `A_v2_mean = 0.0391`
- `A_fragmentation_mean = 0.7870`
- `A_dispersion_mean = 0.3758`
- `A_elongation_mean = 0.6432`
- `A_outlier_mass_mean = 0.0000`

Dominant penalty counts:

- `fragmentation = 33 / 33`
- `dispersion = 0`
- `outlier_mass = 0`
- `elongation = 0`

Therefore:

`v2` is being driven down first and foremost by fragmentation semantics.

### Corrected Finding 2

`v3_test` is not primarily low because of `rho / c_scale`.

Measured Side-A pre-contact means:

- in `v2` runs:
  - `A_v3_mean = 0.2130`
  - `A_c_conn_mean = 0.2130`
  - `A_c_scale_mean = 1.0000`
- in `v3_test` runs:
  - `A_v3_mean = 0.2460`
  - `A_c_conn_mean = 0.2460`
  - `A_c_scale_mean = 1.0000`

Rho-band status:

- `A_rho_in_band_pct = 100%` for all diagnostic runs
- `A_rho_lt_low_pct = 0%`
- `A_rho_gt_high_pct = 0%`

Therefore:

`v3_test` is also being driven low primarily by connectivity semantics, not scale penalty semantics.

### Corrected Finding 3

The low-value problem is shared across both sources because both depend on the same LCC-style connectivity notion.

This is the key synthesis result.

## Integrated Interpretation

Combining the two DOE rounds and the human observations:

1. The early low-value problem is real.
   - human plots showed it
   - both DOE rounds confirmed it numerically

2. `v3_test` is directionally better than `v2`.
   - lower collapse signal
   - lower pursuit intensity
   - fewer event-order anomalies
   - slightly improved realized geometry

3. But the main defect is upstream of the `v2 vs v3_test` replacement choice.

The shared defect is:

`connectivity / largest-component semantics appear too harsh for pre-contact fleet formations`

In practical terms, visually coherent fleets are being numerically treated as badly fragmented very early.

## Engineering Judgment

Current recommendation remains:

`HOLD`

Reason:

- `v3_test` should not yet be promoted as runtime collapse signal baseline
- not because it failed outright
- but because the current source-comparison problem is contaminated by a deeper shared defect in connectivity semantics

## What This Means For Governance Discussion

The next design discussion should not be framed as:

`Which is better, v2 or v3_test?`

It should be framed as:

`What should a runtime collapse-signal source mean during pre-contact and early-contact phases, and how should connectivity be measured?`

That is a cohesion-collapse semantics question, not a simple source-switch question.

## Working Takeaways

1. Do not baseline-replace `v2 -> v3_test` yet.
2. Treat the 648-run DOE as valid evidence that `v3_test` changes runtime behavior meaningfully.
3. Treat the 66-run DOE as the corrective finding that both signals are mainly failing at the connectivity layer.
4. Use future governance work to redefine or constrain cohesion-collapse semantics before reopening the replacement gate.
