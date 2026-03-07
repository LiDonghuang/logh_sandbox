# Parameter Mapping Snapshot v1.0

## Formation Rigidity

Status: Frozen / Authoritative\
Layer: Parameter Mapping Layer\
Anchor: Latest Archetype Version

------------------------------------------------------------------------

# I. Parameter Identity

Formation Rigidity\
Domain: \[1--10\] (normalized internally to \[0,1\])

Definition (Canonical): Controls structural resistance to deformation
and structural reconfiguration speed trade-off.

Formation Rigidity does NOT directly modify: - Damage - HitProbability -
Speed (base) - Risk Appetite - Offense / Defense Weight - Targeting
Logic - Time Preference

------------------------------------------------------------------------

# II. Core Interpretation

Formation Rigidity represents:

Structural Stability ↔ Structural Adaptability trade-off.

High FR → Stable but inflexible.\
Low FR → Flexible but fragile.

------------------------------------------------------------------------

# III. Functional Role in Sandbox Engine

Formation Rigidity influences Cohesion dynamics and structural
adaptability only.

It governs:

1.  Cohesion decay resistance
2.  Cohesion recovery rate
3.  Structural reconfiguration speed

------------------------------------------------------------------------

# IV. Derived Variables

Let FR ∈ \[0,1\] (normalized).

## 1. Cohesion Decay Multiplier

EffectiveCohesionDecay = BaseDecay × (1 - FR × k1)

Higher FR → slower decay under disturbance.

------------------------------------------------------------------------

## 2. Cohesion Recovery Multiplier

EffectiveCohesionRecovery = BaseRecovery × (1 - FR × k2)

Higher FR → slower recovery and re-stabilization.

------------------------------------------------------------------------

## 3. Reconfiguration Speed

ReconfigurationSpeed = BaseReconfiguration × (1 - FR)

Higher FR → slower structural adjustment and maneuver adaptation.

------------------------------------------------------------------------

# V. Causal Chain (Non-Shortcut Rule)

Formation Rigidity → Cohesion dynamics\
Cohesion dynamics → Structural stability or fragmentation\
Structural outcome → Breakthrough vulnerability or resilience

Formation Rigidity does NOT directly trigger Breakthrough.

------------------------------------------------------------------------

# VI. Orthogonality Constraint

Formation Rigidity must remain orthogonal to:

-   Force Concentration Ratio (compression intent)
-   Mobility Bias (movement intensity)
-   Offense / Defense Weight (engagement posture)
-   Risk Appetite (uncertainty tolerance)
-   Targeting Logic (target evaluation)
-   Time Preference (temporal discounting)

It governs structural response characteristics only.

------------------------------------------------------------------------

# VII. Six-Archetype Reference Intuition (Non-binding)

Bittenfeld → High FCR + Low FR\
Reinhard → High FCR + Mid-High FR\
Kircheis → Mid FCR + Mid FR\
Mittermeyer → Mid FCR + Low FR\
Reuenthal → Mid FCR + High FR\
Müller → Low FCR + High FR

These combinations illustrate stability--flexibility trade-offs.

------------------------------------------------------------------------

# VIII. Freeze Declaration

This mapping is frozen under Sandbox Governance Canonical v1.0.

Any modification requires: - Version increment - Explicit change log -
Structural closure declaration

Parameter Mapping Snapshot v1.0 --- Formation Rigidity\
Frozen / Authoritative
