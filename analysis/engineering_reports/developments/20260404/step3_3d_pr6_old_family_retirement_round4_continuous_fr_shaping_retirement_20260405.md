# step3_3d_pr6 old-family retirement round4 - continuous_fr_shaping retirement - 2026-04-05

## Scope

- Scope type: harness-only / test-only old-family retirement
- Requested line of work: continue subtraction-first cleanup after `restore_strength` decoupling
- Files changed:
  - `test_run/settings_accessor.py`
  - `test_run/test_run_scenario.py`
  - `test_run/test_run_execution.py`
  - `test_run/test_run_entry.py`

## Why this group was chosen

Human clarified that the kept surface should be limited to mechanisms actually reached by the current launcher with the current layered settings, and that old 2D / pre-Panda3D family residue should be removed gradually.

`continuous_fr_shaping` was the next bounded candidate because:

- it was not present in the current `runtime.settings.json` or `testonly.settings.json` containers
- the current active launcher/settings path resolves to `movement_model_effective = v4a`
- the active `v4a` path did not use this shaping line
- the remaining carrier was harness-side read / injection / debug plumbing, so it could be removed without touching frozen layers

## Ownership truth before this round

- Active movement owner for current launcher/settings: `v4a`
- Active cohesion decision source for current launcher/settings: `v3_test`
- `continuous_fr_shaping` was not an active current-surface owner; it was an older `v3a`-only experimental harness mechanism
- `symmetric_movement_sync_enabled` was explicitly verified as still active and was **not** part of this retirement round

## What was removed

- deleted `continuous_fr_shaping_*` nested runtime setting path support from `settings_accessor.py`
- deleted `continuous_fr_shaping` construction / effective-state derivation from `_build_movement_cfg`
- deleted harness engine attribute injection for:
  - `CONTINUOUS_FR_SHAPING_ENABLED`
  - `CONTINUOUS_FR_SHAPING_MODE`
  - `CONTINUOUS_FR_SHAPING_A`
  - `CONTINUOUS_FR_SHAPING_SIGMA`
  - `CONTINUOUS_FR_SHAPING_P`
  - `CONTINUOUS_FR_SHAPING_Q`
  - `CONTINUOUS_FR_SHAPING_BETA`
  - `CONTINUOUS_FR_SHAPING_GAMMA`
- deleted the proxy-state implementation used only by this mechanism:
  - `_continuous_fr_midband_gate`
  - `_compute_continuous_fr_shaping`
  - `FormationRigidityFirstReadProxy`
  - `_build_continuous_fr_proxy_state`
  - `debug_last_continuous_fr_shaping`
- narrowed launcher render debug context so it no longer exports `continuous_fr_shaping_*` fields

## What was intentionally not changed

- no change to frozen runtime skeleton ownership or governance files
- no change to `symmetric_movement_sync_enabled`
- no change to `pre_tl_target_substrate` or `odw_posture_bias`
- no change to current layered settings containers because `continuous_fr_shaping` no longer had active values there
- no change to `settings.comments.json` or `settings.reference.md` because this mechanism no longer had a current documented field surface there

## Validation

### Static residue check

Command:

```powershell
rg -n "continuous_fr_shaping|CONTINUOUS_FR_SHAPING|debug_last_continuous_fr_shaping|FormationRigidityFirstReadProxy|_sigmoid\(" test_run -S
```

Result:

- no matches under `test_run/`

### Compile check

Command:

```powershell
python -m py_compile test_run\settings_accessor.py test_run\test_run_scenario.py test_run\test_run_execution.py test_run\test_run_entry.py
```

Result:

- pass

### Active launcher truth check

Command:

```powershell
@'
from pathlib import Path
from test_run import settings_accessor, test_run_scenario as scenario
base = Path(r'e:\logh_sandbox') / 'test_run'
settings = settings_accessor.load_layered_test_run_settings(base)
get_run = lambda key, default: settings_accessor.get_run_control_setting(settings, key, default)
get_runtime = lambda key, default: settings_accessor.get_runtime_setting(settings, key, default)
run_cfg = scenario._build_run_cfg(get_run, get_runtime)
movement_cfg = scenario._build_movement_cfg(
    get_runtime,
    runtime_decision_source_effective=run_cfg['runtime_decision_source_effective'],
    test_mode=run_cfg['test_mode'],
)
print('movement_model_effective=', movement_cfg['model_effective'])
print('has_continuous_block=', 'continuous_fr_shaping' in movement_cfg)
'@ | python -
```

Observed output:

- `movement_model_effective= v4a`
- `has_continuous_block= False`

### Short active run smoke

Command:

```powershell
@'
from pathlib import Path
from test_run import test_run_entry
base = Path(r'e:\logh_sandbox')
result = test_run_entry.run_active_surface(base_dir=base / 'test_run', execution_overrides={'steps': 3}, emit_summary=False)
print('tick=', result['final_state'].tick)
print('movement=', result['prepared']['summary']['movement_model_effective'])
print('cohesion=', result['prepared']['summary']['runtime_decision_source_effective'])
'@ | python -
```

Observed output:

- `tick= 3`
- `movement= v4a`
- `cohesion= v3_test`

## Honest classification

- Result type: `Partial Cleanup`
- Visible subtraction happened in the harness read path and hot path
- This does **not** mean the full `v3a` family is retired
- Remaining old-family candidates are still present, including `pre_tl_target_substrate`, `odw_posture_bias`, and the broader `v3a` support surfaces

