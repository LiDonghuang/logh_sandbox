# dev_v2.0 Launch Semantics Alignment Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: additive 3D viewer bootstrap / launch semantics surface
Affected Parameters: viewer `--steps` handling only
New Variables Introduced: `max_steps_source` metadata label in replay bundle
Cross-Dimension Coupling: viewer launch now defers to existing 2D `run_control.max_time_steps` semantics when no override is passed
Mapping Impact: none
Governance Impact: aligns viewer behavior with existing 2D stop semantics without redefining simulation stop rules
Backward Compatible: yes; explicit `--steps` override remains available

Summary
- Viewer no longer defaults to `240` and silently truncates human tests.
- If `--steps` is omitted, the viewer now respects layered settings as-is.
- If `--steps` is provided, it overrides with the same tick semantics as the underlying 2D path.
- Non-positive step values continue to preserve existing run-until-resolution / arrival-plus-buffer behavior.
- Simulation still decides where replay generation stops; viewer only consumes the generated frames.

## Previous Problem

The bootstrap path used `DEFAULT_VIEWER_MAX_STEPS = 240` as an implicit cap. That changed human launch behavior even when the user did not explicitly ask for a truncated run.

For the current repo state, that was a usability defect because it made the viewer silently stop earlier than the maintained 2D path would stop.

## Alignment Rule Implemented

Current behavior is now:

- no `--steps`:
  - use layered settings `run_control.max_time_steps` directly
- explicit `--steps`:
  - override that value with the same tick-count meaning

This means the viewer does not invent a separate stop rule. It only passes the same stop contract through to the existing active-surface run.

This pass follows an inheritance-first, duplication-last rule: simulation ownership stays in layered `test_run` settings, while `viz3d_panda/` keeps only viewer-local display and usability controls.

## Non-Positive Values

This turn preserves existing 2D semantics for non-positive step values.

If the resolved `max_time_steps` is `<= 0`, the active-surface path still runs under the pre-existing stop logic:

- run until battle resolution or fixture arrival condition
- then apply the already established post-stop / post-elimination buffer behavior

The viewer bootstrap does not redefine any of those conditions.

## Human-Visible Feedback

The viewer status overlay now shows:

- `sim_limit=settings:<value>`
- or `sim_limit=override:<value>`

That keeps the launch semantics visible during human testing without changing the underlying simulation behavior.
