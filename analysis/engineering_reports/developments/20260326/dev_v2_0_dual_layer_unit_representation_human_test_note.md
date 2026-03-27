# dev_v2.0 Dual-Layer Unit Representation Human Test Note

Date: 2026-03-26  
Scope: viewer-local human-read check

## What To Look For

### Far View

- units should still read mainly as wedge tokens
- cluster layer should stay subordinate

### Near View

- a unit should gradually read as a compact internal fleet cluster
- the cluster should not look like particles or debris
- heading should remain coherent as one group
- the inner `2/3/5` rows should sit comfortably inside the outer body rather than touching the edge
- the outer body should read closer to a trapezoid than a sharp dart

### Transition

- zooming should cross-fade smoothly
- no hard pop-in / pop-out should be visible

## Current Internal Smoke Read

Near camera:

- `near_token_alpha_scale = 0.125`
- `near_cluster_alpha_scale = 0.920`

Far camera:

- `far_token_alpha_scale = 1.000`
- `far_cluster_alpha_scale = 0.000`

Read:

- near/far dominance separation is working
- close-range cluster layer is visible
- far-range wedge layer stays dominant

## Halo Read

Current halo now uses:

- 3 layered rings
- stronger brightness and thickness
- slow pulse only on alpha
- slightly heavier ring weight than the first overlay pass

Intended read:

- easier to notice than before
- still subordinate to units
- not a new semantic overlay family
