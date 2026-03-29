# Future 3D Runtime Computation Principles Review Note (2026-03-29)

Status: discussion note only  
Authority: structural review / repo-formalization aid only  
Scope: future 3D runtime computation organization principles  
Implementation Status: closed in this turn

## Purpose

This note captures the current future-3D computation discussion as a repo-side structural review asset.

It does not activate a canonical doctrine and does not authorize implementation.

## Strong Lines Preserved

The current draft should continue to preserve these lines:

1. semantic boundary first
2. local / bounded / sparse computation
3. broad-phase / narrow-phase organization
4. legality as a reference -> feasible middle layer
5. exact / approximate / observer-only distinction
6. multi-rate organization
7. simulation / rendering decoupling
8. research-budget vs interactive-budget divergence without semantic drift
9. human-readable evidence as a control surface

These lines remain worth preserving because they reduce the risk that future 3D work will collapse into:

- monolithic simulation
- viewer-owned semantics
- stealth coupling between research exploration and maintained interactive paths

## Strengthening Additions Worth Making

The draft should now be strengthened by explicitly adding three more lines.

### A. Determinism / replayability first

Future 3D work should preserve:

- reproducible runtime outcomes
- replay-safe surfaces
- evidence that can be re-run and compared

This matters because complex 3D interaction can otherwise hide structural regressions behind “looks plausible.”

### B. Shared candidate surface / shared neighborhood service

Where broad local interaction is needed, the future design should prefer:

- a shared candidate-generation surface
- or a shared neighborhood service

over:

- multiple divergent pair-search stacks buried inside separate layers

This is an organizational principle, not an implementation commitment.

### C. State-surface / source-of-truth discipline

Future 3D computation should stay explicit about:

- what state is runtime-authoritative
- what is derived candidate state
- what is observer-only
- what is viewer-only

This principle is especially important once:

- formation reference
- legality middle layers
- contact-side resolution
- rendering readouts

all coexist.

## External References Status

Any external references cited for this line should be read only as:

- organizational inspirations
- structural comparison points
- vocabulary aids

They should not be read as:

- direct implementation commitments
- imported doctrine
- implied approval of a specific simulation architecture

## Recommended Repo-Side Next Form

Best current next form:

- remain discussion note only for now

Reason:

- the formation-substrate line is still actively validating in PR #6
- turning-cost and contact-substrate lines are not yet mature
- moving too early into a durable engineering doctrine document would risk freezing abstractions before the substrate lines stabilize

## Practical Read for Near-Term Engineering

Near-term engineering should use this note as:

- an organizing review aid
- a scope-control tool
- a reminder that future 3D work should stay sparse, layered, replayable, and semantically disciplined

It should not yet be used as:

- a direct implementation checklist
- a layer-activation mandate
- a replacement for concrete bounded carrier review

## Bottom Line

Current engineering read:

- the draft is strong enough to deserve repo-side anchoring
- it should be strengthened with:
  - determinism / replayability first
  - shared candidate surface / shared neighborhood service
  - state-surface / source-of-truth discipline
- cited external references should remain inspirations only
- the correct next repo form is still discussion-note level, not durable doctrine activation yet
