# collapse_v2_shadow Interface Freeze v1.0
Engine Baseline: v5.0-alpha5
Status: Frozen observer interface (runtime-ready, runtime-deferred)
Scope: Personal LOGH Sandbox (`E:\logh_sandbox`)

## 1. Boundary Statement (Hard)
`collapse_v2_shadow` is observer-only in this phase.
It is computed and reported for audit, but must not be consumed by runtime decisions.

Not consumed by:
1. PD triggering / pursuit mode
2. movement equations
3. targeting semantics
4. combat formulas
5. retreat logic

`collapse_decision_source_effective` remains `legacy_v2` for modes `0/1/2`.

## 2. Frozen Per-Tick Fields (side-level)
The following field names are frozen as the interface contract:
1. `tick`
2. `pressure_v2_shadow` (bool)
3. `collapse_v2_shadow` (bool)
4. `pressure_sustain_counter` (int)
5. `C_conn_signal` (float)
6. `C_coh_signal` (float)
7. `ForceRatio` (float)
8. `AttritionMomentum` (float)

Computation semantics (current implementation):
1. `C_conn_signal` = Cohesion v3.1 shadow connectivity component (`c_conn`)
2. `C_coh_signal` = Cohesion v3.1 shadow value (`cohesion_v3`)
3. `ForceRatio` = `Alive_self / Alive_enemy`
4. `AttritionMomentum` uses fixed window baseline `W=20` with effective startup window `W_eff=min(W,t)`:
   - `loss_rate_self = (Alive_self(t-W_eff) - Alive_self(t)) / W_eff`
   - `loss_rate_enemy = (Alive_enemy(t-W_eff) - Alive_enemy(t)) / W_eff`
   - `AttritionMomentum = loss_rate_self - loss_rate_enemy`

## 3. Threshold/Sustain Policy (Frozen)
Current implementation keeps Phase V.4-f structure:
1. `theta_conn = q20(C_conn_signal)`
2. `theta_coh = q20(C_coh_signal)`
3. `theta_force = q30(ForceRatio)`
4. `theta_attr = q70(AttritionMomentum)`

Fallback defaults (used only when quantile cannot be formed):
1. `collapse_shadow_theta_conn_default = 0.10`
2. `collapse_shadow_theta_coh_default = 0.98`
3. `collapse_shadow_theta_force_default = 0.95`
4. `collapse_shadow_theta_attr_default = 0.10`

Pressure/collapse:
1. `pressure_v2_shadow = (cond_conn + cond_coh + cond_force + cond_attr) >= 2`
2. `pressure_sustain_counter` increments while pressure is true, else resets to 0
3. `collapse_v2_shadow = pressure_sustain_counter >= 10`

## 4. Frozen Per-Run Summary Fields (side-level)
1. `first_tick_pressure_v2_shadow` (int or `N/A`)
2. `first_tick_collapse_v2_shadow` (int or `N/A`)
3. `%ticks_pressure_true` (float)
4. `%ticks_collapse_true` (float)
5. `notes` (`triggered` / `never-trigger` / `observer_disabled`)

## 5. Integration and Audit
Integration locations:
1. Computation: `analysis/test_run_v1_0.py` (post-simulation observer pipeline)
2. BRF Snapshot audit fields:
   - `test_mode`
   - `runtime_decision_source_effective`
   - `collapse_decision_source_effective`

BRF section behavior:
1. Section 5 (Collapse Analysis) may display collapse shadow summary values
2. BRF template section schema remains unchanged

## 6. Effective Freeze Statement
The interface above is frozen for this phase and treated as runtime-ready.
Any future switch from observer-only to runtime-consumed collapse requires explicit Governance approval.
