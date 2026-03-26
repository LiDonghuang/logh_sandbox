# Step 3 3D Formation vs Mapping vs Legality Split Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: Step 3 structural-draft-only layering note
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: clarifies the four-layer split objective -> formation -> mapping -> legality
Mapping Impact: split clarification only
Governance Impact: preserves the anti-collapse boundary between reference geometry and downstream feasibility in the 3D opening review
Backward Compatible: yes

Summary
- Formation reference, mapping, and legality must remain separate layers in 3D just as they were clarified in late 2D.
- Objective remains upstream and already answers where to go.
- Formation answers only reference geometry.
- Mapping answers assignment from units to reference slots.
- Legality answers final feasibility / projection only.

## 1. Layer Order

The intended order remains:

1. objective
2. formation reference
3. mapping
4. legality

This order matters because each layer answers a different question.

## 2. Objective Answers What

Objective answers:

- where the fleet should trend

Objective does not answer:

- the formation frame
- slot assignment
- spacing feasibility
- projection legality

This layer is already established and should not be reopened inside the formation turn.

## 3. Formation Reference Answers What

Formation reference answers:

- reference frame choice
- layout-family intent
- broad aspect/depth tendency
- intended axis-aligned spacing

Formation reference does not answer:

- which unit gets which slot
- whether a slot is feasible
- how collisions are resolved
- how movement is integrated

## 4. Mapping Answers What

Mapping answers:

- how stable unit identity maps to reference slots
- whether reflow/remapping is allowed
- how `expected_position_map` or equivalent reference output is produced

Mapping does not answer:

- final feasibility
- collision resolution
- boundary clipping
- legality overrides

## 5. Legality Answers What

Legality answers:

- whether a reference outcome is feasible
- how spacing conflicts are resolved downstream
- how projection/boundary/collision constraints are enforced

Legality does not answer:

- what the intended formation should be
- who owns slot identity
- what the objective means

## 6. Why 3D Makes This Split More Important, Not Less

In 3D, if these layers are blurred together too early, then:

1. formation reference silently becomes a movement package
2. mapping silently becomes projection
3. legality silently becomes attitude/frame authorship

That would collapse the same layer clarity that the 2D closeout explicitly preserved.

## 7. What Must Not Be Mixed Into Formation Contract v0.1

The following must stay out of the first 3D formation contract:

- mapping mode
- allow_reflow policy
- legality / feasibility fields
- collision / boundary rules
- movement response fields
- combat / targeting fields
- doctrine / posture semantics
- viewer rendering attributes

## 8. Bottom Line

The 3D first-draft reading should stay:

- objective = destination intent
- formation = reference geometry
- mapping = assignment to reference geometry
- legality = downstream feasibility

If the first 3D formation draft starts answering mapping or legality questions directly, then the layer split has already failed.
