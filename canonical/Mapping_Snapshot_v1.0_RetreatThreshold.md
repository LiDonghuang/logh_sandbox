# Parameter Mapping Snapshot v1.0

## Retreat Threshold

Status: Frozen / Authoritative\
Layer: Parameter Mapping Layer\
Anchor: Latest Archetype Version

------------------------------------------------------------------------

# I. Parameter Identity

Retreat Threshold\
Domain: \[1--10\] (normalized internally to \[0,1\])

Definition (Canonical): Controls the structural deterioration level
required before initiating controlled withdrawal.

Retreat Threshold does NOT directly modify: - Damage - HitProbability -
Speed (base) - Risk Appetite - Offense / Defense Weight - Targeting
Logic - Time Preference - Formation Rigidity - Pursuit Threshold

------------------------------------------------------------------------

# II. Core Interpretation

Retreat Threshold defines:

The minimum confirmed own structural collapse signal required to
initiate retreat.

Low Threshold → early withdrawal\
High Threshold → late withdrawal / fight-on posture

------------------------------------------------------------------------

# III. Functional Role in Sandbox Engine

Let:

OwnCollapseSignal = 1 - OwnCohesion

Retreat condition:

If OwnCollapseSignal \> RetreatThreshold: InitiateRetreat()

------------------------------------------------------------------------

# IV. Structural Consequences of Retreat

Retreat modifies structural conditions indirectly:

-   Reduces engagement surface
-   Compresses formation locally
-   Decreases exposure
-   Reduces offensive density

Retreat does NOT directly modify Cohesion value.

------------------------------------------------------------------------

# V. Trade-off Structure

Low Retreat Threshold:

-   Lower catastrophic collapse probability\
-   Reduced flagship exposure\
    − Lost counterattack opportunity\
    − Potential premature disengagement

High Retreat Threshold:

-   Greater chance of recovery under pressure\
-   Maintains offensive presence\
    − Higher risk of structural breakdown\
    − Increased flagship vulnerability

------------------------------------------------------------------------

# VI. Symmetry with Pursuit Threshold

Retreat Threshold and Pursuit Threshold form a structural symmetry:

-   Pursuit governs exploitation of enemy collapse
-   Retreat governs response to own collapse

Both modify structure indirectly and do not directly alter Cohesion.

------------------------------------------------------------------------

# VII. Causal Chain (Non-Shortcut Rule)

Retreat Threshold → Retreat Decision\
Retreat Decision → Structural Compression\
Structural Compression → Exposure Variation\
Exposure Variation → Cohesion Dynamics\
Cohesion Dynamics → Stabilization or Collapse

Direct modification of Cohesion is prohibited.

------------------------------------------------------------------------

# VIII. Orthogonality Constraint

Retreat Threshold must remain orthogonal to:

-   Risk Appetite
-   Offense / Defense Weight
-   Mobility Bias
-   Formation Rigidity
-   Targeting Logic
-   Perception Radius
-   Time Preference

It governs withdrawal timing only.

------------------------------------------------------------------------

# IX. Freeze Declaration

This mapping is frozen under Sandbox Governance Canonical v1.0.

Any modification requires: - Version increment - Explicit change log -
Structural closure declaration

Parameter Mapping Snapshot v1.0 --- Retreat Threshold\
Frozen / Authoritative
