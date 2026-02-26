# Freeze Declaration — v4.1-beta

Engine Version: v4.1-beta

Combat Class: Weakly Anisotropic Linear Exchange  
Spatial Model: Global Non-Penetration

Default Parameters:
- alpha_default = 0.1
- alpha_safe_max = 0.15 (documented)
- min_unit_spacing_default = 2.0
- min_unit_spacing_stress = 1.0 (documented)

Invariants:
- Deterministic: Yes
- Mirror Symmetry Level: 1
- Combat Order: 1
- Movement layer untouched
- Decision layer untouched

Minimal Signature:
- \( q(\theta) = 1 + \alpha\cos(\theta) \)
