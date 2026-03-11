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
- overrides_applied: `FR/MB/PD scenario override only`

## 1. Header
- Engine Version: v5.0-alpha5 (observer-only formation snapshot layer)
- Grid Parameters: representative case FR8_MB8_PD5
- Determinism Status: PASS
- Date: 2026-03-03

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 99 |
| First Kill | 116 |
| Formation Cut | 0 |
| Pocket Formation | 160 |
| Pursuit Mode | 1 |
| Inflection | None |
| Endgame Onset | None |
| End | 300 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 CN Fixed Lead
FSNAP 星域会战

Hawke(A) vs Brenner(B)

Hawke舰队: 10000艘 (A: 100 units); Brenner舰队: 10000艘 (B: 100 units)

### 3.2 CN Narrative
??????01:39 (t=99)??????????01:56 (t=116)???????????????????? (t=0)???????????????02:40 (t=160)?????????????05:00 (t=300)?Hawke Fleet??????????Hawke Fleet??2568? (Hawke units=29)?Brenner Fleet??1941? (Brenner units=22)?

### 3.3 EN Narrative
Hawke Fleet and Brenner Fleet began exchanging fire at Standard Time 01:39 (t=99), and formed-unit casualties appeared at Standard Time 01:56 (t=116). A formation-fracture signal was already present on both sides at t=0. The frontline remained contested through the middle phase, and by Standard Time 02:40 (t=160) both fleets attempted flanking maneuvers. At Standard Time 05:00 (t=300), Hawke Fleet held the advantage and won, with 2,568 ships remaining (Hawke units=29) versus 1,941 ships (Brenner units=22).

## 4. Structural Metrics Summary
- Mirror delta: N/A (not evaluated in this observer report)
- Jitter delta: N/A (not evaluated in this observer report)
- Runtime delta: N/A (observer-only post-processing)
- Cohesion behavior summary: Formation snapshot diagnostics are observer-only and detached from runtime decision path.

## 5. Collapse Analysis
- Collapse occurred before contact: Yes
- Collapse preceded or aligned with pursuit mode: Yes
- Collapse aligned with formation cut (|delta_tick|<=1): Yes
