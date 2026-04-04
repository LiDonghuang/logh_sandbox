# v4a Current Mechanism Flow

Version scope: current PR `#6` local `v4a` line as of 2026-04-03  
Carrier: Markdown + Mermaid  
Purpose: Human-readable flow diagram of the current `v4a` mechanism surface  
Non-scope: diagnosis, repair proposal, merge claim, default-switch claim

---

## 0. Reading Guide

This document describes the **current** `v4a` mechanism flow only.

It intentionally does **not** judge whether a step is correct or incorrect.
It only shows:

- what currently owns which stage
- how signals move between stages
- where current battle / formation / terminal / combat paths branch

Color coding follows the current five discontinuity classes, but is used here
only as a **classification legend**, not as a quality judgment.

### Color Legend

- Class A: Owner / State
- Class B: Reference / Axis
- Class C: Force / Speed-Envelope
- Class D: Targeting / Combat
- Class E: Terminal / Settle
- Neutral gray: shared plumbing / data handoff

### Arrow Legend

To avoid ambiguity, the diagrams use three arrow meanings:

- `-->|stage / calls|`  
  stage progression or same-tick function call order

- `-->|write now / direct feed|`  
  direct state write or direct current-stage data feed

- `-.->|store / bias later|`  
  indirect influence:
  computed now, stored in bundle/state, consumed later by another stage

---

## 1. Top-Level v4a Flow

```mermaid
flowchart TD

    S["Layered settings + scenario prep<br/>test_run settings_accessor / scenario"]:::shared
    I["Initial state + v4a reference bundle<br/>axis / extents / phases / battle bundle"]:::shared
    T["Engine tick step"]:::shared

    S -->|prepare| I -->|seed state| T

    T -->|calls| C1["evaluate_cohesion"]:::shared
    C1 -->|calls| C2["evaluate_target"]:::shared
    C2 -->|calls| C3["integrate_movement"]:::shared
    C3 -->|calls| C4["resolve_combat<br/>frozen runtime hot path"]:::D
    C4 -->|produce| N["State(t+1)"]:::shared

    C2 -->|battle branch| BATTLEA["Battle Layer A<br/>global enemy relation + d* + hold"]:::A
    C2 -->|neutral branch| NEUTRALA["Neutral objective read<br/>same broad stop-chasing surface"]:::A

    BATTLEA -->|compute now| BREF["reference_distance / desired_distance<br/>hold_weight / approach_scale"]:::C
    BATTLEA -->|compute + store| BGEOM["effective_fire_axis<br/>engagement_geometry_active<br/>front_reorientation_weight"]:::B
    NEUTRALA -->|compute now| NOBJ["objective direction / stop_radius arrival gain"]:::A

    BREF -->|write now| TD["last_target_direction<br/>last_engagement_intensity"]:::B
    NOBJ -->|write now| TD

    BGEOM -.->|bias later| MAXIS["morphology_axis_current_xy<br/>movement_heading_current_xy"]:::B
    TD -->|direct feed now| MAXIS
    I -->|seed / carry bundle| MAXIS

    MAXIS -->|write current| MSHAPE["forward/lateral extents<br/>material phases<br/>shape_err"]:::B
    MSHAPE -->|produce| MREF["expected world positions<br/>reference surface"]:::B

    TD -->|direct feed now| MSPEED["shape_vs_advance<br/>engaged speed envelope<br/>attack-direction speed scales"]:::C
    MREF -->|direct feed now| MSPEED
    MSPEED -->|write now| MMOVE["unit max_speed shaping + movement integration"]:::C

    MMOVE -->|feeds combat snapshot| C4

    C4 -->|compute now| TARGET["target selection in range<br/>engaged_target_id"]:::D
    C4 -->|compute now| FIREQ["angle-based fire quality<br/>orientation vs target direction"]:::D
    C4 -->|compute now| CONTACT["contact hysteresis / in_contact / damage events"]:::D

    TARGET -->|write now| N
    FIREQ -->|write now| N
    CONTACT -->|write now| N

    N -->|event only| TERM["objective_reached event<br/>no hard terminal latch path"]:::E

    classDef shared fill:#f3f4f6,stroke:#6b7280,color:#111827,stroke-width:1px;
    classDef A fill:#fde68a,stroke:#b45309,color:#111827,stroke-width:1px;
    classDef B fill:#bfdbfe,stroke:#1d4ed8,color:#111827,stroke-width:1px;
    classDef C fill:#fecaca,stroke:#b91c1c,color:#111827,stroke-width:1px;
    classDef D fill:#c7f9cc,stroke:#15803d,color:#111827,stroke-width:1px;
    classDef E fill:#ddd6fe,stroke:#7c3aed,color:#111827,stroke-width:1px;
```

