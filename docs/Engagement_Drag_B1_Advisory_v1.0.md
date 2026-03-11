# Engagement Drag (B1) Advisory v1.0

LOGH Fleet Sandbox --- Structural Archive Note

Status: Archived (Not Active) Authority: Governance Core Phase: Post
V5.4 (Deferred Implementation)

------------------------------------------------------------------------

## I. Purpose

This document archives a future candidate mechanism:

**Engagement Drag (B1)**

It is not active in the current engine version. It is preserved for
future structural revisit after Cohesion / Collapse stabilization.

------------------------------------------------------------------------

## II. Motivation

Observed phenomenon: - Prolonged symmetric pushing between fleets - Low
dissipation during sustained engagement - Excessive global drift under
continuous contact

Design intention: Introduce a combat-local, delayed drag mechanism that
reduces fleet velocity based on previously received fire exposure.

This is not spatial damping. This is engagement-dependent damping.

------------------------------------------------------------------------

## III. Structural Definition (Proposed)

Let:

-   d_i(t-1) = damage received by unit i at tick (t-1)
-   HP_ref(t-1) = fleet-level reference HP at tick (t) start\
    (recommended: fleet mean or median HP)
-   N = number of alive units at tick t

Define fleet exposure:

E(t-1) = (1/N) \* sum_i clip( d_i(t-1) / HP_ref(t-1), 0, 1 )

Define engagement drag:

D(t) = clip( alpha \* E(t-1), 0, D_max )

Velocity scaling:

v'(t) = (1 - D(t)) \* v(t)

------------------------------------------------------------------------

## IV. Causality Discipline

-   Drag reads ONLY tick (t-1) damage.
-   Movement at tick t does not depend on same-tick combat.
-   No instantaneous feedback loop is introduced.

Causal chain:

combat(t-1) → drag(t) → movement(t)

------------------------------------------------------------------------

## V. Design Principles

1.  Deterministic
2.  Symmetric across sides
3.  No personality parameter coupling
4.  No spatial anchoring term
5.  No same-tick feedback
6.  Canonical constants (alpha, D_max), not archetype parameters

------------------------------------------------------------------------

## VI. Non-Activation Statement

Engagement Drag (B1) is currently: - Not implemented - Not
shadow-active - Not included in runtime

Reason: Cohesion / Collapse semantic stabilization must complete first.

------------------------------------------------------------------------

## VII. Future Revisit Conditions

The mechanism may be reactivated for consideration if:

-   Persistent symmetric drift remains after Collapse calibration
-   Behavior-layer events indicate excessive over-penetration
-   Contact stabilization is required without spatial anchoring

Revisit requires: - Shadow implementation - Full Gate validation -
Behavior event comparison

------------------------------------------------------------------------

End of Document
