# Phase VIII-B Movement 3A DOE Comparison Report

> [VOID NOTICE - 2026-03-05]
> Status: VOID (do not use for governance/runtime decisions).
> Reason: FR/FCR mapping error in FR interpretation lineage.
> FR must map to `formation_rigidity`; affected conclusions in this report are invalid pending corrected rerun.

## Scope and Frozen Semantics
- Runtime code unchanged during DOE execution window (verified by file hash).
- movement_model compared: v1 vs v3a.
- combat/targeting/PD/collapse formulas and BRF template kept unchanged.
- runtime_decision_source fixed to v2 for both models to isolate movement impact.

## DOE Design
- Grid: FR in {2,5,8}, MB in {2,5,8}, PD=5.
- Models: 2 (v1, v3a).
- Replicates per cell: 30 ordered archetype pairs from 8-archetype roster.
- Total runs: 540.

## Baseline Runtime Conditions
- attack_range=5.0, fsr_strength=0.1, contact_hysteresis_h=0.1, boundary_enabled=False
- units_per_side=100, arena_size=200.0, min_unit_spacing=2.0, steps=300

## Overall Statistics
- v1: n=270, end_tick mean/median=300.00/300.00, cut_exists=92.22%, pocket_exists=100.00%, precontact_geom_cut=76.67%
- v3a: n=270, end_tick mean/median=300.00/300.00, cut_exists=85.56%, pocket_exists=100.00%, precontact_geom_cut=96.67%

## Cell-level Delta (v3a - v1)
| case_id | ?end_tick_mean | ?end_tick_median | ?win_rate_A | ?cut_exists_rate | ?pocket_exists_rate | ?precontact_geom_cut_rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| FR2_MB2_PD5 | 0.000 | 0.000 | 13.333 | 6.667 | 0.000 | 30.000 |
| FR2_MB5_PD5 | 0.000 | 0.000 | -13.333 | -13.333 | 0.000 | 30.000 |
| FR2_MB8_PD5 | 0.000 | 0.000 | -6.667 | -13.333 | 0.000 | 0.000 |
| FR5_MB2_PD5 | 0.000 | 0.000 | 13.333 | 6.667 | 0.000 | 30.000 |
| FR5_MB5_PD5 | 0.000 | 0.000 | -13.333 | -13.333 | 0.000 | 30.000 |
| FR5_MB8_PD5 | 0.000 | 0.000 | -6.667 | -13.333 | 0.000 | 0.000 |
| FR8_MB2_PD5 | 0.000 | 0.000 | 13.333 | 6.667 | 0.000 | 30.000 |
| FR8_MB5_PD5 | 0.000 | 0.000 | -13.333 | -13.333 | 0.000 | 30.000 |
| FR8_MB8_PD5 | 0.000 | 0.000 | -6.667 | -13.333 | 0.000 | 0.000 |

## Replicate Selection List (30 ordered pairs, deterministic)
- 01. bittenfeld vs grillparzer
- 02. bittenfeld vs kircheis
- 03. bittenfeld vs knappstein
- 04. bittenfeld vs mittermeyer
- 05. bittenfeld vs muller
- 06. bittenfeld vs reinhard
- 07. bittenfeld vs reuenthal
- 08. grillparzer vs bittenfeld
- 09. grillparzer vs kircheis
- 10. grillparzer vs knappstein
- 11. grillparzer vs mittermeyer
- 12. grillparzer vs muller
- 13. grillparzer vs reinhard
- 14. grillparzer vs reuenthal
- 15. kircheis vs bittenfeld
- 16. kircheis vs grillparzer
- 17. kircheis vs knappstein
- 18. kircheis vs mittermeyer
- 19. kircheis vs muller
- 20. kircheis vs reinhard
- 21. kircheis vs reuenthal
- 22. knappstein vs bittenfeld
- 23. knappstein vs grillparzer
- 24. knappstein vs kircheis
- 25. knappstein vs mittermeyer
- 26. knappstein vs muller
- 27. knappstein vs reinhard
- 28. knappstein vs reuenthal
- 29. mittermeyer vs bittenfeld
- 30. mittermeyer vs grillparzer

## BRF Artifact Policy
- Exemplars: 18 (>=1 per cell per model).
- Pathological exports: 66.
- Total BRF exports: 75.
