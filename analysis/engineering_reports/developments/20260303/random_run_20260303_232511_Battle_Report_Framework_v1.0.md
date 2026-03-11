# Battle Report Framework v1.0

## 0. Run Configuration Snapshot
- Source settings path: `analysis/test_run_v1_0.settings.json`
- display_language: `ZH`
- attack_range: `5.0`
- min_unit_spacing: `2.0`
- arena_size: `200.0`
- max_time_steps_effective: `438`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- ch_enabled / contact_hysteresis_h: `true` / `0.1`
- fsr_enabled / fsr_strength: `true` / `0.1`
- boundary_enabled: `true`
- overrides_applied: none

Randomization policy (this run):
- Implemented ten-parameters random in `[1..9]`: `formation_rigidity`, `mobility_bias`, `pursuit_drive`
- Unimplemented ten-parameters fixed at `5`: `force_concentration_ratio`, `offense_defense_weight`, `risk_appetite`, `time_preference`, `targeting_logic`, `perception_radius`, `retreat_threshold`
- Random draw seed: `767788058`
- Side A params: `MB=7, FR=5, PD=5, others=5`
- Side B params: `MB=1, FR=6, PD=7, others=5`

## 1. Header
- Engine Version: `v5.0-alpha5` (runtime path unchanged)
- Grid Parameters: `A(MB=7, FR=5, PD=5)` vs `B(MB=1, FR=6, PD=7)`; others fixed `5`
- Determinism Status: Not checked in this ad-hoc single run
- Date: `2026-03-03`

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 107 |
| First Kill | 115 |
| Formation Cut | N/A |
| Pocket Formation | N/A |
| Pursuit Mode | N/A |
| Inflection | 108 |
| Endgame Onset | 312 |
| End | 438 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 CN Fixed Lead
MIVJBK 星域会战

A(A) vs B(B)

A舰队: 10000艘 (A: 100 units); B舰队: 10000艘 (B: 100 units)

### 3.2 CN Narrative
双方在标准时01:47 (t=107) 开始交火，并在标准时01:55 (t=115) 出现成建制伤亡。战线在中前段拉锯后，于标准时01:48 (t=108) 出现优势拐点，A一方逐步掌握主动。标准时05:12 (t=312) 后，战局进入终盘压制；至标准时07:18 (t=438)，B舰队全灭，A舰队残余1840艘 (A units=20)。

### 3.3 EN Narrative
The fleets started exchanging fire at ST 01:47 (t=107), and organized losses appeared at ST 01:55 (t=115). After an early mid-line tug of war, an advantage inflection appeared at ST 01:48 (t=108), and A Fleet gradually took initiative. After ST 05:12 (t=312), the battle entered endgame suppression; by ST 07:18 (t=438), B Fleet was eliminated and A Fleet retained 1840 ships (A units=20).

## 4. Structural Metrics Summary
- Mirror delta: N/A (not part of this ad-hoc run)
- Jitter delta: N/A (not part of this ad-hoc run)
- Runtime delta: N/A (not part of this ad-hoc run)
- Cohesion behavior summary: Observer did not alter runtime decision path; battle result reflected MB/FR/PD random draw under fixed baseline mechanics.

## 5. Collapse Analysis
- Collapse occurred before contact: N/A in this ad-hoc BRF-only extraction
- Collapse preceded or aligned with pursuit mode: N/A in this ad-hoc BRF-only extraction
- Collapse aligned with formation cut (|delta_tick|<=1): N/A in this ad-hoc BRF-only extraction
