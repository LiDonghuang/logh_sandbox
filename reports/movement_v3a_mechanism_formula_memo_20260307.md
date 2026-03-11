# Movement v3a Mechanism Formula Memo (As-Implemented)
Date: 2026-03-07  
Scope: `movement` layer only, implementation memo (no behavior change)  
Code anchor: `runtime/engine_skeleton.py` (`integrate_movement`)

## 1. Purpose
This memo records the current movement computation in formula form, including:
- `forward_gain`
- `attract_gain`
- `alpha_sep`
- MB axis transform
- pursuit extension
- centroid probe scaling

It reflects current runtime code, not a proposal.

## 2. Preconditions and Frozen Boundaries
- No FR/MB/PD semantic change.
- No cohesion/collapse/combat/targeting schema change.
- This is a movement-layer technical memo only.

## 3. Key Inputs Per Fleet/Unit
- Fleet-level:
  - `kappa = normalized(formation_rigidity)`
  - `mb = clip(0.2 * (mobility_bias - 5)/5, -0.2, +0.2)`
  - `pd_norm = normalized(pursuit_drive)`
  - `enemy_cohesion` from runtime decision source (currently `v2` in observe mode)
- Unit-level:
  - `target_direction` from target layer
  - `cohesion_dir`: unit -> own centroid direction
  - `separation_dir`: local anti-overlap direction
  - `boundary`: soft boundary gradient term
  - `enemy_dir`: unit -> enemy-centroid direction

## 4. Engagement and Pursuit Gains
Compute enemy collapse signal:
```text
enemy_collapse_signal = 1 - enemy_cohesion
pursuit_confirm_threshold = 1 - pd_norm
deep_pursuit_mode = (enemy_collapse_signal > pursuit_confirm_threshold)
```

If deep pursuit enabled:
```text
pursuit_intensity = clip((enemy_collapse_signal - pursuit_confirm_threshold) / (1 - pursuit_confirm_threshold), 0, 1)
```
Else:
```text
pursuit_intensity = 0
```

Derived movement gains:
```text
forward_gain   = 1 + 0.35 * pursuit_intensity
cohesion_gain  = 1 - 0.35 * pursuit_intensity
extension_gain = 1 + 0.25 * pursuit_intensity
```

## 5. Stray Factor and Attraction Gain
Per unit:
```text
stray_ratio_raw = cohesion_norm / fleet_rms_radius
stray_factor = 0,                               if stray_ratio_raw <= 1.15
stray_factor = clip((stray_ratio_raw - 1.15)/(2.0 - 1.15), 0, 1), otherwise
```

Then:
```text
attract_gain = attract_gain_base + (attract_gain_max - attract_gain_base) * stray_factor
where attract_gain_base = 0.35, attract_gain_max = 0.85

enemy_pull_gain = enemy_pull_floor + (1 - enemy_pull_floor) * stray_factor
where enemy_pull_floor = 0.15
```

## 6. Cohesion Term (Centroid Restoration)
Base cohesion term:
```text
cohesion_scale = 1 + 0.40 * anti_stretch
```
Current implementation has:
```text
anti_stretch = 0
=> cohesion_scale = 1
```

So:
```text
C = (kappa * cohesion_gain * cohesion_scale) * cohesion_dir
```

Probe scaling (A-line):
```text
if movement_v3a_experiment == exp_precontact_centroid_probe:
    C = centroid_probe_scale * C
```

Notes:
- Canonical setting key is now `centroid_probe_scale`.
- Legacy key `precontact_centroid_probe_scale` remains accepted via compatibility mapping.
- This scaling is continuous (all ticks), not pre-contact gated.

## 7. Attraction and Maneuver Core
Attraction vector:
```text
A = attract_gain * [ enemy_pull_gain * enemy_dir + (1 - enemy_pull_gain) * target_direction ]
```

Separation/boundary coefficient:
```text
alpha_sep = 0.6
```

Pre-transform maneuver:
```text
M0 = forward_gain * target_direction + A + alpha_sep * separation_dir + alpha_sep * boundary
```

## 8. MB Axis Transform
If target axis valid:
- Decompose `M0` into parallel/tangent to target axis:
```text
M_parallel = proj(M0, target_axis)
M_tangent  = M0 - M_parallel
```
- Tangential damping:
```text
tangent_scale = max(0.05, 1 + mb - lateral_damping_base * stray_factor)
lateral_damping_base = 0.25
```
- Recompose:
```text
M = (1 - mb) * M_parallel + tangent_scale * M_tangent
```
Else:
```text
M = M0
```

## 9. Pursuit Extension
If deep pursuit:
```text
M = extension_gain * M
```

## 10. Final Movement Vector
Current code keeps axial pull disabled:
```text
axial_pull = 0
```

Final composition:
```text
T = C + M + axial_pull
```

Direction and velocity:
```text
dir = normalize(T), if ||T|| > eps
vel = unit_speed * dir
position_next = position + vel * dt
```

## 11. Post-Movement Stages (Same Tick)
After direction integration, two additional stages still modify final positions:
1. FSR isotropic scaling (if enabled)
2. Single-pass projection enforcing min spacing

So rendered displacement is affected by movement + FSR + projection.

## 12. Contact-Related Variables
Inside movement, `engaged_fraction` and `contact_gate` are computed:
```text
contact_gate = clip((engaged_alive_count / alive_count) / 0.25, 0, 1)
precontact_gate = 1 - contact_gate
```
Current implementation does not feed `precontact_gate` into the centroid probe path.

## 13. Interpretation Reminder
`centroid_probe_scale < 1` reduces cohesion restoration relative to non-cohesion terms.
In direction space:
```text
T = s*C + M  (s in (0,1])
```
Equivalent ratio view:
```text
T ∥ C + (1/s)*M
```
So lower `s` means stronger relative influence from forward/attract/separation/boundary branches.
