# dev_v2.0 Visual Refinement V1 Human Test Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: viewer-local human test guidance only
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: none
Mapping Impact: none
Governance Impact: records a bounded Round V1 human-check surface only
Backward Compatible: yes

Summary
- Default fire-link mode is now `minimal`.
- Tokens should read as the dominant visual object.
- Fire-links should read as straight, faint laser cues rather than raised arcs.
- `V` cycles fire-link mode between `minimal` and `full`.
- This note is only a quick human-check list for Round V1.

## Suggested Human Checks

1. Launch the viewer with default arguments.
2. Confirm the token body now reads as the main object, not the fire-link.
3. Watch several active combat moments and confirm the fire-link no longer looks like a parabola.
4. Press `V` to switch from `minimal` to `full`.
5. Confirm `minimal` is the better default for routine observation and `full` is only slightly stronger.

## Expected Round V1 Result

- blue and red tokens should look deeper and less washed out under transparency
- fire-links should feel subordinate
- the link should read more like a laser cue than an arcing 2D line transplanted into 3D
