# Parameter Mapping Snapshot v1.0

## Mobility Bias

Status: Frozen / Authoritative\
Layer: Parameter Mapping Layer\
Anchor: Latest Archetype Version

------------------------------------------------------------------------

# I. Parameter Identity

Mobility Bias\
Domain: \[1--10\] (normalized internally to \[0,1\])

Definition (Canonical): Controls priority and intensity of maneuver
behavior relative to positional stability.

Mobility Bias does NOT directly modify: - Damage - HitProbability -
Breakthrough trigger - Risk Appetite - Time Preference

------------------------------------------------------------------------

# II. Functional Role in Sandbox Engine

Mobility Bias influences movement decision logic only.

It governs:

1.  Velocity utilization ratio (how close to MaxSpeed units operate)
2.  Frequency of directional change
3.  Flank vector weighting
4.  Willingness to stretch formation for positional gain

------------------------------------------------------------------------

# III. Derived Variables

The following derived variables are permitted:

## 1. VelocityUtilizationRatio

VelocityUtilization = MaxSpeed × MobilityBias_normalized

Higher Mobility Bias → greater proportion of available speed used.

------------------------------------------------------------------------

## 2. FlankVectorWeight

FlankVectorWeight = f(MobilityBias)

Higher Mobility Bias → increased preference for lateral or oblique
approach vectors.

------------------------------------------------------------------------

## 3. ManeuverPersistence

ManeuverPersistence = f(MobilityBias)

Higher Mobility Bias → reduced tendency to halt once contact
established.

------------------------------------------------------------------------

# IV. Causal Chain (Non-Shortcut Rule)

Mobility Bias → Positional Change\
Positional Change → Local Density Redistribution\
Density Redistribution → LocalCount Variation\
LocalCount Variation → EffectiveDamage via α\
EffectiveDamage → Potential Breakthrough

Direct mapping from Mobility Bias → Breakthrough is prohibited.

------------------------------------------------------------------------

# V. Separation Constraints

Mobility Bias must remain orthogonal to:

-   Force Concentration Ratio
-   Risk Appetite
-   Formation Rigidity
-   Perception Radius

Mobility controls movement priority, not structural cohesion or risk
tolerance.

------------------------------------------------------------------------

# VI. Legacy Mechanism Recovery Notes

The following legacy mechanisms are allowed only if driven by Mobility
Bias:

-   Flanking maneuvers
-   Single-wing pressure tactics
-   High-speed exploitation behavior

The following are NOT allowed:

-   Direct damage multiplier
-   Artificial breakthrough probability bonus
-   Automatic aggression escalation

------------------------------------------------------------------------

# VII. Freeze Declaration

This mapping is frozen under Sandbox Governance Canonical v1.0.

Any modification requires: - Version increment - Explicit change log -
Structural closure declaration

Parameter Mapping Snapshot v1.0 --- Mobility Bias\
Frozen / Authoritative
