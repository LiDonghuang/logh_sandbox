# dev_v2.0 realistic Posture + Low-Speed Smoothing Human Test Note

Date: 2026-03-27  
Scope: viewer-local human-read check

## What To Look For

### realistic Mode

Use:

- `--direction-mode realistic`

Read:

- early-stage correction should feel calmer than the earlier tangent-heavy read
- units should look less like they are being redefined every frame by tiny local wiggles
- late-stage around the objective may still remain visually unsettled

Current honest expectation:

- early-stage looks improved locally
- late-stage is not yet a closed issue
- current repo-side read should therefore treat late-stage `realistic` as an active residual, not a solved item

### Low-Speed Playback

Use:

- playback gear `1/5`, `2/5`, or `3/5`

Read:

- continuous playback should look visibly smoother than exact whole-frame hopping
- tracked camera motion should stay aligned with the smoothed presentation frame during playback
- pause should still show the exact stored frame
- `N/B` stepping should still stay exact

### Toggle Surface

- `M` toggles smoothing on/off
- overlay shows `smooth=on/off`

## Focused Local Checks

Current local checks confirm:

- smoothing defaults on
- low-speed smoothing is active at `4 FPS`
- smoothing does not stay active for pause or exact-step inspection
- pause returns the viewer to the exact stored frame
- camera tracking now follows the interpolated presentation frame during continuous low-speed playback

Read:

- smoothing remains an active viewer-local improvement
- current late-stage `realistic` residual still remains open for later governance discussion
