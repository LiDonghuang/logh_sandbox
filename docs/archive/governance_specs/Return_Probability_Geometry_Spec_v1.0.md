# 📐 Return Probability Geometry Specification (RP-G v1.0)

Status: Governance Technical Appendix  
Scope: Diagnostic / Theoretical Foundation  
Applies to: Phase V (FSR + Projection + Movement Interaction)  
Behavior Modification: None  
Normative Power: Constraint Reference Only  

---

## I. Purpose

This document formalizes the geometric basis of **return probability** for persistent outlier diagnosis.

Objective:

> Guarantee that no unintended absorbing geometric state exists in the fleet dynamics.

This specification defines measurable quantities used to determine whether:

1. A unit's failure to re-enter formation is caused by projection geometry.
2. A unit is externally pushed by separation bias.
3. A local shell barrier eliminates inward feasible motion.

---

## II. Definitions

For fleet f:

- Unit position: x_i ∈ ℝ²
- Fleet centroid: C_f = (1/N_f) Σ x_i
- Relative vector: r_i = x_i − C_f
- Radial distance: ρ_i = ||r_i||
- Radial direction (toward centroid): d̂_i = (C_f − x_i) / ||C_f − x_i||

A unit is considered **outlier** if:

ρ_i > R_shell + δ

Where:

- R_shell may be defined as R_p90 or RMS radius.
- δ is a small margin.

---

## III. Effective Radial Motion

### 1. Free (Pre-Projection) Radial Component

Let:

ṽ_i = u_i + Δ_i^FSR

Where:

- u_i = movement composite (cohesion, separation, pursuit)
- Δ_i^FSR = isotropic scale relaxation

Define:

ṽ_r,i = ṽ_i · d̂_i

Interpretation:

- ṽ_r,i < 0 → free dynamics attempts inward motion.
- ṽ_r,i > 0 → free dynamics pushes outward.

---

### 2. Post-Projection Radial Component

After projection:

v_r,i = (x_i^(t+1) − x_i^t) · d̂_i

---

### 3. Radial Feasibility Ratio

Define:

κ_i = v_r,i / (ṽ_r,i + ε)

Interpretation:

- ṽ_r,i < 0 but v_r,i ≈ 0 → Projection suppresses inward motion.
- ṽ_r,i > 0 → Movement bias outward.
- κ_i ≈ 1 → Projection not suppressing radial motion.
- κ_i ≈ 0 → Radial component nearly eliminated.

---

## IV. Shell Barrier Geometry

### 1. Radial Gap Measure

For nearest neighbors j in inward half-space:

g_i = min_j (x_j − x_i) · d̂_i

Interpretation:

- g_i ≈ 0 → No inward corridor.
- Larger g_i → Geometric space exists for re-entry.

---

### 2. Return Corridor Density (Continuous)

Within angular sector ±φ around d̂_i:

Compute local density or nearest-neighbor spacing.

Purpose:

> Avoid binary blocked/open saturation metrics.

---

## V. Return Probability Definition

Within window W:

P_return = Pr(∃ τ ∈ [t, t+W]: ρ_i^τ ≤ R_shell)

System-level requirement:

> P_return > 0 must hold for any outlier configuration unless explicitly designed otherwise.

---

## VI. Absorbing Geometry Condition

An unintended absorbing state exists if:

1. ṽ_r,i < 0 frequently,
2. v_r,i ≥ 0 for extended window,
3. g_i ≈ 0,
4. κ_i → 0 consistently.

This indicates:

> Projection geometry eliminates inward feasible motion.

---

## VII. Governance Principle

The engine must not create hidden absorbing subspaces
unless such structure is explicitly part of strategic modeling.

Return feasibility must remain geometrically accessible.

No behavioral patch may be applied unless
the absorbing condition is formally verified.

---

## VIII. Scope Limitations

- This document does not prescribe repair methods.
- It does not authorize projection clamp.
- It does not alter combat or targeting logic.
- It provides measurable geometric diagnostics only.

---

## Interpretation Layer (Non-Normative)

Persistent outlier is not a “strategy.”
It is a geometric feasibility failure
unless shown otherwise.
