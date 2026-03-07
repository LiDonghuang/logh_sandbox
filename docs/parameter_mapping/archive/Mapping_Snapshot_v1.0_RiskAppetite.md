# Parameter Mapping Snapshot v1.0

## Risk Appetite

Status: Frozen / Authoritative\
Layer: Parameter Mapping Layer\
Anchor: Latest Archetype Version

------------------------------------------------------------------------

# I. Parameter Identity

Risk Appetite\
Domain: \[1--10\] (normalized internally to \[0,1\])

Definition (Canonical): Controls tolerance for uncertainty and
willingness to commit under ambiguous or disadvantageous local
conditions.

Risk Appetite does NOT directly modify: - Damage - HitProbability -
Speed - Force Concentration Ratio - Offense / Defense Weight

------------------------------------------------------------------------

# II. Functional Role in Sandbox Engine

Risk Appetite influences commitment thresholds under uncertainty.

It governs:

1.  Willingness to advance when LocalAdvantage is marginal
2.  Commitment behavior before clear superiority established
3.  Tolerance for exposure to concentrated enemy fire
4.  Breakthrough commitment threshold (indirectly)

------------------------------------------------------------------------

# III. Derived Variables

The following derived variables are permitted:

## 1. AdvanceUnderUncertaintyThreshold

AdvanceUnderUncertaintyThreshold = BaseThreshold -
(RiskAppetite_normalized × k)

Higher Risk Appetite → lower threshold → earlier commitment.

------------------------------------------------------------------------

## 2. BreakthroughCommitThreshold

BreakthroughCommitThreshold = f(RiskAppetite)

Higher Risk Appetite → more likely to invest resources in breakthrough
attempt under uncertainty.

------------------------------------------------------------------------

## 3. ExposureTolerance

ExposureTolerance = f(RiskAppetite)

Higher Risk Appetite → greater acceptance of temporary casualty
acceleration.

------------------------------------------------------------------------

# IV. Causal Chain (Non-Shortcut Rule)

Risk Appetite → Commitment Decision\
Commitment Decision → Increased Exposure\
Increased Exposure → Casualty Variation\
Casualty Variation → Structural Outcome\
Structural Outcome → Potential Breakthrough or Collapse

Direct mapping from Risk Appetite → Damage or HitProbability is
prohibited.

------------------------------------------------------------------------

# V. Orthogonality Constraint

Risk Appetite must remain orthogonal to:

-   Offense / Defense Weight (engagement posture)
-   Force Concentration Ratio (spatial compression)
-   Mobility Bias (movement intensity)
-   Time Preference (temporal discounting)

Risk Appetite governs uncertainty tolerance, not posture, compression,
tempo, or speed.

------------------------------------------------------------------------

# VI. Legacy Mechanism Recovery Notes

The following legacy behaviors are allowed only if driven by Risk
Appetite:

-   Early aggressive commitment
-   Willingness to push under incomplete information
-   High-variance outcome patterns

The following are NOT allowed:

-   Direct damage multiplier
-   Automatic aggression override
-   Forced breakthrough trigger independent of decision logic

------------------------------------------------------------------------

# VII. Freeze Declaration

This mapping is frozen under Sandbox Governance Canonical v1.0.

Any modification requires: - Version increment - Explicit change log -
Structural closure declaration

Parameter Mapping Snapshot v1.0 --- Risk Appetite\
Frozen / Authoritative
