# Parameter Mapping Snapshot v1.0

## Perception Radius

Status: Frozen / Authoritative\
Layer: Parameter Mapping Layer\
Anchor: Latest Archetype Version

------------------------------------------------------------------------

# I. Parameter Identity

Perception Radius\
Domain: \[1--10\] (normalized internally to \[0,1\])

Definition (Canonical): Controls spatial perception coverage and
structural resolution trade-off.

Perception Radius does NOT directly modify: - Damage - HitProbability -
Speed - Risk Appetite - Force Concentration Ratio - Offense / Defense
Weight - Targeting Logic - Time Preference - Formation Rigidity

------------------------------------------------------------------------

# II. Core Interpretation

Perception Radius represents a fixed information resource trade-off:

Coverage ↑ → Structural resolution ↓\
Coverage ↓ → Structural resolution ↑

No information delay model is used in v1.0.\
No stochastic perception error is introduced.

------------------------------------------------------------------------

# III. Functional Role in Sandbox Engine

Perception Radius influences:

1.  VisibleSet (which enemy units are considered perceptible)
2.  Structural feature resolution accuracy

------------------------------------------------------------------------

# IV. Coverage Model

EffectivePerceptionRadius = BaseRadius × PR_normalized

Units outside this radius are excluded from decision calculations.

------------------------------------------------------------------------

# V. Resolution Model

PerceptionResolution = 1 / (1 + k × PR_normalized)

Higher PR → lower resolution (flattened structural contrast).\
Lower PR → higher resolution (sharper structural contrast).

------------------------------------------------------------------------

# VI. Application to TargetFeatures

ObservedFeature = TrueFeature × PerceptionResolution

Applied to:

-   LocalDensityScore
-   IsolationScore
-   StrategicValueScore (optional, if range-dependent)

DistanceScore remains geometrically computed.

No random noise is introduced.

------------------------------------------------------------------------

# VII. Behavioral Trade-off

High Perception Radius:

-   Wider situational awareness\
-   Earlier flank detection\
    − Reduced contrast between dense and sparse targets\
    − More diffuse target prioritization

Low Perception Radius:

-   Precise local structural discrimination\
-   Sharper weak-point identification\
    − Vulnerable to out-of-range maneuver\
    − Slower recognition of global threats

------------------------------------------------------------------------

# VIII. Orthogonality Constraint

Perception Radius must remain orthogonal to:

-   Targeting Logic (evaluation weighting)
-   Risk Appetite (commitment threshold)
-   Mobility Bias (movement intensity)
-   Formation Rigidity (structural elasticity)
-   Time Preference (temporal discounting)

It governs information coverage and resolution only.

------------------------------------------------------------------------

# IX. Archetype Reference Note

Six-archetype Perception values are not frozen at this stage. They will
be calibrated after full ten-parameter mapping completion.

------------------------------------------------------------------------

# X. Freeze Declaration

This mapping is frozen under Sandbox Governance Canonical v1.0.

Any modification requires: - Version increment - Explicit change log -
Structural closure declaration

Parameter Mapping Snapshot v1.0 --- Perception Radius\
Frozen / Authoritative
