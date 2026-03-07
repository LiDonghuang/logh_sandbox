# Parameter Mapping Snapshot v1.0

## Force Concentration Ratio (FCR)

Status: Frozen / Authoritative\
Layer: Parameter Mapping Layer\
Anchor: Latest Archetype Version

------------------------------------------------------------------------

# I. Parameter Identity

Force Concentration Ratio (FCR)\
Domain: \[1--10\] (normalized internally to \[0,1\])

Definition (Canonical): Controls spatial compression tendency of fleet
structure.

FCR does NOT directly modify: - Damage - HitProbability - Breakthrough
trigger - Risk behavior

------------------------------------------------------------------------

# II. Functional Role in Sandbox Engine

FCR influences spatial behavior only.

It governs:

1.  Desired formation density
2.  Cluster radius preference
3.  Local reinforcement attraction strength
4.  Flagship proximity tendency (indirectly)

------------------------------------------------------------------------

# III. Derived Variables

The following derived variables are permitted:

## 1. DesiredClusterRadius

DesiredClusterRadius = BaseClusterRadius × (1 - FCR_normalized × k)

Where: - k is scaling constant - Higher FCR → smaller radius → higher
density

------------------------------------------------------------------------

## 2. DensityAttractionWeight

DensityAttractionWeight = f(FCR)

Higher FCR → stronger pull toward friendly centroid

------------------------------------------------------------------------

# IV. Causal Chain (Non-Shortcut Rule)

FCR → Higher Local Density\
Higher Local Density → Higher LocalCount\
Higher LocalCount → Increased EffectiveDamage via α\
Increased EffectiveDamage → Potential Breakthrough

Direct mapping from FCR → Breakthrough is prohibited.

------------------------------------------------------------------------

# V. Separation Constraints

FCR must remain orthogonal to:

-   Risk Appetite
-   Offense / Defense Weight
-   Formation Rigidity
-   Time Preference

FCR controls compression, not aggression or persistence.

------------------------------------------------------------------------

# VI. Legacy Mechanism Recovery Notes

The following legacy mechanisms are allowed only if driven by FCR:

-   Main battle cluster tightening
-   Guard density around flagship
-   Narrow battlefront formation

The following are NOT allowed:

-   Direct damage multipliers
-   Artificial breakthrough bonus
-   Aggression bias override

------------------------------------------------------------------------

# VII. Freeze Declaration

This mapping is frozen under Sandbox Governance Canonical v1.0.

Any modification requires: - Version increment - Explicit change log -
Structural closure declaration

Parameter Mapping Snapshot v1.0 --- FCR\
Frozen / Authoritative
