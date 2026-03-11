# ODW Posture DOE Report

Status: engineering exploratory DOE
Scope: bounded ODW posture-bias prototype only

## Batch

- Runs: `90`
- Side-A ODW levels: `[2, 5, 8]`
- Prototype gains k: `[0.0, 0.25, 0.5, 0.75, 1.0]`
- Opponents: `reinhard, kircheis, reuenthal, mittermeyer, bittenfeld, muller`
- Seed policy: single fixed seed `SP01` (deterministic path; no metatype sampling)

## Frozen Context

- movement baseline = `v3a`
- movement_v3a_experiment = `exp_precontact_centroid_probe`
- centroid_probe_scale = `0.5`
- runtime collapse signal source baseline = `v3_test @ 1.1`
- physical spacing / boundary / combat / targeting unchanged from active test-run baseline

## Key Readout

- Event-order anomaly count: `1`
- `pocket_before_cut` count: `1`
- Baseline (`k=0`) precontact `NetAxisPush abs p90` mean: `0.0068`
- Strongest (`k=1.0`) precontact `NetAxisPush abs p90` mean: `0.0076`
- Baseline (`k=0`) precontact `AR_forward p90` mean: `2.0310`
- Strongest (`k=1.0`) precontact `AR_forward p90` mean: `2.0240`
- Baseline (`k=0`) precontact `WedgeRatio p10` mean: `0.8055`
- Strongest (`k=1.0`) precontact `WedgeRatio p10` mean: `0.8173`

## Relation Hints

- `precontact_net_axis_push_abs_p90` vs `precontact_ar_forward_p90_A` Pearson r: `0.0446`
- `precontact_net_axis_push_abs_p90` vs `precontact_wedge_ratio_p10_A` Pearson r: `0.0147`
- `precontact_net_axis_push_abs_p90` vs `first_deep_pursuit_tick_A` Pearson r: `-0.3203`
- `precontact_net_axis_push_abs_p90` vs `mean_enemy_collapse_signal_A` Pearson r: `0.4618`

## Engineering Reading

- This batch is large enough to expose whether ODW posture bias produces stable geometry/topology shifts across multiple canonical opponents without opening new mechanism layers.
- `NetAxisPush` is included as a supporting indicator only. It can suggest relative axial pressure asymmetry, but it is not ODW-specific and must not be read as direct shape meaning.
- The main question is whether higher `k` and different `ODW` levels produce interpretable movement/topology differences while keeping event integrity acceptable.

## Files

- `odw_posture_doe_run_table.csv`
- `odw_posture_doe_delta_from_k0.csv`
- `odw_posture_doe_summary_by_k.csv`
- `odw_posture_doe_summary_by_odw.csv`
- `odw_posture_doe_summary_by_opponent.csv`
- `odw_posture_doe_relation_summary.csv`
