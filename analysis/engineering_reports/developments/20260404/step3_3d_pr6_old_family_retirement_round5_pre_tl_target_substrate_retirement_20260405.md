# step3_3d_pr6 old-family retirement round5 - pre_tl_target_substrate retirement - 2026-04-05

## Scope

- Scope type: harness-only / test-only old-family retirement
- Requested line of work: continue subtraction-first cleanup after round4
- Files changed:
  - `test_run/settings_accessor.py`
  - `test_run/test_run_scenario.py`
  - `test_run/test_run_execution.py`
  - `test_run/test_run_entry.py`
  - `test_run/test_run_anchor_regression.py`
  - `test_run/test_run_v1_0.testonly.settings.json`
  - `test_run/test_run_v1_0.settings.comments.json`

## Why this group was chosen

Human clarified that:

- only mechanisms actually used by the current launcher with current layered settings should be kept as active surface
- old 2D / pre-Panda3D family residue should be retired gradually
- when an old mechanism/parameter is deleted, the layered settings containers and comments surface must be updated in the same turn

`pre_tl_target_substrate` was the next bounded candidate because:

- the current active launcher/settings path resolves to `movement_model_effective = v4a`
- the current `v4a` battle target path already bypasses this local substrate branch by supplying battle restore bundles and reading battle target as global enemy relation + `d*`
- the parameter still remained exposed in `testonly.settings.json`, settings access, harness debug surface, and anchor-regression setup

## Ownership truth before this round

- Active movement owner for current launcher/settings: `v4a`
- Active cohesion decision source for current launcher/settings: `v3_test`
- `pre_tl_target_substrate` was not active on the current `v4a` launcher path
- it remained only as an older `v3a` local-target substrate selector

## What changed

- retired the public/test-only `pre_tl_target_substrate` parameter surface
- removed its layered settings path from `settings_accessor.py`
- removed its read from `_build_movement_cfg`
- removed its launcher/render debug export from `test_run_entry.py`
- removed its stale assignment from `test_run_anchor_regression.py`
- removed the key from `test_run_v1_0.testonly.settings.json`
- removed the field comment from `test_run_v1_0.settings.comments.json`

## Execution behavior after this round

- current active `v4a` battle path is unchanged; it was already not using this parameter
- older non-bundle fallback targeting in `test_run_execution.py` now uses one fixed retained local-reference behavior:
  - nearest-5 enemy centroid

This round therefore removes the configurable substrate family without claiming that all old target evaluation logic is gone.

## What was intentionally not changed

- no frozen-layer edits
- no `runtime/engine_skeleton.py` edits
- no `test_run_v1_0_viz.py` edits
- no `odw_posture_bias` retirement in this round
- no `settings.reference.md` change, because that file did not currently expose this field surface

## Validation

### Static residue check

Command:

```powershell
rg -n "pre_tl_target_substrate|PRE_TL_TARGET_SUBSTRATE|ROUTINE_PRE_TL_TARGET_SUBSTRATE" test_run -S
```

Result:

- no matches under `test_run/`

### Syntax compile check

`python -m py_compile` hit a local `__pycache__` access error on this machine, so a no-write compile check was used instead.

Command:

```powershell
@'
from pathlib import Path
files = [
    Path(r'e:\logh_sandbox\test_run\settings_accessor.py'),
    Path(r'e:\logh_sandbox\test_run\test_run_scenario.py'),
    Path(r'e:\logh_sandbox\test_run\test_run_execution.py'),
    Path(r'e:\logh_sandbox\test_run\test_run_entry.py'),
    Path(r'e:\logh_sandbox\test_run\test_run_anchor_regression.py'),
]
for path in files:
    source = path.read_text(encoding='utf-8-sig')
    compile(source, str(path), 'exec')
    print('compiled', path.name)
'@ | python -
```

Observed output:

- `compiled settings_accessor.py`
- `compiled test_run_scenario.py`
- `compiled test_run_execution.py`
- `compiled test_run_entry.py`
- `compiled test_run_anchor_regression.py`

### JSON validation

Command:

```powershell
@'
import json
from pathlib import Path
for name in [
    r'e:\logh_sandbox\test_run\test_run_v1_0.testonly.settings.json',
    r'e:\logh_sandbox\test_run\test_run_v1_0.settings.comments.json',
]:
    data = json.loads(Path(name).read_text(encoding='utf-8-sig'))
    print('json_ok', Path(name).name, isinstance(data, dict))
'@ | python -
```

Observed output:

- `json_ok test_run_v1_0.testonly.settings.json True`
- `json_ok test_run_v1_0.settings.comments.json True`

### Current active launcher truth check

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
print('has_pre_tl_key=', 'pre_tl_target_substrate' in movement_cfg)
'@ | python -
```

Observed output:

- `movement_model_effective= v4a`
- `has_pre_tl_key= False`

### Default active smoke

Command:

```powershell
@'
from pathlib import Path
from test_run import test_run_entry
base = Path(r'e:\logh_sandbox')
result = test_run_entry.run_active_surface(
    base_dir=base / 'test_run',
    execution_overrides={'steps': 3},
    emit_summary=False,
)
print('tick=', result['final_state'].tick)
print('movement=', result['prepared']['summary']['movement_model_effective'])
print('cohesion=', result['prepared']['summary']['runtime_decision_source_effective'])
print('has_pre_tl_debug=', any('pre_tl_target_substrate' in str(k) for k in result.get('render_debug_context', {}).keys()))
'@ | python -
```

Observed output:

- `tick= 3`
- `movement= v4a`
- `cohesion= v3_test`
- `has_pre_tl_debug= False`

### Forced v3a fallback smoke

Command:

```powershell
@'
from pathlib import Path
from test_run import test_run_entry
base = Path(r'e:\logh_sandbox')
override = {
    'runtime': {
        'selectors': {'movement_model': 'v3a'},
    }
}
result = test_run_entry.run_active_surface(
    base_dir=base / 'test_run',
    settings_override=override,
    execution_overrides={'steps': 2},
    emit_summary=False,
)
print('tick=', result['final_state'].tick)
print('movement=', result['prepared']['summary']['movement_model_effective'])
print('cohesion=', result['prepared']['summary']['runtime_decision_source_effective'])
print('has_pre_tl_debug=', any('pre_tl_target_substrate' in str(k) for k in result.get('render_debug_context', {}).keys()))
'@ | python -
```

Observed output:

- `tick= 2`
- `movement= v3a`
- `cohesion= v3_test`
- `has_pre_tl_debug= False`

## Honest classification

- Result type: `Partial Cleanup`
- visible subtraction happened in the public/test-only config surface, harness read path, debug surface, and old branch logic
- this does **not** retire all old target-evaluation residue
- remaining nearby old-family candidates still include `odw_posture_bias` and broader `v3a` support surfaces

