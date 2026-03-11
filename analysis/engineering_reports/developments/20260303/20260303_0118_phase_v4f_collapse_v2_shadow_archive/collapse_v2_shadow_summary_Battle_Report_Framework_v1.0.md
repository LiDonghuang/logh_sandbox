# Battle Report Framework v1.0

## 0. Run Configuration Snapshot
- Source settings path: `analysis/phase_v_default.settings.json`
- attack_range: 5.0
- min_unit_spacing: 2.0
- arena_size: 200.0
- max_time_steps_effective: 300
- unit_speed: 1.0
- damage_per_tick: 1.0
- ch_enabled / contact_hysteresis_h: true / 0.1
- fsr_enabled / fsr_strength: true / 0.1
- boundary_enabled: false
- overrides_applied: `none`

## 1. Header
- Engine Version: v5.0-alpha5 (Phase V.4-f observer-only)
- Grid Parameters: FR, MB, PD in {2, 5, 8} (3x3x3), representative narrative on FR8_MB8_PD5
- Determinism Status: PASS
- Date: 2026-03-03

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
V4F 星域会战

A vs B

A舰队: 10000艘 (A: 100); B舰队: 10000艘 (B: 100)

### 3.2 CN Narrative Body
本轮代表案例 FR8_MB8_PD5 在 t=99 首次接敌, t=116 出现首批战损。旧版 collapse_event_v2 在 t=1 即触发, 与接敌时序明显错位。collapse_v2_shadow 在该案例中呈现更保守的时序: A侧在观测窗口内未触发, B侧在 t=137 达到 2-of-4 + 10 tick sustain 后触发。该结果支持将 collapse 从"单点阈值"转为"多信号持续事件标签"以降低开局误报。

至 t=300, A舰队残余2568艘 (A units=29); B舰队残余1941艘 (B units=22)

### 3.3 EN Narrative
In representative case FR8_MB8_PD5, first contact occurred at t=99 and first losses appeared at t=116. Legacy `collapse_event_v2` fired at t=1, clearly earlier than combat contact. Under the new observer definition (`2-of-4` plus `10-tick sustain`), collapse was not triggered on side A within the observed window, while side B triggered at t=137. This supports interpreting collapse as a sustained battlefield condition label rather than a single-threshold instant signal.

## 4. Structural Metrics Summary
- Mirror delta: N/A (not evaluated in this observer report)
- Jitter delta: N/A (not evaluated in this observer report)
- Runtime delta: N/A (observer-only post-processing)
- Cohesion behavior summary: Cohesion v3.1 is used only as shadow observation input; decision path remains cohesion_v2.

## 5. Collapse Analysis
- Collapse occurred before contact: Old v2=Yes; Shadow v2=No
- Collapse preceded or aligned with pursuit mode: Old v2=Yes; Shadow v2=No
- Collapse aligned with formation cut (|delta_tick|<=1): Old v2=Yes; Shadow v2=No
