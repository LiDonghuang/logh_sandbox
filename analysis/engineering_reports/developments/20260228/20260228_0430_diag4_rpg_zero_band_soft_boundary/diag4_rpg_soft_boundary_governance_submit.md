# Governance Submission - Phase V.1 DIAG4 Zero-Band + Soft Boundary Integration

Engine Version: v5.0-alpha2  
Modified Layer: Movement (soft boundary) + DIAG4-RPG diagnostics  
Affected Parameters: `BOUNDARY_SOFT_ENABLED`  
New Variables: none in personality layer  
Cross-Dimension Coupling: none  
Mapping Impact: none  
Backward Compatible: yes (`BOUNDARY_SOFT_ENABLED=false`)  

## Gates
- Determinism: PASS
- Combat regression: PASS
- Mirror non-worsening: PASS
- No new attractor signal: PASS
- Boundary penetration count: 0
- Permanent boundary trap count: 0
- RPG overhead <10%: PASS (8.16%)

## DIAG4-RPG Zero-Band Readout
- tau: 0.049916
- outward_ratio: 0.5000
- tangential_ratio: 0.0000
- suppressed_ratio: 0.0000
- P_return by class: see `diag4_rpg_soft_boundary_summary.json`.

## Soft Boundary Readout
- Soft ON: survivors A/B = 13/30, first_contact_tick=100
- Soft OFF baseline: survivors A/B = 13/30, first_contact_tick=99

## Note
- Mirror metric values reused from prior run (`20260228_0400`) because the latest patch changed diagnostic-only path and left behavior branch unchanged.
