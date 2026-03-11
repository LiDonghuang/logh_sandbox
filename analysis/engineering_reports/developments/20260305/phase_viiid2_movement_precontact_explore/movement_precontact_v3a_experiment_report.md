# Movement Pre-contact V3A Diagnostic Report

## Scope
- Focus window: pre-contact ticks up to min(first_contact-1, 100).
- FR fixed 8, MB in {2,5,8}, opponents=first six archetypes.
- Movement model fixed: `v3a`.
- Experiments: base + A(reduced centroid) + B(distance-capped attraction) + C(frame translation bias).
- Total runs: 72.

## Mean Delta vs base
- exp_a_reduced_centroid:
  - delta precontact_ar_p90_A: -0.1530
  - delta precontact_wedge_p10_A: 0.0985
  - delta precontact_persistent_outlier_p90: -2.7333
  - delta precontact_max_persistence_max: -28.1111
  - delta precontact_split_p90_A: -0.0029
  - delta first_contact_tick: 1.3333
  - delta tactical_cut_tick_T: -32.9444
  - delta tactical_pocket_tick_T: -16.9444
  - delta end_tick: 2.7222
- exp_b_distance_capped:
  - delta precontact_ar_p90_A: -0.0057
  - delta precontact_wedge_p10_A: -0.0035
  - delta precontact_persistent_outlier_p90: -0.3833
  - delta precontact_max_persistence_max: -2.2778
  - delta precontact_split_p90_A: 0.0067
  - delta first_contact_tick: 0.2222
  - delta tactical_cut_tick_T: -15.0556
  - delta tactical_pocket_tick_T: 5.7778
  - delta end_tick: -11.8333
- exp_c_frame_translation:
  - delta precontact_ar_p90_A: -0.0751
  - delta precontact_wedge_p10_A: 0.0147
  - delta precontact_persistent_outlier_p90: -1.3833
  - delta precontact_max_persistence_max: -10.6667
  - delta precontact_split_p90_A: 0.0010
  - delta first_contact_tick: 0.2778
  - delta tactical_cut_tick_T: -40.5556
  - delta tactical_pocket_tick_T: -9.0556
  - delta end_tick: 7.3889

## Artifacts
- movement_precontact_v3a_experiment_run_table.csv
- movement_precontact_v3a_experiment_delta_table.csv
- movement_precontact_v3a_experiment_summary_by_mb.csv
- movement_precontact_v3a_experiment_determinism_check.md