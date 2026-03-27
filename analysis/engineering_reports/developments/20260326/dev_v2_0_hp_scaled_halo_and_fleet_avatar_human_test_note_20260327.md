# dev_v2.0 HP-Scaled Halo + Fleet Avatar Human Test Note

Date: 2026-03-27  
Scope: viewer-local human-read check

## What To Look For

### Halo Radius

Read:

- halo should shrink as the fleet loses HP
- the change should feel gradual rather than jumpy
- halo should still remain a low-key fleet-size cue, not a new semantic overlay family

### Avatar Behavior

Read:

- avatar should appear above the fleet when the fleet is on screen
- avatar should follow fleet movement
- avatar should remain upright during orbit
- avatar should keep fixed on-screen size under zoom
- avatar should keep a stable `4:5` portrait ratio
- avatar should now show a faction-colored card frame rather than a bare image
- `P` should hide/show portraits without affecting any replay or simulation behavior

### Inner Cluster Visibility

Read:

- close-range inner cluster should be less likely to disappear behind the transparent outer wedge when the camera angle changes

## Focused Local Checks

Current local checks confirm:

- active-battle halo radius decreases with alive total HP
- avatar scale remains fixed across zoom changes
- avatar toggle defaults on and flips cleanly with `P`
- outer token and inner cluster now both render with depth-write disabled

Read:

- halo and avatar remain consumer-side only
- inner-cluster visibility improved locally under the current minimal transparency-order correction
