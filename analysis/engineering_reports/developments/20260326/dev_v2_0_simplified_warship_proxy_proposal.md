# dev_v2.0 Simplified Warship Proxy Proposal

Date: 2026-03-26  
Scope: proposal only; no runtime/viewer implementation in this turn

## Identity

This note is a bounded proposal for a future viewer-local experiment only.

It does not authorize or claim:

- replacement of the current fixed 10-cuboid inner cluster
- direct use of the existing `warship_symmetric_rebuild_v2.glb`
- replay/runtime/settings changes
- unit-semantic ownership growth inside `viz3d_panda/`

Current implementation remains:

- outer wedge token
- inner fixed 10-cuboid metallic-gray cluster

## Why A Proxy Instead Of The Full Bundle

Current bundle inspection shows:

- `warship_symmetric_rebuild_v2.obj` is much flatter and more practical than `.glb`
- `.glb` explodes into many Panda3D geom nodes
- even `.obj` is still far heavier than the current cuboid cluster

So the cleanest next experiment would not be "use the bundle directly."

It would be:

- derive a tiny warship-like proxy from the bundle's silhouette and massing
- keep it to `2` to `4` primitive bodies
- continue using viewer-local fixed internal layout

## Proposed Proxy Shape

Recommended first proxy:

1. main hull body
   - long narrow box
2. aft block
   - shorter, slightly wider rear box
3. bridge / dorsal block
   - small raised top box

Optional fourth piece only if still visually worthwhile:

4. nose taper block
   - short forward prism or wedge-like cap

This keeps the proxy readable as "warship-like" without turning the viewer into a ship-model system.

## Proposed Use Path

If a later viewer-local trial is approved:

- keep unit count at the current fixed `10`
- replace each cuboid with the same fixed simplified proxy
- keep the current distance-driven cross-fade structure
- keep the same cluster ownership and heading behavior

## Why This Is The Narrow Path

This path would preserve:

- fixed ship count
- fixed local layout
- no HP-count semantics
- no replay widening
- no runtime touch
- no generalized asset pipeline

It would also avoid the worst current risks:

- direct `glb` scene-node explosion
- importing a heavy external asset family into the live viewer path
- turning a small visual turn into a ship-model program

## Recommendation

If Governance wants a future experiment, the narrowest safe order is:

1. keep current cuboid cluster as baseline
2. authorize one viewer-local proxy-only trial
3. build the proxy from `2` to `4` primitive bodies
4. do not use the full `glb` as the runtime-rendered per-ship mesh

## Structured Summary

- Engine Version: `dev_v2.0`
- Modified Layer: none; proposal only
- Affected Parameters: none
- New Variables Introduced: none
- Cross-Dimension Coupling: none
- Mapping Impact: none
- Governance Impact: identifies a possible future narrow viewer-only proxy path without requesting implementation in this turn
- Backward Compatible: yes

Summary
- Current inner layer remains the fixed 10-cuboid cluster.
- Full bundle use is too heavy for the present viewer path.
- A future narrow experiment could use a `2` to `4` primitive warship-like proxy.
- The proxy should be derived from the bundle as reference, not used as a live heavy mesh.
