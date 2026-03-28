# Step 3 3D Legality First Bounded Implementation Report (2026-03-28)

Engine Version: `dev_v2.0`
Modified Layer: Step 3 legality line first bounded implementation attempt on the runtime/harness path
Affected Parameters: none
New Variables Introduced: legality debug/surface tracing only (`legality_surface` host in runtime debug state plus bounded legality summary fields in runtime debug payload / fixture metrics)
Cross-Dimension Coupling: exposes one explicit legality intake / middle stage / handoff seam using the existing mapping-produced reference-position surface and the existing post-movement correction region without redesigning mapping, downstream consumers, or viewer ownership
Mapping Impact: reuses the current mapping-produced `expected_positions`-style reference surface; no mapping-production redesign
Governance Impact: first real bounded legality exposure now exists as code, but only as a seam-first baseline and not as final legality architecture or algorithm finalization
Backward Compatible: yes

Summary
- This turn implements one bounded first-cut legality exposure.
- The implementation reuses the existing mapping-produced `expected_positions`-style reference surface as the bounded predecessor of `reference_positions_by_unit`.
- The explicit legality-owned middle stage is exposed locally around the already-existing post-movement correction region in `runtime/engine_skeleton.py`.
- The implementation emits one explicit feasible-position surface as the bounded predecessor of `feasible_positions_by_unit`.
- Harness-side traceability is added through existing runtime debug payload extraction and fixture metrics reuse.
- No mapping redesign, downstream consumer redesign, viewer ownership change, or algorithm rewrite is introduced.

## Files Changed

- `runtime/engine_skeleton.py`
- `test_run/test_run_execution.py`
- `test_run/test_run_telemetry.py`
- `repo_context.md`
- `system_map.md`

## Implementation Seam Chosen

The chosen seam is intentionally narrow:

1. reuse the existing fixture mapping-produced `expected_positions` surface in `runtime/engine_skeleton.py`
2. treat that surface as the legality intake-side bounded predecessor of `reference_positions_by_unit`
3. expose one explicit legality-owned middle stage around the existing:
   - tentative position build
   - post-movement separation/projection correction
   - hard-boundary clamp
4. emit one identity-preserving feasible-position surface on the post-legality side

The seam is local and seam-first.

It does not claim that the current correction code is already the final legality design.

It only makes that region explicitly usable as the first bounded legality baseline.

## Validation Path Used

Validation used the current bounded neutral-transit fixture/harness path through:

- `test_run/test_run_scenario.py`
  - `prepare_neutral_transit_fixture(...)`
- `test_run/test_run_entry.py`
  - `run_active_surface(...)`
- `test_run/test_run_execution.py`
  - existing fixture metrics capture and runtime debug payload consumption

Validation command shape:

```powershell
@'
from pathlib import Path
from test_run import settings_accessor as settings_api
from test_run import test_run_entry as entry
from test_run import test_run_scenario as scenario

base = Path("test_run").resolve()
settings = settings_api.load_layered_test_run_settings(base)
prepared = scenario.prepare_neutral_transit_fixture(base, settings_override=settings)
result = entry.run_active_surface(
    base_dir=base,
    prepared_override=prepared,
    settings_override=settings,
    execution_overrides={
        "capture_positions": True,
        "frame_stride": 999999,
        "include_target_lines": False,
        "print_tick_summary": False,
        "plot_diagnostics_enabled": True,
        "post_elimination_extra_ticks": 0,
    },
    summary_override={
        "animate": False,
        "export_battle_report": False,
    },
    emit_summary=False,
)
fixture = result["observer_telemetry"]["fixture"]
summary = {
    "ticks": int(result["final_state"].tick),
    "legality_reference_surface_count_peak": max(fixture["legality_reference_surface_count"]),
    "legality_feasible_surface_count_peak": max(fixture["legality_feasible_surface_count"]),
    "legality_middle_stage_any": any(fixture["legality_middle_stage_active"]),
    "legality_handoff_any": any(fixture["legality_handoff_ready"]),
    "expected_position_rms_error_last": fixture["expected_position_rms_error"][-1],
    "projection_pairs_peak": max(fixture["projection_pairs_count"]),
}
print(summary)
'@ | python -
```

Key observed bounded outputs from the run:

- `ticks = 425`
- `legality_reference_surface_count_peak = 100`
- `legality_feasible_surface_count_peak = 100`
- `legality_middle_stage_any = True`
- `legality_handoff_any = True`
- `expected_position_rms_error_last = 1.0999073359004958`
- `projection_pairs_peak = 80`

## What Worked

- the legality intake surface is now explicit in runtime code instead of remaining implicit only inside existing movement math
- the legality-owned middle stage is now traceable as a named bounded runtime concept
- the legality handoff side is now explicit as an identity-preserving feasible-position surface
- harness/runtime debug payload now exposes legality counts/flags without inventing a new telemetry channel
- existing expected-position RMS error and projection activity metrics still run on the bounded fixture path
- the first cut stayed local to the agreed files and did not trigger broader refactor

## What Remains Unresolved

- exact hook location is still not frozen beyond this first bounded seam
- exact runtime/storage type for the legality surfaces is still not frozen
- exact downstream consumer integration shape is still open
- exact execution order inside the legality-owned middle stage is still open
- projection / collision / boundary procedures remain the existing ones; this turn does not claim they are the final legality algorithms
- the first cut is still bounded to the current fixture-aligned path; it is not yet a generalized legality integration

## Merge-Worthy Assessment

Current engineering read:

- merge-worthy as a bounded baseline

Reason:

- this cut makes legality explicit and traceable in code
- it does so without widening scope into algorithm redesign or architecture rewrite
- it preserves existing bounded validation signals
- it remains honest about unresolved items and does not pretend to be final legality architecture

The correct review reading is:

- first bounded implementation attempt only
- not final legality architecture
- not algorithm-finalization
- not full runtime integration redesign
