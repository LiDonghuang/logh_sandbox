# Phase VIII-A DOE Summary

## Execution Mode
- Replicate semantics mode: archetype matchup sampling (deterministic harness, no random replicate variance).
- Archetype roster size: 8
- Ordered pair pool: 56
- Selected ordered pairs per cell: 30
- Grid cells: 9 (FR in {2,5,8}, MB in {2,5,8}, PD=5)
- Total runs: 270

## Frozen Detector Semantics
- theta_split=1.715, theta_env=0.583, S=20
- Channel G: geometry-only; Channel T: contact-gated (in_contact_count > 0)
- BRF Tier-2 mapping uses Channel T only

## Baseline Config
- attack_range: 5.0
- damage_per_tick: 1.0
- fire_quality_alpha: 0.1
- contact_hysteresis_h: 0.1
- fsr_strength: 0.1
- boundary_enabled: False
- units_per_side: 100
- arena_size: 200.0
- min_unit_spacing: 2.0
- unit_speed: 1.0
- unit_max_hit_points: 100.0
- initial_fleet_aspect_ratio: 2.0
- steps: 300

## Cell Statistics
| Case | n | %cut_T | %pocket_T | cut_T p50/p90/p95 | pocket_T p50/p90/p95 | delta(pocketT-cutT) p50/p90/p95 | cut_precontact_G rate | Pathological flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FR2_MB2_PD5 | 30 | 93.3% | 100.0% | 137.0/282.0/282.0 | 175.0/199.0/203.4 | 27.0/65.9/79.0 | 66.7% | PocketNoCut:2 |
| FR2_MB5_PD5 | 30 | 90.0% | 100.0% | 142.0/299.0/299.0 | 188.0/207.0/215.2 | 46.0/72.0/77.1 | 63.3% | PocketNoCut:3 |
| FR2_MB8_PD5 | 30 | 93.3% | 100.0% | 124.0/140.0/151.0 | 170.0/208.1/209.0 | 47.0/69.5/80.8 | 100.0% | CutAlwaysPreG, PocketNoCut:2 |
| FR5_MB2_PD5 | 30 | 93.3% | 100.0% | 137.0/282.0/282.0 | 175.0/199.0/203.4 | 27.0/65.9/79.0 | 66.7% | PocketNoCut:2 |
| FR5_MB5_PD5 | 30 | 90.0% | 100.0% | 142.0/299.0/299.0 | 188.0/207.0/215.2 | 46.0/72.0/77.1 | 63.3% | PocketNoCut:3 |
| FR5_MB8_PD5 | 30 | 93.3% | 100.0% | 124.0/140.0/151.0 | 170.0/208.1/209.0 | 47.0/69.5/80.8 | 100.0% | CutAlwaysPreG, PocketNoCut:2 |
| FR8_MB2_PD5 | 30 | 93.3% | 100.0% | 137.0/282.0/282.0 | 175.0/199.0/203.4 | 27.0/65.9/79.0 | 66.7% | PocketNoCut:2 |
| FR8_MB5_PD5 | 30 | 90.0% | 100.0% | 142.0/299.0/299.0 | 188.0/207.0/215.2 | 46.0/72.0/77.1 | 63.3% | PocketNoCut:3 |
| FR8_MB8_PD5 | 30 | 93.3% | 100.0% | 124.0/140.0/151.0 | 170.0/208.1/209.0 | 47.0/69.5/80.8 | 100.0% | CutAlwaysPreG, PocketNoCut:2 |

## BRF Artifact Policy
- Exemplar BRFs (one per cell): 9
- Additional pathological BRFs: 18
- Total BRF artifacts exported: 27

## Notable Findings
- FR2_MB2_PD5: pocket_never=false, cut_always_precontact_G=false, pocket_without_cut_runs=2
- FR2_MB5_PD5: pocket_never=false, cut_always_precontact_G=false, pocket_without_cut_runs=3
- FR2_MB8_PD5: pocket_never=false, cut_always_precontact_G=true, pocket_without_cut_runs=2
- FR5_MB2_PD5: pocket_never=false, cut_always_precontact_G=false, pocket_without_cut_runs=2
- FR5_MB5_PD5: pocket_never=false, cut_always_precontact_G=false, pocket_without_cut_runs=3
- FR5_MB8_PD5: pocket_never=false, cut_always_precontact_G=true, pocket_without_cut_runs=2
- FR8_MB2_PD5: pocket_never=false, cut_always_precontact_G=false, pocket_without_cut_runs=2
- FR8_MB5_PD5: pocket_never=false, cut_always_precontact_G=false, pocket_without_cut_runs=3
- FR8_MB8_PD5: pocket_never=false, cut_always_precontact_G=true, pocket_without_cut_runs=2