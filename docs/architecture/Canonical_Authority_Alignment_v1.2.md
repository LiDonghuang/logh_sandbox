# Canonical Authority Alignment (Governance Directive)
Date: 2026-03-07
Status: Active
Scope: Engineering reference hierarchy alignment (no runtime behavior change)
Directive Basis: Governance Core instruction (Cross-Thread Protocol v1.2)

## 1. Authoritative Canonical References
Engineering shall treat the following as semantic authority:

### Governance Layer
- `Sandbox_Governance_Canonical_v1.1`
- `Sandbox_CrossThread_Protocol_v1.2`

### Archetype Layer
- `Strategic_Archetype_Layer_v1.5`

### Parameter Naming Canonical
- `Ten_Parameters_Canonical_Index_v1.1`
- Canonical names:
  - `FCR`, `MB`, `ODW`, `RA`, `TP`, `TL`, `FR`, `PR`, `PD`, `RT`

### Parameter Mapping Canonical
- `Parameter_Mapping_Snapshot_v1.1 (PD)` (active mapping authority)

### Runtime Parameter Input
- `analysis/archetypes_v1_5.json`

## 2. Conceptual Governance References (Non-Algorithmic)
- `Formation_Geometry_Doctrine_v1.0`

Usage rule:
- Treated as conceptual interpretation guidance.
- Not treated as direct algorithm implementation spec.

## 3. Superseded / Historical-Only References
These are historical references and must not be used as canonical authority:

- `Mapping_Snapshot_v1.1_PursuitDrive` (merged; historical only)
- `Ten_Parameters_Three_Class_Mapping_Essay_v1.1` (interpretive essay; non-spec)

## 4. Engineering Reference Priority
Engineering must follow this priority order:

1. Governance Canonical
2. Cross-Thread Protocol
3. Parameter Canonical Index
4. Parameter Mapping Snapshot
5. Archetype Layer
6. Runtime JSON
7. Conceptual Governance Memos

Rule:
- Lower-priority layers cannot override higher-priority layers.

## 5. Engineering Compliance Rules
Engineering must ensure:

1. Runtime code references canonical parameter names only.
2. Archetype parameter semantics align to `Strategic_Archetype_Layer_v1.5`.
3. Mapping semantics align to active `Parameter_Mapping_Snapshot_v1.1 (PD)`.
4. Concept memos are not used as direct code specs.

## 6. Notes
- This document aligns engineering interpretation and reporting behavior.
- It does not authorize runtime formula changes.
- It does not change phase boundaries.
