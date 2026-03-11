# Governance Submission - Phase V.1 Soft Boundary Auto-Scaling Refinement

Engine Version: v5.0-alpha3  
Modified Layer: Movement (soft boundary width derivation) + DIAG readouts  
Affected Parameters: `BOUNDARY_SOFT_ENABLED`  
New Variables: none in personality layer  
Cross-Dimension Coupling: none  
Mapping Impact: none  
Backward Compatible: yes (`BOUNDARY_SOFT_ENABLED=false`)  

## Formula Confirmation
- Implemented: `w = min(separation_radius, 0.05 * L)`
- L used: `arena_size` (square map)
- Strength scaling: unchanged

## Gates
- Determinism: PASS
- Combat regression: PASS
- Mirror non-worsening: PASS
- No new attractor signal: PASS
- Boundary penetration count: 0
- Permanent boundary trap count: 0
- RPG overhead <10%: PASS (7.21%)

## Required Diagnostic Readouts
- boundary_band_width_w: 2.0
- boundary_band_fraction: 0.01
- boundary_force_events_count_total: 22

## Small Arena Sensitivity (arena=100)
- Before (old formula): survivors 8/16, first_contact=38, mean_band_fraction=0.0200, force_events_total=1641
- After (autoscaled): survivors 8/16, first_contact=38, mean_band_fraction=0.0200, force_events_total=1641
- Note: current scenario has `separation_radius=2`, so old/new width coincide at arena=100.

## Large Arena Non-Regression
- Current soft ON: survivors 13/30, first_contact=100
- Prior soft ON (0430): survivors 13/30, first_contact=100
- Delta: A=0, B=0, contact_tick=0


## Overhead Measurement Note
- This gate uses pure engine-step timing (no external per-tick metric extraction in benchmark loop).
