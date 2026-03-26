# v4b Candidate A Structural Draft (2026-03-24)

Status: Limited Authorization  
Scope: inspect/plan-only structural draft for `v4b Candidate A`; no runtime implementation authorized

## 1. Governance Background

The current bounded sequence is:

- stop old-factor DOE expansion on the polluted path
- keep `v4a` as subtractive clarification
- keep the no-enemy fix frozen
- prepare the smallest formation-aware rebuild move without broad rewrite

Within that sequence, `Candidate A - Minimal Expected-Position Anchor` remains the most concrete next bounded target.

## 2. Why Candidate A Is The Current Focus

`v4a` reduced broad compaction and broad projection burden, but it did not remove the remaining local correction intensity.

The most likely surviving cause is still:

- centroid-directed restoration competing with forward transport and local separation

So the first rebuild move should replace the restoration object, not reopen the old shaping family.

## 3. How ObjectiveLocationSpec v0.1 Is Consumed In `neutral_transit_v1`

For the fixture path, the intended consumption model is:

- `anchor_point_xy` comes directly from fixture objective settings
- `forward_hint_xy` is the fleet-level shared forward trend toward that anchor
- `source_owner = fixture`
- `no_enemy_semantics = enemy_term_zero`

This objective spec is consumed by:

- the fleet frame generator
- the expected-position reference builder
- the existing fleet-level objective trend

It is **not** consumed as a slot map or legality rule.

## 4. How FormationSpec v0.1 Is Generated In The Fixture Path

The fixture path already supplies bounded inputs:

- single fleet
- stable initial geometry
- stable initial unit order
- no enemy
- no slot death/reflow pressure

So `FormationSpec v0.1` can be generated once from fixture-start state using:

- a centroid-anchored 2D fleet frame
- primary axis from `forward_hint_xy`
- rectangular lattice compatibility language
- deterministic width-depth aspect target
- fixed initial slot identity policy
- deterministic slot fill order

This keeps the spec fixture-bounded and avoids a generalized battle formation framework.

## 5. How `expected_position_map` Would Be Generated

The smallest inspectable route is:

1. capture the initial fleet centroid
2. build one initial 2D fleet frame from objective forward hint
3. project each unit's initial position into that local frame
4. store that local offset by stable `unit_id` order
5. at later ticks, rebuild the current fleet frame from the current anchor and current forward hint
6. reconstruct each unit's expected world position from the stored local offset

This means the first bounded Candidate A move can use:

- initial geometry
- stable unit identity
- no reflow
- no slot reassignment

without needing a generalized slot optimizer.

## 6. How Restoration Input Would Be Replaced

If later authorized, the bounded replacement point should be upstream of movement integration:

- current fixture path computes centroid-directed restoration input
- Candidate A would instead compute expected-position-directed restoration input

In plain terms:

- old input: `centroid - unit.position`
- bounded Candidate A input: `expected_position_map[unit_id] - unit.position`

What stays unchanged:

- fleet-level objective-forward trend
- low-level separation
- final projection / legality
- boundary handling

## 7. How Legality / Projection Stays Untouched

The structural fence is:

- reference mapping prepares expected positions
- movement consumes a different upstream restoration vector
- legality / projection continues exactly as-is

That means Candidate A must not:

- move projection earlier
- merge mapping into collision handling
- reinterpret projection as formation maintenance

## 8. How Battle Path / TL / Baseline Stay Unaffected

The intended hard fences are:

- fixture path only
- `neutral_transit_v1` only
- single-fleet only
- no battle-path activation
- no TL change
- no baseline selector replacement

If later implemented, the gate should be explicit and experimental.
It must not silently replace `v3a` or `v4a`.

## 9. Comparative Structural Reading

Why this draft stays smaller than a generalized reference-formation framework:

- it reuses initial geometry rather than building a reusable formation engine
- it fixes unit identity rather than supporting reassignment
- it keeps everything inside the neutral fixture path
- it leaves legality/projection alone

This is the narrowest path that still changes the restoration object itself.

## 10. Recommended First Bounded Implementation Target

If Governance later approves a very small implementation step, the recommended target is:

- fixture-only expected-position anchor capture from initial geometry
- fixture-only expected-position reconstruction from current fleet frame
- fixture-only replacement of centroid-directed restoration input

Not recommended for the first cut:

- generalized slot mapping service
- battle-path integration
- FR semantic rewrite
- layout reflow

## 11. Explicit Non-Authorizations

This draft does **not** authorize:

- runtime implementation
- broad movement rewrite
- generalized reference-formation framework
- slot reassignment
- TL modification
- battle-path activation
- baseline replacement
- 3D runtime work

## 12. Next-Step Request To Governance

If this draft is accepted, the next bounded request should be:

- one very small implementation authorization for fixture-only expected-position anchor preparation and restoration-input replacement
- paired only against current `v4a`
- with front stretching elevated as a primary validation target
