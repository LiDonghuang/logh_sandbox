# Governance Concept Memo

## Formation Geometry Doctrine

LOGH Fleet Sandbox

Status: Governance Concept Canonical  
Authority: Governance / Design Review Node  
Scope: Conceptual Architecture  
Implementation: Not authorized

---

# 1. Purpose

This memo clarifies the **structural origin of formation geometry** in the sandbox.

Historical warfare and the tactical narratives of *Legend of the Galactic Heroes* frequently feature recognizable formation geometries, including:

* wedge
* line
* concave
* circular formations

The sandbox must allow such formations to emerge naturally.

However, these geometries must **not arise from accidental parameter side-effects**.

Instead, they must emerge as the structural consequence of command personality interacting with battlefield physics.

This memo defines the conceptual doctrine governing formation geometry.

---

# 2. Core Governance Principle

Formation geometry must remain an **emergent property** of the movement vector field.

The sandbox must **never directly construct, prescribe, or hardcode formations**.

Instead, geometry must arise from the interaction of movement forces across the fleet.

Therefore:

```text
Formation Geometry
= emergent property of the movement vector field
```

Governance may influence geometry only **indirectly**, through parameters that bias movement vectors.

Direct geometry control is prohibited.

---

# 3. Structural Causal Chain

To maintain interpretability, formation geometry must follow a clear structural chain.

```text
Personality
    ↓
Tactical Posture
    ↓
Vector Bias
    ↓
Formation Geometry
    ↓
Battle Dynamics
```

Meaning of each layer:

**Personality**  
Ten-parameter archetype vector.

**Tactical Posture**  
Commander doctrine implied by parameter combination.

**Vector Bias**  
Directional tendencies in the movement field.

**Formation Geometry**  
Macroscopic fleet shape produced by velocity gradients.

**Battle Dynamics**  
Contact timing, encirclement, attrition, and collapse behavior.

This layered interpretation prevents parameters such as **FR** from being misinterpreted as formation generators.

---

# 4. Field-Level Nature of Formation Geometry

Formation geometry is not produced by discrete commands.

It arises from **velocity gradients across the fleet**.

Conceptually:

```text
movement_vector =
    cohesion
  + maneuver
  + enemy attraction
  + separation
  + boundary constraints
```

These components produce spatial differences in velocity.

Those differences create a **vector field with gradients**.

Formation geometry is therefore a **field-level phenomenon**, not a rule-based instruction.

---

# 5. Role of Formation Rigidity (FR)

The parameter **Formation Rigidity (FR)** must be interpreted precisely.

Correct definition:

```text
FR = resistance to formation deformation
```

Meaning:

* high FR → formations resist distortion
* low FR → formations deform easily under movement forces

FR does **not** define formation geometry.

FR only controls how strongly an existing formation shape persists.

This preserves the intended semantic meaning of the parameter.

---

# 6. Geometry Tendencies and Tactical Posture

Different formation shapes may emerge depending on tactical posture.

Examples:

| Posture tendency            | Possible geometry        |
| --------------------------- | ------------------------ |
| aggressive forward pressure | wedge                    |
| neutral advance             | line                     |
| defensive containment       | concave                  |
| maneuver encirclement       | curved or circular front |

These shapes should emerge from **combined vector biases** produced by parameter interactions.

Importantly:

```text
No single parameter should directly determine formation shape.
```

Geometry tendencies arise from the **combined influence** of parameters such as:

* MB (Mobility Bias)
* ODW (Offense/Defense Weight)
* TL (Targeting Logic)
* FR (rigidity influence on deformation)

Therefore concepts such as **curvature bias** should be understood as **posture tendencies**, not as new independent parameters.

The ten-parameter archetype system should remain stable.

---

# 7. Stray Detection Limitation

Current stray detection relies primarily on centroid distance.

```text
distance_from_centroid
```

This assumption fails when formations intentionally contain forward elements.

For example, wedge formations naturally contain forward units farther from the centroid.

These units are not stray.

Future diagnostic systems must therefore distinguish between:

* **role-based forward elements**
* **true formation detachment**

Potential future approach:

```text
distance_from_expected formation surface
```

However, this concept belongs to **future architecture exploration** and is not part of the current implementation.

---

# 8. Current Movement Architecture Status

Movement v3 experiments have identified key causal relationships in pre-contact geometry.

Evidence indicates:

* centroid cohesion strength affects wedge behavior
* stable operating ranges exist
* deterministic properties remain intact

Therefore movement v3 is currently in a **stabilization phase**.

The purpose of this phase is:

* parameter validation
* diagnostic confirmation
* behavioral consistency checks

No structural redesign is authorized during this phase.

---

# 9. Future Research Direction

The observations recorded in this memo suggest a long-term research direction.

Future movement architectures may explore:

```text
personality
→ tactical posture
→ vector bias structure
→ formation geometry
```

Such systems could allow different commanders to naturally produce different battlefield geometries.

However, this direction belongs to **future exploration phases** and is not part of current engineering work.

---

# 10. Governance Directive

Engineering should continue focusing on:

* movement v3 stabilization
* diagnostic verification
* parameter consistency

Structural redesign of formation generation is **not authorized** during the current phase.

This memo serves only as a **conceptual governance reference**.

---

# 11. Design Philosophy Reminder

The sandbox does not simulate war directly.

It simulates the **structural consequences of command personality within a deterministic battlefield system**.

Formation geometry must therefore arise from:

```text
personality
→ doctrine
→ vector bias
→ geometry
→ battle outcome
```

rather than from hardcoded formation rules.

---

End of Governance Concept Memo  
Formation Geometry Doctrine
