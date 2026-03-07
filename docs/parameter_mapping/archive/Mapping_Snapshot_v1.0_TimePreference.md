# Parameter Mapping Snapshot v1.0

## Time Preference

Status: Frozen / Authoritative\
Layer: Parameter Mapping Layer\
Anchor: Latest Archetype Version

------------------------------------------------------------------------

# I. Parameter Identity

Time Preference\
Domain: \[1--10\] (normalized internally to \[0,1\])

Definition (Canonical): Controls temporal discount rate applied to
delayed strategic outcomes.

Time Preference does NOT directly modify: - Damage - HitProbability -
Speed - Force Concentration Ratio - Risk Appetite - Offense / Defense
Weight

------------------------------------------------------------------------

# II. Core Interpretation

Time Preference defines a temporal valuation function.

It governs:

How much future gains are discounted relative to immediate gains.

Higher Time Preference → stronger discount of delayed outcomes.\
Lower Time Preference → greater valuation of long-term structural
outcomes.

This parameter does NOT represent impatience.\
It represents temporal value weighting.

------------------------------------------------------------------------

# III. Derived Variable

## 1. Temporal Discount Factor (λ)

λ = f(TimePreference_normalized)

λ ≥ 0

Higher Time Preference → higher λ → faster discounting of delayed
rewards.

------------------------------------------------------------------------

# IV. Decision Utility Structure

All commitment-level decisions must use a temporal utility structure:

Utility = ImmediateGain + DiscountedFutureGain

Where:

DiscountedFutureGain = FutureGain × exp(-λ × Δt)

Δt = estimated delay before outcome realization.

------------------------------------------------------------------------

# V. Behavioral Consequences

High Time Preference:

-   Prioritizes immediate tactical advantage
-   Compresses engagement windows
-   Expands small advantages early
-   May over-commit before long-term structure stabilizes

Low Time Preference:

-   Tolerates prolonged engagement
-   Values structural maturation
-   Avoids premature expansion
-   May miss early breakthrough windows

------------------------------------------------------------------------

# VI. Causal Chain (Non-Shortcut Rule)

Time Preference → Temporal Discount λ\
Temporal Discount λ → Utility Calculation\
Utility Calculation → Commitment Decision\
Commitment Decision → Structural Evolution\
Structural Evolution → Breakthrough or Long-War Outcome

Direct mapping from Time Preference → Damage, Speed, or Breakthrough is
prohibited.

------------------------------------------------------------------------

# VII. Separation Constraints

Time Preference must remain orthogonal to:

-   Risk Appetite (uncertainty tolerance)
-   Offense / Defense Weight (engagement posture)
-   Mobility Bias (movement intensity)
-   Force Concentration Ratio (spatial compression)

Time Preference governs temporal valuation only.

------------------------------------------------------------------------

# VIII. Engine Requirement

Sandbox must maintain a temporal dimension (t).

However:

-   No mandatory supply decay required.
-   No automatic resource degradation required.
-   Temporal valuation operates at decision layer only.

------------------------------------------------------------------------

# IX. Freeze Declaration

This mapping is frozen under Sandbox Governance Canonical v1.0.

Any modification requires: - Version increment - Explicit change log -
Structural closure declaration

Parameter Mapping Snapshot v1.0 --- Time Preference\
Frozen / Authoritative
