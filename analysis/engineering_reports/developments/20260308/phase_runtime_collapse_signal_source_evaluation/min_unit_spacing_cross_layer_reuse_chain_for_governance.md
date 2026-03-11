# Mechanism Map - `min_unit_spacing / separation_radius` Cross-Layer Reuse Chain

## Scope

This note documents a single structural fact for governance review:

`min_unit_spacing`

from run settings is currently reused as:

`separation_radius`

across multiple layers.

This is an engineering diagnosis only.

No redesign is proposed in this note.

## One-Line Summary

The current system uses one scalar for:

- initial formation spacing
- movement separation force radius
- post-move minimum-distance projection
- cohesion/connectivity graph radius
- `v3_test` scale reference radius

Therefore a physics-layer spacing value is also acting as a semantics-layer fragmentation threshold.

## Current Reuse Chain

```text
test_run/test_run_v1_0.settings.json
    battlefield.min_unit_spacing
        鈫?test_run/test_run_v1_0.py
    unit_spacing
        鈫?    build_initial_state(..., unit_spacing=...)
        鈫?    run_simulation(..., separation_radius=unit_spacing)
        鈫?runtime/engine_skeleton.py
    self.separation_radius
        鈹溾攢 initial movement separation branch
        鈹溾攢 post-move hard projection threshold
        鈹溾攢 cohesion_v2 connectivity radius
        鈹斺攢 cohesion_v3_shadow:
             鈹溾攢 c_conn connectivity radius
             鈹斺攢 r_ref scale baseline
```

## Layer-by-Layer Use

### 1. Initial Formation Geometry

`test_run/test_run_v1_0.py:1744`
`test_run/test_run_v1_0.py:1758`

The initial fleet grid uses `unit_spacing` directly for row and lateral offsets.

Meaning:

- larger value -> looser initial formation
- smaller value -> denser initial formation

This is a legitimate geometry-layer use.

### 2. Movement Separation Force

`runtime/engine_skeleton.py:499`
`runtime/engine_skeleton.py:726`

Inside `integrate_movement()`:

- `r_sep = self.separation_radius`
- pairwise soft separation activates only when `distance < r_sep`

Formula shape:

```text
decay = 1 - distance / r_sep
separation_dir = normalized(pos_i - pos_j)
separation_component = separation_dir * decay
```

Meaning:

- this is a short-range repulsion radius
- it directly affects pre-contact approach geometry

This is a legitimate movement-layer use.

### 3. Post-Move Minimum-Distance Projection

`runtime/engine_skeleton.py:504`
`runtime/engine_skeleton.py:1175`
`runtime/engine_skeleton.py:1198`

After tentative movement:

- `min_unit_spacing = self.separation_radius`
- if two units are still closer than this threshold, they are projected apart

Formula shape:

```text
penetration = min_unit_spacing - distance
correction = normal * penetration
```

Meaning:

- this is not a force trend
- it is a hard geometric correction step

This is also a legitimate physics-layer use.

### 4. `cohesion_v2` Connectivity / Fragmentation

`runtime/engine_skeleton.py:222`

`cohesion_v2` computes `lcc_ratio` using:

```text
connect_radius = self.separation_radius
```

Two units are connected if:

```text
distance <= connect_radius
```

Then:

```text
lcc_ratio -> f_frag = 1 - lcc_ratio -> cohesion_v2
```

Meaning:

- the same spacing radius is now serving as the semantic definition of fragmentation

This is the first cross-layer reuse that matters for the current cohesion-collapse issue.

### 5. `cohesion_v3_shadow` Connectivity

`runtime/engine_skeleton.py:358`

`v3_test` / `cohesion_v3_shadow` computes:

```text
c_conn
```

using the same graph condition:

```text
connect_radius = self.separation_radius
distance <= connect_radius
```

Meaning:

- `v3_test` shares the same connectivity backbone as `v2`

This is why the recent DOE work found a shared low-connectivity problem across both sources.

### 6. `cohesion_v3_shadow` Scale Baseline

`runtime/engine_skeleton.py:341`

`v3_test` also defines:

```text
r_ref = self.separation_radius * sqrt(n_alive)
rho = r / r_ref
```

Meaning:

- the same spacing scalar also defines the expected fleet-scale radius for the `rho / c_scale` branch

In the recent 66-run diagnostic DOE, this branch did **not** dominate:

- `rho` stayed in-band
- `c_scale` stayed effectively `1.0`

So in the tested regime, the shared problem came from connectivity, not from this scale term.

## Why Governance Should Care

The same scalar is currently doing two different jobs:

### Physics Job

```text
How close may units physically get?
```

### Semantics Job

```text
When should the fleet be considered fragmented / collapse-prone?
```

Those are not obviously the same question.

The recent cohesion-collapse DOE evidence suggests that binding them together is now distorting runtime interpretation.

## Relation to Recent DOE Findings

The two recent findings become coherent under this map:

### 648-run DOE

- `v3_test` changed runtime intensity meaningfully
- but `first_deep_pursuit_tick` stayed saturated at `t=1`

### 66-run diagnostic DOE

- `v2` low values were dominated by `fragmentation`
- `v3_test` low values were dominated by `c_conn`
- `rho / c_scale` did not dominate

Combined interpretation:

```text
Both sources inherit an overly harsh connectivity reading from the same spacing-derived graph radius.
```

## Governance-Relevant Question

The key future design question is not merely:

```text
v2 or v3_test?
```

It is:

```text
Should physical spacing radius and semantic fragmentation radius remain the same variable?
```

That is the structurally important question exposed by the recent evaluation work.

## Current Engineering Posture

No mechanism change is requested in this note.

This note exists only to make the cross-layer reuse chain explicit before governance discusses the next cohesion-collapse design step.

