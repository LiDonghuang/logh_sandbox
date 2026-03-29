# Step 3 3D Turning Cost / Heading Inertia Discussion Note (2026-03-29)

Status: discussion note only  
Authority: structural / methodology discussion only  
Scope: future shared movement-substrate modernization line  
Implementation Status: closed in this turn

## Purpose

This note opens a bounded methodology discussion on turning cost / heading inertia as a future movement-substrate modernization line.

This note does not authorize:

- implementation
- default switching
- broad movement rewrite
- new personality surface

## Current Read

Current runtime should still be read as too close to near-instant heading response.

The strongest source-code reason is simple:

- movement composition resolves a `total_direction`
- per-tick orientation is then set directly from that resolved movement direction
- there is no explicit max turn-rate / heading inertia stage between desired direction and realized heading

So even when movement composition itself is nontrivial, heading response is still much closer to:

- “desired direction becomes current heading now”

than to:

- “desired direction is filtered through a bounded heading-change cost”

## Why Heading-Cost First Is the Right Modernization Read

The preferred first modernization read is:

- heading-change cost
- heading inertia
- max turn-rate

rather than:

- full linear acceleration-first physics

Reason:

1. it is the smallest meaningful seam that would change visible 3D motion posture
2. it is more directly tied to battle readability than full acceleration modeling
3. it is more local to orientation / turn behavior and therefore easier to keep bounded
4. it is less likely to explode into broad substrate coupling than a full velocity / acceleration rewrite

## Smallest Clean First Seam

The smallest clean future seam should likely sit between:

- desired movement direction
- realized heading / orientation update

not inside every upstream decision term.

That keeps the line readable:

- target / cohesion / separation can still express desired intent
- heading-cost logic becomes the bounded realization stage

This is structurally cleaner than trying to spread turn cost across:

- target gain
- separation gain
- posture bias
- restore terms

all at once.

## Best First Candidate Shapes

Current ranking:

1. bounded max turn-rate / heading relaxation
2. simple heading inertia filter
3. any more complex turn-cost family only later

Preferred first read:

- a small max turn-rate or heading-relaxation candidate is the cleanest first modernization

Not preferred as a first cut:

- full linear acceleration model
- coupled translational-acceleration-first physics
- broad momentum stack redesign

## Risks If This Line Advances Later

If implemented later, this line would create meaningful risks for:

### Neutral transit validation
- formation substrate evidence could become harder to interpret
- some current restore / spacing reads might partly change because realized heading would no longer snap to desired direction

### Battle readability
- readability may improve if motion posture becomes less twitchy
- but battle timing and closure reads could become less immediately transparent if turn response becomes too sluggish

### Formation restore behavior
- restore may need reinterpretation once heading response is no longer near-instant
- some current “restore strength” reads may actually be “heading realization” reads in disguise

## Recommended Governance / Engineering Posture

This line should remain open as methodology discussion only until the formation-substrate line is more settled.

Recommended sequence:

1. finish formation-substrate validation to a cleaner stopping point
2. then open one bounded heading-cost implementation-prep note
3. only after that consider a first candidate implementation

## Bottom Line

Current engineering read:

- yes, the runtime still reads too close to near-instant heading response
- yes, turning cost / heading inertia is the right first modernization lens
- no, this should not be implemented in the current turn
- yes, the future first candidate should likely be a bounded heading-relaxation / max-turn-rate seam rather than full acceleration-first physics
