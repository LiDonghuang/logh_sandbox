# Step 3 3D Formation Fast Visible Path Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: Step 3 structural-draft-only carrier-path note
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: proposes the narrowest future visible-formation carrier by extending the already-bounded objective/fixture path without changing ownership
Mapping Impact: planning only; mapping remains a later distinct layer
Governance Impact: identifies the fastest human-visible 3D formation path while preserving the existing objective / formation / mapping / legality split
Backward Compatible: yes

Summary
- The fastest safe path to a human-visible 3D formation should remain on a bounded neutral-transit-like carrier.
- That carrier should stay single-fleet, no-enemy, and objective-led.
- The first visible formation should not start from battle path or multi-fleet interaction.
- The first visible formation family should be one fixed, shallow `rect_lattice_3d`-style reference family only.
- This family is the narrowest 3D extension of the accepted 2D `rect_lattice_2d` reading.
- Viewer should still consume already-owned formation results only.
- The first visible turn should not open generalized formation selection, legality, combat, doctrine, or renderer-owned semantics.

## 1. Scope

This note answers one narrow Step 3 question only:

what is the fastest path that could let humans see a visible 3D formation soon, without prematurely opening legality, combat, doctrine, or a generalized 3D formation system?

It does not authorize:

- formation runtime code
- mapping code
- legality / projection code
- viewer-owned formation semantics
- battle-path formation activation

## 2. Fastest Visible Path: Main Judgment

The fastest safe visible-formation path should remain:

- single-fleet
- no-enemy
- neutral-transit-like
- fixture-bounded
- objective-led

The reason is simple:

the existing neutral-transit carrier is already the narrowest place where objective ownership, stop semantics, and viewer consumption have been proven to stay bounded.

If the first visible formation instead starts from:

- battle path
- multi-fleet interaction
- enemy-aware transit
- generalized viewer overlays

then the formation turn would immediately be contaminated by combat, legality, or visualization-surface growth.

## 3. Recommended First Carrier Candidate

The recommended first visible-formation carrier should be:

- the existing bounded neutral-transit fixture path
- with objective remaining upstream owner
- with formation results added only as a bounded runtime-side fixture result

That means the first visible carrier should still look like:

- one fleet only
- one destination only
- no enemy term beyond the already-established objective rule
- no firing
- no pursuit / retreat switching
- no battle semantics

This keeps the visible-formation question narrow:

can a single fleet maintain one explicit 3D reference geometry while trending toward one already-owned objective anchor?

That is the fastest human-visible question that does not silently reopen broader systems.

## 4. Recommended First Visible Formation Family

The first visible formation should allow only one fixed family:

- `rect_lattice_3d` in a shallow, bounded reading

That reading should mean:

- the 2D accepted `rect_lattice_2d` family is extended into 3D by adding bounded depth layering
- not a generalized volume-filling formation generator
- not a family registry
- not a fleet-doctrine selector

Why this family is the narrowest choice:

1. it is the closest 3D extension of the already accepted 2D reference language
2. it keeps the visual question easy for humans to read
3. it avoids inventing a new 3D-only shape family before layering is stable
4. it avoids confusing "visible 3D formation" with "many formation options"

For the first visible turn, "3D formation" should mean:

- one fixed shallow lattice family
- explicit depth layering
- deterministic slot identity expectation
- no dynamic family switching

## 5. Why This Should Still Be Objective-Led

The first visible formation path must remain downstream of objective:

- objective answers where to go
- formation answers reference geometry only

That means the first visible formation turn should not redefine:

- destination ownership
- fallback target semantics
- stop semantics
- no-enemy handling

If those are reopened, then the work is no longer a formation opening.

## 6. Why Mapping And Legality Must Stay Closed

The first visible formation should not require full mapping or legality to be opened.

The intended narrow reading is:

- formation reference becomes visible first
- mapping remains a later assignment question
- legality remains a later feasibility question

This is important because otherwise "let humans see 3D formation" quickly turns into:

- slot projection
- collision handling
- boundary feasibility
- reflow policy
- movement correction

That would skip over the layer split that Step 2 and the objective line worked hard to preserve.

## 7. Viewer Role In The Fast Visible Path

`viz3d_panda/` should remain only:

- a replay/view consumer
- a readout/display surface for already-owned formation results

It should not become:

- the author of formation semantics
- the author of fallback frame construction
- the owner of layout family meaning

So the fast visible path should not begin by asking:

- what new scene marker package should the viewer invent?

It should begin by asking:

- what smallest runtime-owned formation result could later be shown through the existing viewer?

## 8. What The First Visible Turn Should Still Exclude

Even if human-visible 3D formation is the next practical goal, the first visible turn should still exclude:

- generalized formation-family selection
- doctrine / posture packages
- legality / projection fields
- combat / targeting semantics
- full roll / bank / attitude authorship
- moving-objective carriers
- multi-waypoint transit
- multi-fleet / enemy-aware visible formation carriers
- viewer-owned semantic overlays

These are all ways the visible-formation turn could quietly become a broad 3D mechanism turn.

## 9. Recommended Bottom-Line Reading

The fastest safe path to "humans can see 3D formation" is:

- keep the already-bounded neutral-transit-like carrier
- keep it single-fleet and no-enemy
- keep objective as the upstream owner
- add one fixed shallow `rect_lattice_3d` reference family only
- keep viewer as consumer only
- delay mapping / legality / combat / doctrine until later separate openings

That path is narrow enough to move quickly, but still disciplined enough not to reopen the whole 3D stack.
