# dev_v2.0 Dual-Layer Unit Representation

Date: 2026-03-26  
Scope: `viz3d_panda/` viewer-local unit rendering only

## Identity

This turn adds a distance-driven dual-layer unit representation inside the existing Panda3D viewer.

It does not change:

- runtime behavior
- replay protocol
- HP meaning
- direction-mode semantics
- semantic ownership

Viewer remains a consumer only.

## Outer Layer

The outer layer keeps the current wedge token.

- far-range readability remains anchored on the wedge
- base token alpha is raised to `0.80`
- near camera, the wedge fades down rather than permanently covering the inner layer

## Inner Layer

The inner layer is a fixed close-range cluster.

- 10 metallic-gray cuboids
- approximate aspect ratio `4:1:1`
- stable fixed local layout
- non-uniform `2/3/5` row structure
- shallow forward/back depth and lateral spread
- whole cluster follows unit heading through the shared unit-local parent

It does not introduce:

- HP-driven ship-count changes
- random per-frame layout
- random per-ship rotation
- complex ship-model family

## Shape Read

After the initial close-range pass, the local fit was refined once more:

- the outer wedge was pulled back from a too-sharp profile toward a more trapezoid-like body
- the `2/3/5` inner cluster now sits farther from the outer edge
- front/mid/rear row spacing is intentionally non-uniform so the cluster reads as wedge-compatible rather than grid-like

## Distance Rule

The viewer uses an internal-only near/far band and continuous cross-fade.

- near band = `max(18.0, arena_size * 0.11)`
- far band = `max(70.0, arena_size * 0.28)`

Read:

- near view: cluster dominates, wedge is still faintly present
- far view: wedge dominates, cluster fades out
- no hard switch is used

## Halo Adjustment

During the same viewer-local pass, the fleet halo was also strengthened:

- brighter
- thicker
- multi-layered for a soft blur read
- slow alpha pulse only
- slightly stronger again after the first pass so it remains visible without becoming a semantic overlay

This is still a viewer-local overlay effect only.

## Files Touched

- `viz3d_panda/unit_renderer.py`
- `viz3d_panda/app.py`

## Structured Summary

- Engine Version: `dev_v2.0`
- Modified Layer: viewer-local unit rendering only
- Affected Parameters: none user-facing
- New Variables Introduced: none user-facing; only internal near/far cross-fade constants
- Cross-Dimension Coupling: none beyond existing replay consumption
- Mapping Impact: none
- Governance Impact: implements the authorized dual-layer visual enhancement without widening ownership
- Backward Compatible: yes

Summary
- Wedge token remains the far-range readable carrier.
- Close-range view now reveals a fixed 10-cuboid metallic-gray cluster.
- Transition is continuous, not hard-switched.
- HP still only scales the whole unit bucket.
- Direction-mode semantics remain unchanged.
- Fleet halo is slightly strengthened in the same viewer-local pass.
