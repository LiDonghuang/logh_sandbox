Scope: design note only

Status
- discussion / diagnosis only
- no implementation
- no push

Purpose
- explain why neutral pre-contact formation is currently much cleaner than battle
- explain why the current battle line still shows a center-ahead arc and later internal disorder
- identify the missing owner without proposing another patch loop

Current accepted read
- Recent Human read says:
  - neutral pre-contact transition is fast, mostly stable, and largely orderly
  - battle pre-contact still shows a center-ahead arc
  - later battle body is still disorderly
- Earlier local patches on:
  - hold smoothing
  - near-contact internal stability
  - battle-only front/fire-plane bias
  improved or changed some symptoms, but did not remove the early battle arc

Core diagnosis
- The decisive difference is not a small scalar.
- The decisive difference is owner structure in movement realization.

Neutral line: what it has
- In the neutral fixture path, runtime receives a real per-unit expected-position map.
- See `runtime/engine_skeleton.py::_build_fixture_expected_position_map()`.
- When `expected_position_candidate_active` is true for `neutral_transit_v1`, unit cohesion is pulled toward per-unit expected positions rather than only toward fleet centroid.
- This gives neutral a true per-unit formation-realization owner during transit.

Battle line: what it lacks
- In the current battle `v4a` line, test-run builds battle restore bundles and a soft-morphology reference surface.
- But battle currently uses that surface mainly to influence:
  - fleet-level target direction
  - movement heading
  - unit speed envelope
- Battle does not currently own a comparable per-unit expected-position realization path inside the runtime movement core.
- So battle pre-contact still falls back to a weaker combination of:
  - fleet-level target direction
  - centroid/cohesion tendencies
  - unit-level speed modulation

Why the center-ahead arc appears
- When battle lacks a true per-unit expected-position owner, pre-contact formation is realized indirectly.
- Indirect realization lets middle units preserve forward progress better than wings while lateral opening is still underway.
- The result is not primarily a post-contact fire-plane issue.
- It is a pre-contact formation-realization gap.

Why earlier fixes were limited
- Removing battle-only front/fire-plane direct axis bias was directionally reasonable, but it was not the owner of the early arc.
- Removing near-contact internal-stability smoothing also did not remove the arc, because the arc exists before the near-contact zone becomes the main owner.
- Therefore the current problem should not be read as:
  - a bad hold constant
  - a bad smoothing constant
  - a bad fire-plane bias alone

Sharper statement
- Neutral has a per-unit expected-position realization owner.
- Battle does not.
- This is now the sharpest explanation for:
  - battle pre-contact arc
  - weaker battle internal order
  - why neutral and battle diverge even when nominal formation targets are the same

Implication
- Further tuning of battle-only scalars is unlikely to remove this class of artifact reliably.
- If battle pre-contact formation is expected to become as orderly as neutral, battle needs a more honest formation-realization owner.

Implementation boundary
- This is not a small mathematical-tuning gap anymore.
- The likely next step is structural enough that it must be discussed before implementation.
- Two broad families exist:

1. test-run-side bounded bridge
- introduce a battle-side expected-position candidate path as a harness-owned experiment
- goal: prove the owner gap without rewriting frozen runtime semantics broadly

2. deeper touchpoint acknowledgement
- admit that battle formation realization is pressing against a deeper runtime owner boundary
- only choose this if the test-run-side bridge is not honest enough

Recommended next question
- not: "which scalar should be tuned next?"
- but: "what is the smallest honest battle-side expected-position realization owner we are willing to introduce?"

Bottom line
- The current early battle arc is best read as a formation-realization owner gap, not just a smoothing defect.
- Neutral is cleaner because runtime actually owns per-unit expected positions there.
- Battle still lacks that same class of owner.