---

## 2. Battle-Side Flow Detail

```mermaid
flowchart LR

    G["Enemy fleet relation<br/>fleet centroid to enemy centroid"]:::shared
    DS["d* computation<br/>attack_range + own_extent + enemy_extent"]:::A
    H["hold_weight<br/>battle_hold_weight_strength × hold band relation"]:::C
    P["approach_scale = 1 - hold_weight"]:::C

    EF["effective_fire_axis<br/>aggregate engaged attack directions"]:::B
    EA["engagement_geometry_active"]:::A
    FRW["front_reorientation_weight"]:::B
    FA["morphology/front axis bias"]:::B

    G -->|direct feed now| DS -->|write now| H -->|write now| P
    EF -->|direct feed now| FRW
    EA -->|direct feed now| FRW
    FRW -->|store / bias later| FA

    P -->|write now| TD["last_target_direction"]:::B
    FA -.->|later bias front axis| TD

    classDef shared fill:#f3f4f6,stroke:#6b7280,color:#111827,stroke-width:1px;
    classDef A fill:#fde68a,stroke:#b45309,color:#111827,stroke-width:1px;
    classDef B fill:#bfdbfe,stroke:#1d4ed8,color:#111827,stroke-width:1px;
    classDef C fill:#fecaca,stroke:#b91c1c,color:#111827,stroke-width:1px;
```

---

## 3. Movement / Formation Realization Detail

```mermaid
flowchart LR

    TD["last_target_direction"]:::B -->|direct feed now| HEAD["movement_heading_current_xy"]:::B
    AX["morphology_axis_current_xy"]:::B -->|direct feed now| REF["reference surface / expected world positions"]:::B
    SH["shape_vs_advance"]:::C -->|direct feed now| SPD["transition speed shaping"]:::C
    ENG["engaged speed envelope<br/>forward / lateral / backward scales"]:::C -->|direct feed now| SPD
    REF -->|direct feed now| SPD
    HEAD -->|direct feed now| SPD
    SPD -->|write now| MOVE["integrate_movement"]:::C

    classDef B fill:#bfdbfe,stroke:#1d4ed8,color:#111827,stroke-width:1px;
    classDef C fill:#fecaca,stroke:#b91c1c,color:#111827,stroke-width:1px;
```

---

## 4. Combat / Targeting / Damage Detail

```mermaid
flowchart LR

    U["Alive units snapshot"]:::shared -->|scan now| SEL["target selection in attack range"]:::D
    SEL -->|write now| ENGAGED["engaged_target_id / engaged state"]:::D
    ENGAGED -->|direct feed now| ANG["orientation vs target direction"]:::D
    ANG -->|direct feed now| DMG["damage quality multiplier"]:::D
    ENGAGED -->|direct feed now| HYS["contact hysteresis<br/>r_enter / r_exit"]:::D

    classDef shared fill:#f3f4f6,stroke:#6b7280,color:#111827,stroke-width:1px;
    classDef D fill:#c7f9cc,stroke:#15803d,color:#111827,stroke-width:1px;
```

---

## 5. Neutral Validation Surface

```mermaid
flowchart LR

    OBJ["Fixture objective anchor"]:::shared -->|direct feed now| ARR["arrival gain / stop_radius relation"]:::A
    ARR -->|write now| TD["last_target_direction"]:::B
    TD -->|direct feed now| AX["morphology axis / reference surface / movement shaping"]:::B
    AX -->|event only| REACH["objective_reached event<br/>no hard terminal latch"]:::E

    classDef shared fill:#f3f4f6,stroke:#6b7280,color:#111827,stroke-width:1px;
    classDef A fill:#fde68a,stroke:#b45309,color:#111827,stroke-width:1px;
    classDef B fill:#bfdbfe,stroke:#1d4ed8,color:#111827,stroke-width:1px;
    classDef E fill:#ddd6fe,stroke:#7c3aed,color:#111827,stroke-width:1px;
```

---

## 6. Current Active Observability Surface

Current Human-readable observation for this line is centered on:

- fleet-centroid trajectory
- alive-unit body observation
- 3D HUD battle-focused debug rows such as:
  - `Kinetics: v / h`
  - `eng_act`
  - `front_rw`
  - `fire_da`

These are observation surfaces only.
They are not runtime owners by themselves.
