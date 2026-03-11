# Battle Report Framework v1.0

## 0. Run Configuration Snapshot
- Source settings path: `analysis/test_run_v1_0.settings.json`
- attack_range: 5.0
- min_unit_spacing: 2.0
- arena_size: 200.0
- max_time_steps_effective: 300 (settings was -1)
- unit_speed: 1.0
- damage_per_tick: 1.0
- ch_enabled / contact_hysteresis_h: true / 0.1
- fsr_enabled / fsr_strength: true / 0.1
- boundary_enabled: false (settings was true; harness override for this diagnostic baseline)
- overrides_applied: `max_time_steps_effective`, `boundary_enabled`

## 1. Header
- Engine Version: v5.0-alpha5 + V5.4-b
- Grid Parameters: FR, MB, PD in {2, 5, 8} (3x3x3)
- Determinism Status: PASS
- Date: 2026-03-02

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 99 |
| First Kill | 116 |
| Formation Cut | 1 |
| Pocket Formation | 188 |
| Pursuit Mode | 1 |
| Inflection | None |
| Endgame Onset | None |
| End | 300 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 CN Fixed Lead
ZGDIGO 星域会战

阿弗雷德·格利鲁帕尔兹(A) vs 布鲁诺·冯·克纳普斯坦(B)

格利鲁帕尔兹舰队: 10000艘 (A: 100 units); 克纳普斯坦舰队: 10000艘 (B: 100 units)

### 3.2 CN Narrative Body
双方在标准时01:39 (t=99)首次接触, 并在标准时01:56 (t=116)出现首批战损。战线在中段持续拉扯, 00:01 (t=1)即出现结构切割信号, 03:08 (t=188)观测到口袋化事件。本例中未出现优势拐点与终局阈值触发。至标准时05:00 (t=300), 格利鲁帕尔兹一方获胜。格利鲁帕尔兹舰队残余2568艘 (A units=29); 克纳普斯坦舰队残余1941艘 (B units=22)。

### 3.3 EN Narrative
ZGDIGO Sector engagement. First contact occurred at Standard Time 01:39 (t=99), with first confirmed losses at Standard Time 01:56 (t=116). The frontline remained contested through the middle phase; a structural-cut signal appeared as early as 00:01 (t=1), and a pocket event was observed at 03:08 (t=188). No alive-curve inflection or endgame-threshold onset was observed in this case. At Standard Time 05:00 (t=300), the Grillparzer side won. Remaining force sizes were 2,568 ships (A units=29) vs 1,941 ships (B units=22).

## 4. Structural Metrics Summary
- Mirror delta: -0.34276772203108213 (v4b macro)
- Jitter delta: -0.171161478198124 (v4b macro)
- Runtime delta: -0.008657843983832583 (v4b macro)
- Cohesion behavior summary: BEL captures `cohesion_v2` and `cohesion_v1` shadow at timeline level; no runtime decision path change in this directive.

## 5. Collapse Analysis
- Collapse occurred before contact: Yes
- Collapse preceded or aligned with pursuit mode: Yes
- Collapse aligned with formation cut (|delta_tick|<=1): Yes
