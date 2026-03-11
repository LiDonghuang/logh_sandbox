# Engineering Report v1.0 - attack_range Calibration + Mapping Status Audit
Engine Version: v5.0-alpha3
Modified Layer: none (measurement-only; no behavior change in this round)
Affected Parameters: attack_range (experiment input only)
New Variables: none
Cross-Dimension Coupling: none introduced
Mapping Impact: audit-only
Governance Impact: none
Backward Compatible: yes

## Calibration Summary (fixed-seed mode)
- range=3: survivors A/B=73/64, first_contact=110, crossing=False, FFC mean/p90=0.1744/0.2632, deltaAlive std=0.6234, nonzero=49, mass-focus-fire-dominant=False
- range=5: survivors A/B=53/37, first_contact=109, crossing=False, FFC mean/p90=0.2477/0.4274, deltaAlive std=0.7534, nonzero=84, mass-focus-fire-dominant=False
- range=10: survivors A/B=40/14, first_contact=106, crossing=False, FFC mean/p90=0.3917/0.5777, deltaAlive std=0.7669, nonzero=111, mass-focus-fire-dominant=True
- range=20: survivors A/B=35/11, first_contact=102, crossing=False, FFC mean/p90=0.5945/0.7347, deltaAlive std=0.6529, nonzero=129, mass-focus-fire-dominant=True
- range=30: survivors A/B=38/6, first_contact=97, crossing=False, FFC mean/p90=0.6288/0.8080, deltaAlive std=0.8004, nonzero=109, mass-focus-fire-dominant=True

## Random-seed Spot-check Note
- Runtime is deterministic in current baseline path; random_seed affects visualization/background only.
- Three repeats per range were still executed as requested and are included in CSV appendix.

## Mapping Status Audit Appendix
| Archetype Parameter | Runtime Variable(s) Affected | Status | Gate Phase | MB/FR/Other Interaction | Notes |
|---|---|---|---|---|---|
| force_concentration_ratio | - | Not Implemented | - | Other | No active runtime read path in movement/targeting/combat. |
| mobility_bias | integrate_movement: mb_personality (local workspace patch only) | Experimental-Active | V2-DIAG0 (workspace patch, uncommitted) | MB | In current workspace file it drives MB reweighting; in HEAD baseline used for calibration here it is not active. |
| offense_defense_weight | resolve_combat: damage_scale via unit.offense_defense_weight | Partially Implemented | Pre-V baseline | Other | Combat path exists, but test_run initialization does not map archetype ODW into UnitState (default 0.5 used). |
| risk_appetite | - | Not Implemented | - | Other | No active runtime read path. |
| time_preference | - | Not Implemented | - | Other | No active runtime read path. |
| targeting_logic | - | Not Implemented | - | Other | No active runtime read path in target assignment. |
| formation_rigidity | evaluate_cohesion(kappa), integrate_movement(cohesion weight), FSR k_f coupling | Canonical-Active | V1 | FR | Primary geometric stiffness/coupling control in current runtime. |
| perception_radius | - | Not Implemented | - | Other | No active runtime read path. |
| pursuit_drive | - | Not Implemented | - | Other | No active runtime read path. |
| retreat_threshold | - | Not Implemented | - | Other | No active runtime read path. |

## Layer Confirmation
- Movement layer affected by: formation_rigidity, mobility_bias (workspace patch only)
- Cohesion / FSR affected by: formation_rigidity
- Contact affected by: none (archetype-independent in current HEAD baseline)
- Targeting affected by: none (archetype-independent in current HEAD baseline)
- Combat resolution affected by: offense_defense_weight path exists but archetype mapping not applied in test_run initialization
- Indirect archetype runtime effects (HEAD baseline): formation_rigidity only
- mobility_bias affects runtime under DIAG0 (HEAD baseline): False
- mobility_bias affects runtime in current workspace file: True
