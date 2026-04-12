# Step3 3D PR6 - Display Language Surface Restore and Cleanup Mistake Record - 2026-04-09

Scope: protocol/truth-surface correction + active settings restoration

## What went wrong

During old-family cleanup, the `visualization.display_language` key was removed from the active layered settings surface.

That deletion was incorrect.

The mistaken assumption was:

- `display_language` belonged only to the retired 2D visualization / BRF path

Current active-code truth showed otherwise:

- the maintained 3D replay path in `viz3d_panda/replay_source.py` still reads
  `visualization.display_language`
- the current active use is narrow but real:
  - fleet / commander name language selection (`EN | ZH`)

So this was not dead 2D residue.
It was an active 3D-facing visualization setting that should have been preserved.

## Active owner

- `viz3d_panda/replay_source.py`
  - `_resolve_display_language(settings)`
  - `_resolve_full_name(...)`

The active code path reads the layered setting through:

- `settings_api.get_visualization_setting(settings, "display_language", "EN")`

## Fix applied

Restored the active truth surface only:

- `test_run/test_run_v1_0.settings.json`
- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`

Restored value:

- `visualization.display_language = "ZH"`

No retired 2D visualization code was brought back.
No old BRF path was restored.
No active mechanism behavior changed.

## Lesson

This is a concrete cleanup mistake pattern:

- removing a surface because its original major owner was retired
- without first checking whether a smaller maintained owner still consumes it

For future cleanup rounds:

1. identify the current active owner, not just the historical owner
2. if a setting still has a narrow maintained reader, keep or reroot it before deletion
3. shrinking a surface is correct only after the last active reader is gone
