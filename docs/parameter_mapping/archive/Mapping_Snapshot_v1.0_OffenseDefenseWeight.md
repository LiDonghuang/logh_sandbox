# Parameter Mapping Snapshot v1.0

## Offense / Defense Weight

Status: Frozen / Authoritative\
Layer: Parameter Mapping Layer\
Anchor: Latest Archetype Version

------------------------------------------------------------------------

# I. Parameter Identity

Offense / Defense Weight\
Domain: \[1--10\] (normalized internally to \[0,1\])

Definition (Canonical): Controls engagement posture bias between
advancing pressure and positional stability.

Offense / Defense Weight does NOT directly modify: - Damage -
HitProbability - Breakthrough trigger - Risk Appetite - Force
Concentration Ratio

------------------------------------------------------------------------

# II. Functional Role in Sandbox Engine

Offense / Defense Weight influences engagement-level decision logic.

It governs:

1.  Willingness to advance after contact
2.  Threshold for maintaining vs pushing line
3.  Contact expansion behavior
4.  Distance maintenance during fire exchange

------------------------------------------------------------------------

# III. Derived Variables

The following derived variables are permitted:

## 1. EngagementAdvanceThreshold

EngagementAdvanceThreshold = BaseThreshold × (1 -
OffenseWeight_normalized)

Higher Offense Weight → lower threshold → easier push forward.

------------------------------------------------------------------------

## 2. HoldLineThreshold

HoldLineThreshold = f(OffenseWeight)

Higher Defense orientation → stronger tendency to maintain formation
under pressure.

------------------------------------------------------------------------

## 3. ContactExpansionBias

ContactExpansionBias = f(OffenseWeight)

Higher Offense Weight → increased likelihood of widening engagement
front.

------------------------------------------------------------------------

# IV. Causal Chain (Non-Shortcut Rule)

Offense Weight → Engagement Posture\
Engagement Posture → Positional Adjustment\
Positional Adjustment → Local Density Variation\
Local Density Variation → EffectiveDamage via α\
EffectiveDamage → Potential Breakthrough

Direct mapping from Offense Weight → Damage or Breakthrough is
prohibited.

------------------------------------------------------------------------

# V. Separation Constraints

Offense / Defense Weight must remain orthogonal to:

-   Risk Appetite (risk tolerance under uncertainty)
-   Force Concentration Ratio (spatial compression)
-   Mobility Bias (movement intensity)
-   Time Preference (temporal discounting)

It governs posture, not compression, risk, or tempo.

------------------------------------------------------------------------

# VI. Legacy Mechanism Recovery Notes

The following legacy behaviors are allowed only if driven by Offense /
Defense Weight:

-   Aggressive line pushing
-   Defensive line stabilization
-   Controlled engagement width

The following are NOT allowed:

-   Direct damage multiplier
-   Artificial breakthrough probability bonus
-   Forced aggression override independent of posture logic

------------------------------------------------------------------------

# VII. Freeze Declaration

This mapping is frozen under Sandbox Governance Canonical v1.0.

Any modification requires: - Version increment - Explicit change log -
Structural closure declaration

Parameter Mapping Snapshot v1.0 --- Offense / Defense Weight\
Frozen / Authoritative
