# Parameter Mapping Snapshot v1.0

## Targeting Logic

Status: Frozen / Authoritative\
Layer: Parameter Mapping Layer\
Anchor: Latest Archetype Version

------------------------------------------------------------------------

# I. Parameter Identity

Targeting Logic\
Domain: \[1--10\] (normalized internally to \[0,1\])

Definition (Canonical): Controls structural focus of target selection
logic within visible enemy set.

Targeting Logic does NOT directly modify: - Damage - HitProbability -
Speed - Risk Appetite - Force Concentration Ratio - Offense / Defense
Weight - Time Preference

------------------------------------------------------------------------

# II. Continuous Interpretation

Targeting Logic is defined as:

StructureFocus ∈ \[0,1\]

0 → Structural fragmentation preference (Isolation focus)\
1 → Structural core focus (Density focus)

No discrete targeting categories are permitted.

------------------------------------------------------------------------

# III. TargetFeatures v1.0 (Fixed Feature Set)

Only the following four continuous features are permitted:

1.  LocalDensityScore ∈ \[0,1\]
2.  IsolationScore ∈ \[0,1\]
3.  StrategicValueScore ∈ \[0,1\]
4.  DistanceScore ∈ \[0,1\]

No additional TargetFeatures may be introduced without version
increment.

------------------------------------------------------------------------

# IV. TargetScore Function

TargetScore = w1 × LocalDensityScore + w2 × IsolationScore + w3 ×
StrategicValueScore - w4 × DistanceScore

Where:

w1 = StructureFocus\
w2 = 1 - StructureFocus

w3, w4 are fixed baseline weights (may be influenced by other parameters
in separate mappings).

------------------------------------------------------------------------

# V. Causal Chain (Non-Shortcut Rule)

Targeting Logic → StructureFocus\
StructureFocus → TargetScore weighting\
TargetScore → Target selection\
Target selection → Structural evolution\
Structural evolution → Breakthrough or Cohesion effects

Direct mapping from Targeting Logic → Damage or Breakthrough is
prohibited.

------------------------------------------------------------------------

# VI. Orthogonality Constraint

Targeting Logic must remain orthogonal to:

-   Risk Appetite (commitment threshold)
-   Offense / Defense Weight (engagement posture)
-   Mobility Bias (movement intensity)
-   Force Concentration Ratio (spatial compression)
-   Perception Radius (visibility domain)

It governs evaluation preference only.

------------------------------------------------------------------------

# VII. Reference TL Values (Six Archetypes)

The following normalized values are reference implementations for
current six-personality mapping (non-binding, explanatory only):

Reinhard (Decisive) → TL = 0.85\
Kircheis (Fragmentation) → TL = 0.15\
Mittermeyer (Mobile Pressure) → TL = 0.35\
Reuenthal (Balanced Elastic) → TL = 0.55\
Bittenfeld (Extreme Assault) → TL = 0.95\
Müller (Iron Wall) → TL = 0.65

These values illustrate structural tendencies only and may be adjusted
in future version updates without altering the core mapping framework.

------------------------------------------------------------------------

# VIII. Freeze Declaration

This mapping is frozen under Sandbox Governance Canonical v1.0.

Any modification requires: - Version increment - Explicit change log -
Structural closure declaration

Parameter Mapping Snapshot v1.0 --- Targeting Logic\
Frozen / Authoritative
