# Step 3 3D Objective Ownership And Layering Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: Step 3 structural-draft-only ownership/layering record
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: clarifies how objective meaning stays runtime-owned while replay/view stay consumer layers
Mapping Impact: ownership clarification only
Governance Impact: keeps objective separate from formation, legality, and viewer ownership in the first 3D draft turn
Backward Compatible: yes

Summary
- Objective contract belongs to the runtime-facing contract layer, not the viewer layer.
- Runtime owns canonical meaning and consumption of the objective.
- Replay should transfer already-owned objective results, not define them.
- Viewer may read and display objective results, but may not own their semantics.
- Objective must stay separate from formation and legality even in 3D.

## 1. Objective Contract Layer

The 3D objective contract belongs to:

- the runtime-facing contract layer

It sits upstream of:

- formation reference language
- movement integration
- legality / projection
- viewer rendering

Its job is only to express where the fleet should trend and who owns that objective source.

## 2. Runtime Ownership

Runtime owns:

- canonical meaning of the objective fields
- allowed owner readings
- consumption of the objective during bounded mechanism work

Runtime does not hand objective meaning downward to the viewer to reinterpret.

## 3. Replay Transfer

Replay should:

- transfer objective results as already-owned runtime data
- preserve field identity without redefining meaning

Replay should not:

- invent new objective semantics
- expand the objective contract into a rendering bundle

## 4. Viewer Consumption

Viewer may:

- read objective-related results
- render objective markers or transit traces later if separately authorized
- remain a consumer of replay output

Viewer may not:

- own canonical objective meaning
- define fallback rules
- define legality or formation semantics around the objective

## 5. Why Viewer Cannot Own Objective Semantics

If the viewer owns objective semantics, then:

- replay/view layering collapses
- semantic meaning becomes display-coupled
- Step 2 anti-fat guardrails break

The viewer container must continue to follow:

- viewer consumes, runtime owns

## 6. Why Objective Must Stay Separate From Formation And Legality

Objective answers:

- where the fleet should trend

It does not answer:

- how the fleet frame is built
- whether a move is legal
- how spacing or extents should be enforced

Keeping these separate prevents the first 3D contract from becoming a hidden frame/legality package before those layers are explicitly reviewed.
