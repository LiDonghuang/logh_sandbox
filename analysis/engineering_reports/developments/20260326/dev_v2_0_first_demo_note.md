# dev_v2.0 First Demo Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: additive 3D viewer demo container
Affected Parameters: none
New Variables Introduced: none beyond bootstrap files and isolated venv
Cross-Dimension Coupling: 2D runtime output replayed in a 3D viewer shell
Mapping Impact: none
Governance Impact: remains within viewer bootstrap authorization
Backward Compatible: yes

Summary
- The first demo path calls existing `test_run` execution and consumes returned `position_frames` in memory.
- The viewer opens a Panda3D window and renders unit placeholders on a 3D scene plane.
- Playback includes play/pause, step forward/back, looped time advance, and simple status overlay.
- Camera controls include pan, orbit, pitch, reset, and wheel zoom.
- This demo validates viewer bootstrap only; it does not establish a 3D baseline or runtime semantic layer.

## Demo Path

The current demo flow is:

1. call existing active-surface `test_run` execution
2. request captured `position_frames`
3. normalize them into a viewer-local replay bundle
4. render units as simple placeholders in Panda3D
5. drive playback from the captured frames only

This means the demo proves:

- current repo data can be fed into a 3D container immediately
- the first container can stay additive
- no replay-standard design round was required to get a moving 3D result

## Verified Demo Capabilities

The current first demo is intended to provide:

- Panda3D window startup
- current active-surface replay ingestion
- per-frame unit placeholder rendering
- simple playback loop
- simple camera interaction

Current overlay labels are intentionally kept on the English/ASCII side in this bootstrap turn so the viewer does not silently expand into font-asset setup work.

The viewer iterates whatever fleet buckets appear in `position_frames`, so the renderer is not hard-coded to exactly two fleets even though the first verified source path is the current dual-fleet active scenario.

## Most Obvious Next Step

The most obvious next step is to improve bounded viewer readability:

- better replay source presets
- optional target-line drawing or status layers
- cleaner camera presets for battlefield framing

## What Should Not Be Done Next

The first thing that should **not** happen after this demo is to let the viewer bootstrap silently turn into a 3D engine thread. In particular, this line should not immediately absorb:

- 3D movement semantics
- 3D formation mechanics
- 3D combat/targeting rewrite
- generalized runtime object redesign
