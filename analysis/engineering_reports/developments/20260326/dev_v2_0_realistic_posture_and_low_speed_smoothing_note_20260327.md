# dev_v2.0 realistic Posture Re-definition + Low-Speed Replay Smoothing

Date: 2026-03-27  
Scope: `viz3d_panda/` viewer-local readout/presentation only

## Identity

This viewer-local turn now reads as two bounded outcomes:

1. keep low-speed replay smoothing as an active presentation aid
2. keep `realistic` as a short-window human-readable travel-posture mode, but without turning it into a heavier heading-state machine

It does not change:

- runtime semantics
- replay ownership
- replay protocol
- objective / formation / legality meaning
- unit ontology

## realistic Mode: Current Local State

Current `realistic` now uses a stronger short-window net-displacement read than the older tangent-heavy version.

Current local rule:

- short centered / widened net displacement stays primary
- very small motion still holds the last usable display direction
- the earlier local experiment that added heavier reversal hysteresis + heading inertia is not kept as the active local shape of the mode

Current read intention remains:

- steadier than `effective`
- more human-readable than local tangent microscope behavior
- still viewer-local only

Current honest limit:

- early-stage read improved locally
- late-stage objective-area residual is still not closed
- this remaining late-stage issue should be treated as an open item for later governance discussion rather than claimed as solved here

## Low-Speed Replay Smoothing

Viewer playback now supports a bounded smoothing layer.

- default: on
- keyboard toggle: `M`
- overlay status: `smooth=on/off`

Smoothing remains bounded as follows:

- applies only during continuous playback
- does not apply during pause
- does not apply during single-step / hold-step inspection
- applies only for low-speed playback levels (`fps <= 12`)
- affects only displayed position and displayed heading
- tracked fleet camera now follows the interpolated presentation frame during low-speed continuous playback so camera motion no longer lags behind the smoothed visual frame

It does not alter:

- stored replay frames
- exact-frame inspection semantics
- runtime or replay data ownership

## Files Touched

- `viz3d_panda/replay_source.py`
- `viz3d_panda/app.py`

## Structured Summary

- Engine Version: `dev_v2.0`
- Modified Layer: viewer-local direction readout and playback presentation only
- Affected Parameters: none user-facing beyond the existing viewer-local direction-mode and playback surface
- New Variables Introduced: none in public settings; only internal posture-window and smoothing constants
- Cross-Dimension Coupling: none beyond existing replay consumption
- Mapping Impact: none
- Governance Impact: keeps the authorized low-speed smoothing active while recording that late-stage `realistic` residual remains open
- Backward Compatible: yes

Summary
- `realistic` remains a short-window travel-posture read, not a local-tangent microscope.
- The heavier local hysteresis/inertia experiment is not retained as the active shape of the mode.
- Low-speed continuous playback now smooths displayed position and displayed heading.
- Tracked camera motion follows the smoothed presentation frame during low-speed playback.
- Pause and step inspection remain exact-frame.
- Early-stage read improved locally, but late-stage `realistic` residual is still open.
