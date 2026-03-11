# Cohesion v2 --- Canonical Mechanism Definition v1.0

LOGH Fleet Sandbox\
Phase V.4 --- Structural Evolution\
Status: Canonical\
Authority: Governance Core\
Date: 2026-03-XX

------------------------------------------------------------------------

## I. Purpose

This document formally redefines **Cohesion** within the LOGH Fleet
Sandbox.

Cohesion is no longer a time-recursive personality-driven scalar.

Cohesion v2 is defined as:

> A purely geometric, objective measurement of battlefield
> exploitability.

It is a structural observable.

Not a behavioral modifier.\
Not a personality projection.\
Not a time-decay function.

------------------------------------------------------------------------

## II. Canonical Principle

Cohesion(t) must satisfy:

1.  Depend only on current unit positions.\
2.  Not depend on any personality parameter (FR, MB, PD, etc.).\
3.  Not use time-recursive smoothing.\
4.  Be deterministic.\
5.  Be permutation-invariant (unit order independent).\
6.  Preserve mirror symmetry.\
7.  Remain within \[0, 1\].

Cohesion is a "physical thermometer," not a strategic evaluator.

Strategic interpretation belongs to the decision layer (PD).

------------------------------------------------------------------------

## III. Formal Definition

Let:

Exploitability(t) = F(geometry at time t)

Cohesion(t) = 1 − Exploitability(t)

Where Exploitability is constructed from geometric observables only.

------------------------------------------------------------------------

## IV. Exploitability Components

Exploitability is composed of the following normalized geometric
observables:

### 1. Connectivity (Fragmentation)

Metric:\
Largest Connected Component Ratio (LCC ratio)

Definition:\
LCC_ratio = size_of_largest_connected_component / total_units

Fragmentation_component = 1 − LCC_ratio

Interpretation:\
Higher fragmentation → higher exploitability.

No spectral (λ₂) computation is used in v1.0.

------------------------------------------------------------------------

### 2. Dispersion (Compactness Loss)

Metric:\
Quantile-based dispersion ratio.

Example form:\
dispersion = Q90_distance / Q50_distance

Normalized to \[0,1\] via fixed canonical mapping.

Interpretation:\
Higher dispersion → weaker formation compactness.

No absolute radius threshold is used.

------------------------------------------------------------------------

### 3. Outlier Mass (Pocket Proxy)

Metric:\
IQR-based tail proportion.

Definition:\
outlier_ratio = fraction of units beyond (Q75 + k × IQR)

k is a fixed internal canonical constant (not a personality parameter).

Interpretation:\
Higher outlier_ratio → more exploitable pocket structure.

------------------------------------------------------------------------

### 4. Elongation (Line Stretch)

Metric:\
PCA eigenvalue ratio.

Definition:\
elongation = 1 − (λ2 / (λ1 + ε))

Where:\
λ1 ≥ λ2 are covariance eigenvalues of unit positions.

Interpretation:\
Higher elongation → stretched line formation → increased exploitability.

------------------------------------------------------------------------

## V. Exploitability Aggregation

Exploitability is aggregated using complement product form:

Exploitability = 1 − Π (1 − component_i)

Where component_i ∈ \[0,1\].

This ensures:

-   Any severe structural weakness raises exploitability.\
-   Multiple moderate weaknesses compound.\
-   No single component dominates artificially.

------------------------------------------------------------------------

## VI. Relationship to Personality Parameters

Cohesion does NOT read:

-   Formation Rigidity (FR)\
-   Mobility Bias (MB)\
-   Pursuit Drive (PD)\
-   Retreat Threshold (RT)\
-   Offense/Defense Weight\
-   Any other personality dimension

Personality affects:

-   Movement dynamics\
-   Decision thresholds\
-   Tactical response

Cohesion is an observation, not a control signal.

------------------------------------------------------------------------

## VII. Collapse and Decision Layer Separation

EnemyCollapseSignal remains:

EnemyCollapseSignal = 1 − EnemyCohesion

Decision layer MAY define:

StrengthAdvantage = normalized_alive_units_ratio

OpportunitySignal = EnemyCollapseSignal × StrengthAdvantage

Pursuit confirmation logic operates on OpportunitySignal, not directly
on Cohesion.

This preserves layer separation:

Geometry → Cohesion → Collapse\
Strength → Opportunity\
PD → Decision

------------------------------------------------------------------------

## VIII. Stability Constraints

Cohesion v2 must:

-   Not introduce oscillatory instability.\
-   Not create artificial mirror equalization.\
-   Not introduce attractor-class behavior.\
-   Preserve determinism.

------------------------------------------------------------------------

## IX. Known Structural Consequences

1.  Cohesion becomes more responsive to real geometric events.\
2.  PD trigger windows become structure-dependent rather than
    time-dependent.\
3.  Mirror amplification may shift but must not structurally worsen.\
4.  Cohesion curve may exhibit higher variance than v1.0.

These effects are accepted under Phase V.4 Structural Evolution.

------------------------------------------------------------------------

## X. Versioning Rule

Any future modification to Cohesion must:

1.  Reference this document explicitly.\
2.  State which components are modified.\
3.  Justify changes in structural terms.\
4.  Preserve the observation/control separation principle.

------------------------------------------------------------------------

End of Cohesion v2 Canonical Mechanism v1.0
