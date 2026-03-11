# Phase V.2 --- Mobility Bias Canonical Activation

Engine Version: v5.0-alpha4\
Status: Authorized\
Type: Structural Upgrade\
Scope: Movement Layer Only

------------------------------------------------------------------------

## 0. Phase V Default Combat Baseline

Effective immediately, Phase V adopts the following canonical default:

**attack_range = 5.0**

Semantic constraints:

-   Not bound to arena size\
-   Not bound to spacing\
-   Not bound to unit type\
-   Serves as Phase V geometric stability anchor\
-   May not be altered prior to targeting-system revision

This value must be reflected in:

-   `test_run_v1_0.settings.json`\
-   Phase V reference scenario\
-   Phase Chronicle documentation

------------------------------------------------------------------------

## I. Objective

Upgrade `mobility_bias` from experimental knob to Canonical Archetype
Mapping parameter.

Phase V transitions from:

> FR-only structural system

to:

> FR × MB dual-parameter dynamical system

------------------------------------------------------------------------

## II. Canonical Mapping Definition

Let:

-   `mobility_bias ∈ [1, 10]`
-   Neutral value = 5
-   `max_MB_eff = 0.2`

Mapping rule:

MB_eff = 0.2 \* (mobility_bias - 5) / 5

Constraints:

-   Continuous\
-   Monotonic\
-   No thresholds\
-   Clipped to \[-0.2, +0.2\]\
-   No additional tunable parameters

Critical invariant:

mobility_bias = 5 must be bitwise-equivalent to v5.0-alpha3 baseline
behavior.

------------------------------------------------------------------------

## III. Implementation Constraints

1.  Insert inside `integrate_movement` before normalization.
2.  Reweight only non-cohesion movement vector components.
3.  Do not alter:
    -   Cohesion
    -   FSR
    -   Contact logic
    -   Targeting logic
    -   Combat resolution
    -   Projection sequence
4.  No stochastic branches.
5.  No multi-pass projection.

------------------------------------------------------------------------

## IV. Gate Requirements

All must pass:

1.  Determinism\
2.  mobility_bias = 5 → bitwise baseline equivalence\
3.  Mirror metric degradation ≤ +5%\
4.  Jitter degradation ≤ +10%\
5.  No new attractor-class signal\
6.  Runtime overhead ≤ +10%

------------------------------------------------------------------------

## V. Validation Matrix

Fixed scenario parameters:

-   attack_range = 5\
-   FSR = enabled (0.1)\
-   Contact hysteresis = enabled\
-   Boundary = disabled

Test grid:

-   FR ∈ {2, 5, 8}\
-   mobility_bias ∈ {2, 5, 8}

Required outputs:

-   Alive curve crossing detection\
-   Focus-Fire Concentration (FFC)\
-   Orbit ratio\
-   Mirror metric\
-   Jitter metric\
-   Attractor proxy signals

------------------------------------------------------------------------

## VI. Explicit Non-Goals

-   No targeting modification\
-   No attack range modification\
-   No pursuit_drive activation\
-   No combat-layer modification

------------------------------------------------------------------------

## VII. Phase Discipline

Until Phase V.2 validation completes:

-   Default attack_range must remain 5\
-   No targeting logic revision permitted\
-   No additional archetype parameter may enter runtime

------------------------------------------------------------------------

## VIII. Structural Significance

This upgrade establishes:

-   Formation Rigidity (FR) as structural stiffness axis\
-   Mobility Bias (MB) as maneuver preference axis

Together forming a two-dimensional dynamical personality space.

Phase V formally enters the Dual-Parameter Dynamics stage.

------------------------------------------------------------------------

End of Phase V.2 Canonical Activation v5.0-alpha4
