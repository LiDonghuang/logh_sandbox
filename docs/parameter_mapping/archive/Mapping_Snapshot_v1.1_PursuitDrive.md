# Parameter Mapping Snapshot v1.1

## Pursuit Drive (PD)

Status: Frozen / Authoritative  
Layer: Parameter Mapping Layer  
Anchor: Governance-approved canonical naming migration

------------------------------------------------------------------------

# I. Parameter Identity

Pursuit Drive (PD)  
Domain: [1--10] (normalized internally to [0,1])

Definition (Canonical): Controls pursuit tendency after enemy-structure collapse signals appear.

PD does NOT directly modify:
- Damage
- HitProbability
- Speed (base)
- Risk Appetite
- Offense / Defense Weight
- Targeting Logic
- Time Preference
- Formation Rigidity
- Cohesion value

------------------------------------------------------------------------

# II. Core Interpretation

PD defines pursuit tendency strength.

Low PD -> conservative pursuit  
High PD -> stronger pursuit tendency

------------------------------------------------------------------------

# III. Engine-Compatible Derived Threshold

PD is not a threshold parameter.

For decision compatibility, engine internals may derive:

PursuitConfirmThreshold = 1 - PD_norm

where:

EnemyCollapseSignal = 1 - EnemyCohesion

Decision comparison structure remains unchanged:

If EnemyCollapseSignal > PursuitConfirmThreshold: EngageDeepPursuit()

------------------------------------------------------------------------

# IV. Causal Chain (Non-Shortcut Rule)

Pursuit Drive -> DeepPursuit Decision  
DeepPursuit Decision -> Structural Stretch  
Structural Stretch -> Exposure Variation  
Exposure Variation -> Cohesion Dynamics  
Cohesion Dynamics -> Breakthrough or Stabilization

Direct Cohesion modification is prohibited.

------------------------------------------------------------------------

# V. Orthogonality Constraint

Pursuit Drive remains orthogonal to:
- Risk Appetite
- Offense / Defense Weight
- Mobility Bias
- Formation Rigidity
- Perception Radius
- Targeting Logic

------------------------------------------------------------------------

# VI. Replacement Notice

This snapshot supersedes prior v1.0 pursuit mapping in active governance usage.
Legacy references are archive-only.

------------------------------------------------------------------------

# VII. Freeze Declaration

This mapping is frozen under Sandbox Governance Canonical v1.0+.
Any further modification requires explicit Governance approval and version increment.

