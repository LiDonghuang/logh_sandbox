## PR9 Phase II - Combat Coupling Replacement, HP-Scaled Fire, and Angle-Quality Rename

Date: 2026-04-20  
Scope: runtime + maintained `test_run` public config surface  
Status: implemented locally, validated against current Phase II primary baselines

### 1. What changed

This round replaces the legacy fleet-level `coupling` damage modifier in the
active combat path with a per-unit HP-scaled fire term, and renames the public
angle-quality coefficient from `fire_quality_alpha` to
`fire_angle_quality_alpha`.

Active owner/path:

- `runtime/engine_skeleton.py`
  - `EngineTickSkeleton.resolve_combat(...)`
- Maintained public config / bridge surface:
  - `test_run/settings_accessor.py`
  - `test_run/test_run_scenario.py`
  - `test_run/test_run_execution.py`
  - `test_run/test_run_v1_0.runtime.settings.json`
  - `test_run/test_run_v1_0.settings.comments.json`
  - `test_run/test_run_v1_0.settings.reference.md`
  - `README.md`

### 2. Formula replacement

Previous active damage read:

- `event_damage = damage_per_tick * coupling * angle_quality * range_quality`
- where:
  - `coupling = 1.0 + geom_gamma * (p_attacker - p_target)`
  - `p_attacker = attackers_by_fleet / alive_by_fleet`
  - `p_target = attackers_by_fleet / alive_by_fleet`

New active damage read:

- `hp_fire_scale = clamp(unit.hit_points / unit.max_hit_points, 0.0, 1.0)`
- `event_damage = damage_per_tick * hp_fire_scale * angle_quality * range_quality`

Implications:

- fleet-level participation ratio no longer changes single-hit damage
- damaged units now lose fire output progressively as HP drops
- fresh full-HP units still fire at full `damage_per_tick`

### 3. Public naming change

Public / maintained settings rename:

- old: `runtime.physical.fire_control.fire_quality_alpha`
- new: `runtime.physical.fire_control.fire_angle_quality_alpha`

Reason:

- the coefficient only governs `angle_quality`
- `range_quality` is a separate modifier driven by `fire_optimal_range_ratio`
- the old name was too easy to read as a merged or generic fire-quality knob

Current runtime read remains:

- `angle_quality = max(0, 1 + fire_angle_quality_alpha * cos(theta))`

### 4. What did not change

This round did not change:

- target-selection ownership
- `resolve_combat(...)` stage ownership
- `fire_cone_half_angle_deg` semantics
- `fire_optimal_range_ratio` semantics
- locomotion / local desire / movement ownership
- `BattleState` schema
- harness ownership of doctrine

### 5. Files changed

- `runtime/engine_skeleton.py`
- `test_run/settings_accessor.py`
- `test_run/test_run_scenario.py`
- `test_run/test_run_execution.py`
- `test_run/test_run_v1_0.runtime.settings.json`
- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`
- `README.md`

### 6. Validation

Static check:

- `python -m py_compile runtime/engine_skeleton.py test_run/settings_accessor.py test_run/test_run_scenario.py test_run/test_run_execution.py`

Narrow smoke:

- maintained active path, `steps=120`
- result:
  - `final_tick = 120`
  - `first_contact_tick = 61`
  - `first_damage_tick = 61`
  - `engaged_count_final = 16`

Paired baseline review anchor:

- current Phase II primary baselines under `analysis/reference_notes/eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_*.json`

Replay note:

- those baseline captures predate later explicit `local_desire_*` public-surface
  storage
- current fail-fast runtime now requires those keys
- for comparison replay only, the script explicitly injected the current
  maintained accepted values:
  - `local_desire_turn_need_onset = 0.45`
  - `local_desire_heading_bias_cap = 0.06`
  - `local_desire_speed_brake_strength = 0.03`
- this was an explicit comparison-time compatibility patch, not a restored
  runtime silent fallback

Paired comparison result:

- `battle_36v36`
  - changed
  - baseline final:
    - `A alive=25 hp=1779.327760`
    - `B alive=27 hp=1844.239022`
  - current final:
    - `A alive=28 hp=1938.337492`
    - `B alive=30 hp=2336.952714`
  - first contact / first damage stayed `61 / 61`
- `battle_100v100`
  - changed
  - baseline final:
    - `A alive=72 hp=5534.064357`
    - `B alive=67 hp=5277.515490`
  - current final:
    - `A alive=75 hp=6249.738653`
    - `B alive=76 hp=6178.012498`
  - first contact / first damage stayed `58 / 58`
- `neutral_36`
  - exact match
- `neutral_100`
  - exact match

### 7. Human-readable read

The replacement behaves as expected:

- early battle timing is unchanged because opening volleys come from mostly
  full-HP units, so `hp_fire_scale` is near `1.0`
- longer battle outcomes soften because damaged ships now lose outgoing fire
  power instead of retaining full base damage behind a fleet-level participation
  scalar
- neutral fixture behavior is unchanged because the combat path is never entered

### 8. Current conclusion

This is a real behavior-bearing combat-model change, not a cleanup-only rename.

Accepted reading after local validation:

- legacy fleet participation `coupling` is removed from active runtime damage
- active damage now depends on explicit per-unit HP state rather than fleet-level
  participation ratio
- the public angle-quality coefficient name now matches its actual scope

Human follow-up read:

- the battle drift is accepted as intended mechanism-content change
- early-phase parity is the relevant continuity check for this round
- this record should be treated as the anchor document for the next baseline
  refresh rather than as a failed cleanup delta
