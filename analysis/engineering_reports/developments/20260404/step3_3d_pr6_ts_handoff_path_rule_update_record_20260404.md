# TS Handoff Path Rule Update Record - 2026-04-04

Status: protocol / policy only  
Scope: TS migration artifact default path correction

## Intent

This record captures a small but important policy correction:

- TS handoff packages should live under:
  - `docs/archive/ts_handoff_archive/`

not under:

- `archive/ts_handoff_archive/`

## Change

The root `AGENTS.md` TS migration rule was updated so that the default persistence requirement now points to:

- `docs/archive/ts_handoff_archive/TS_HANDOFF_<YYYYMMDD_HHMMSS>/`

The just-created handoff package for this thread was also moved to the corrected location.

## Reason

The project already treats:

- `docs/archive/ts_handoff_archive/`

as the proper archive surface for retained TS handoff materials.

Keeping the AGENTS rule pointed at the older root-level path would continue to create inconsistent archive placement.

## Bottom Line

TS handoff packages should now be created under:

- `docs/archive/ts_handoff_archive/`

and older one-off handoffs created in the root-level archive path should be treated as path inconsistencies rather than the preferred future location.
