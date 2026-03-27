# LOGH Sandbox

## Engineering Query

### dev_v2.0 Viewer-Local HP-Bucketed Inner Cluster Count

Status: Query only
Authority Requested From: Governance Main Thread
Scope: `viz3d_panda/` viewer-local unit rendering only

## Current confirmed repo state

- The close-range inner cluster in `viz3d_panda/unit_renderer.py` is currently fixed at `10` metallic-gray cuboids per unit.
- HP currently affects only the outer unit size bucket.
- Current governance-approved dual-layer rule explicitly does **not** allow HP to change the inner cuboid count.

## Human-driven request under review

Human requested a possible viewer-local enhancement:

- keep the current HP-based outer size buckets
- reduce the **number** of inner cluster cuboids when HP drops
- keep each individual inner cuboid at a fixed size
- do not change runtime, replay, or HP semantics

## Engineering read

This request appears to stay on the viewer-local side if kept narrow:

- no runtime change
- no replay protocol widening
- no settings surface growth
- no change to canonical HP meaning

However, it would still revise a currently explicit visual rule:

- HP would begin affecting **inner cluster count**, not only outer token size

That is why Engineering did **not** implement it directly.

## Narrow question to Governance

Is Engineering authorized to make the inner close-range cluster count follow the same existing HP bucket family, while keeping:

- per-cuboid size fixed
- no new user settings
- no replay/runtime changes
- no change to outer token ownership/semantics

Recommended bounded shape if authorized:

- reuse the existing HP bucket ladder
- map each bucket to a fixed inner cuboid count
- keep the current near/far cross-fade structure
- keep this viewer-local only

## Not requested in this query

- no realistic warship mesh path
- no generalized ship-proxy system
- no HP-driven color changes
- no HP-driven animation system
- no runtime ownership expansion

## Why this query exists

The current viewer-local rule is clear but rigid:

- outer token shrinks with HP
- inner cluster stays fixed at `10`

Human feedback indicates that a bounded HP-to-count reduction may read more naturally at close range, but Engineering considers that a governance decision rather than a safe silent tweak.
