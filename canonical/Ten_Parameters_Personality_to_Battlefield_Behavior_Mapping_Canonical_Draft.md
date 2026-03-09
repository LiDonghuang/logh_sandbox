# Ten Parameters Personality to Battlefield Behavior Mapping

Status: Governance Canonical Draft  
Scope: Conceptual architecture clarification  
Implementation: Not authorized by this document

---

## I. Purpose

This document clarifies how the canonical ten-parameter personality model relates to battlefield behavior.

Its purpose is interpretive discipline.

It exists to prevent future misreadings such as:

- parameter -> tactic
- parameter -> formation
- parameter -> direct battle outcome

None of those direct mappings are canonical.

---

## II. Core Mapping Chain

The correct structural chain is:

```text
Personality Parameters
-> Mechanism Bias / Threshold / Weight
-> Runtime Behavior
   (movement / targeting / pursuit / retreat)
-> Formation Geometry & Event Topology
-> Battle Outcome
```

This chain is one-way in interpretation.

Parameters influence runtime only through mechanism-layer rules.

They do not directly issue tactical commands.

---

## III. Layer Separation

### 1. Personality Layer

The personality layer contains only the canonical ten parameters:

- FCR
- MB
- ODW
- RA
- TP
- TL
- FR
- PR
- PD
- RT

These parameters express:

- preference
- tendency
- threshold orientation

They do not express:

- ability
- intelligence
- direct formation templates
- explicit tactic selection

### 2. Mechanism Layer

The mechanism layer converts personality into runtime control through:

- bias
- threshold
- weight
- trigger

Examples of mechanism-layer effects include:

- stronger or weaker movement-vector components
- different pursuit confirmation thresholds
- target selection bias
- retreat activation sensitivity

Mechanism rules are the only valid place where personality affects runtime behavior.

### 3. Result Layer

The result layer is what emerges from runtime execution:

- formation geometry
- event topology
- battle outcome

These are outputs of the system, not direct parameter declarations.

---

## IV. Runtime Behavior Mapping

At runtime, personality influences behavior only through implemented mechanisms such as:

- movement weighting
- pursuit confirmation
- retreat gating
- targeting priority logic

These mechanisms generate runtime behavior such as:

- approach direction
- cohesion restoration tendency
- extension tendency
- target preference
- pursuit continuation
- retreat timing

The runtime layer is therefore the only valid bridge between personality and battlefield behavior.

---

## V. Formation Geometry

Formation geometry must remain an emergent property of the movement vector field.

This is a binding doctrine.

Therefore:

- no parameter directly creates wedge, line, concave, or circular formations
- no parameter directly selects a tactical formation template
- no single parameter should be interpreted as a geometry generator

Instead, geometry emerges from the interaction of movement forces and runtime bias structure.

This preserves the doctrine established in `docs/architecture/Formation_Geometry_Doctrine_v1.0.md`.

---

## VI. Event Topology

Battlefield events also belong to the result layer.

Examples:

- First Contact
- First Kill
- Formation Cut
- Pocket Formation
- collapse-like pressure transitions

These events are not direct expressions of a single parameter.

They arise from runtime interaction between:

- movement
- contact logic
- targeting
- collapse-signal interpretation
- battle geometry

Parameters may bias the conditions that make events more likely, but they do not directly instantiate events.

---

## VII. Role of Specific Parameters

This document does not redefine any parameter.

It only clarifies how parameter meaning should be interpreted structurally.

Examples:

- `FR` influences resistance to deformation, not direct formation shape
- `MB` influences movement bias, not direct maneuver scripts
- `PD` influences pursuit-related thresholds, not direct order issuance
- `ODW` influences offense/defense weighting where implemented, not direct courage or competence

This distinction must remain explicit in all future engineering interpretation.

---

## VIII. Canonical Constraint

The ten parameters are the complete personality layer.

This document does not authorize:

- new pseudo-parameters
- new posture-parameter layer
- ability-language reinterpretation
- one-to-one parameter-to-tactic claims
- one-to-one parameter-to-formation claims

Any such expansion would require separate governance review.

---

## IX. Engineering Implication

Engineering should use this document as an interpretation rule:

1. map personality into mechanism-layer controls
2. observe runtime behavior
3. interpret geometry and events as emergent outputs

Engineering should not collapse these layers together during implementation or analysis.

---

## X. Unifying Statement

The sandbox does not model:

```text
parameter -> tactic
```

It models:

```text
parameter
-> mechanism bias / threshold / weight
-> runtime behavior
-> geometry and event topology
-> battle outcome
```

That is the canonical reading of personality-to-battlefield behavior mapping under the current architecture.
