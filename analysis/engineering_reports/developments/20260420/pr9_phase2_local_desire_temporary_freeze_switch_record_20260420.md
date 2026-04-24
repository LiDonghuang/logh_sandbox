## PR9 Phase II - Local Desire Temporary Freeze Switch Record

Date: 2026-04-20  
Scope: explicit temporary freeze switch only  
Status: implemented

### 1. Where the switch lives

Active public setting path:

- `runtime.physical.local_desire.experimental_signal_read_realignment_enabled`

Files changed for this switch:

- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1662>)
- [test_run/settings_accessor.py](<E:/logh_sandbox/test_run/settings_accessor.py:16>)
- [test_run/test_run_scenario.py](<E:/logh_sandbox/test_run/test_run_scenario.py:835>)
- [test_run/test_run_execution.py](<E:/logh_sandbox/test_run/test_run_execution.py:656>)
- [test_run/test_run_v1_0.runtime.settings.json](<E:/logh_sandbox/test_run/test_run_v1_0.runtime.settings.json:64>)
- [test_run/test_run_v1_0.settings.comments.json](<E:/logh_sandbox/test_run/test_run_v1_0.settings.comments.json:93>)
- [README.md](<E:/logh_sandbox/README.md:91>)

### 2. What exact active behavior it suppresses / restores

When the switch is `false`:

- the current experimental heading-side signal-read realignment is suppressed
- heading-side local desire returns to the temporary working-anchor pre-realignment read:
  - `heading_bias_cap * near_contact_gate * front_bearing_need * heading_turn_need`
- speed-side remains the same brake-only path already present on the temporary working anchor

When the switch is `true`:

- the current frozen experimental heading-side signal-read realignment is allowed to run
- heading-side local desire uses the current experimental read:
  - `heading_bias_cap * near_contact_gate * front_bearing_need`

What this does **not** change:

- `local_desire` layer/carrier stays in place
- same-tick target source stays single: `selected_target_by_unit`
- target-selection ownership does not change
- `resolve_combat(...)` ownership does not change
- no mode / retreat / persistent memory / second target owner is introduced

### 3. Maintained default after this change

Maintained active default is now:

- `runtime.physical.local_desire.experimental_signal_read_realignment_enabled = false`

Meaning:

- the maintained working path is frozen back to the accepted temporary working anchor
- the current experimental realignment remains available only behind an explicit visible switch

### 4. Confirmation that the switch is explicit, visible, and not a silent fallback

This switch is:

- explicit:
  - public runtime setting path exists
- visible:
  - documented in maintained settings comments and README
- fail-fast:
  - scenario builder requires the key
  - runtime validates that the value is boolean

This switch is **not**:

- a hidden local branch
- a private debug-only workaround
- a silent fallback
- an undocumented behavior fork

### 5. Minimal validation

Compile check:

- `python -m py_compile runtime/engine_skeleton.py test_run/settings_accessor.py test_run/test_run_scenario.py test_run/test_run_execution.py`

Result:

- passed

Maintained default (`false`) behavior check:

- paired comparison against refreshed temporary working-anchor baselines
- `battle_36v36`, `battle_100v100`, `neutral_36`, `neutral_100`
- all four matched on the checked behavior-bearing summaries

Smoke confirmation:

- switch `false`
  - `final_tick = 120`
  - `engaged_count_final = 14`
  - `first_contact_tick = 61`
  - `first_damage_tick = 61`
- switch `true`
  - `final_tick = 120`
  - `engaged_count_final = 6`
  - `first_contact_tick = 61`
  - `first_damage_tick = 61`

Engineering read:

- the switch is live
- the maintained default is restored to the temporary working anchor
- the frozen experimental local-desire realignment effect is still explicitly reproducible when intentionally enabled
