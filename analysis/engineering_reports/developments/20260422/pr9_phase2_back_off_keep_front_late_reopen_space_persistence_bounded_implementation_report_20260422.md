## PR9 Phase II - `back_off_keep_front` Late Reopen-Space Persistence Bounded Implementation Report

Date: 2026-04-22  
Scope: bounded experimental runtime slice plus validation report  
Status: implemented behind existing explicit experimental enablement

**Line classification:** Behavior line  
**Owner classification:** fleet-authorized / unit-realized  
**Honest claim boundary:** this report may claim a bounded later-phase reopen-space persistence adjustment under current locomotion semantics; it may not claim literal keep-front backward motion, turn-away retirement, full retreat doctrine, or a new locomotion capability

### 1. Battle read first

The previous `back_off_keep_front` slice fixed the most important opening
problem:

- first contact no longer read like deep immediate front-rank overrun
- front readability was much better
- `100v100` improved clearly

The remaining problem was narrower:

- `36v36` still had too much later sticky firing contact
- after the initial line collision was already controlled, too many front-rank
  Units kept welding into local contact instead of creating a clean enough
  reopen-space window

This slice improves that specific small-scale late-contact read.

At `36v36`, compared with the immediately prior `back_off_keep_front` branch:

- `190-220` mean contact falls from `15.71` to `8.68`
- `230-280` mean contact falls from `3.06` to `1.57`
- tick `205` contact falls from `17` to `13`
- tick `250` contact rises from the prior `3` to `6`, but remains low and the
  fleet gap is clearly open

The early no-crossing gain is preserved:

- `36v36` still has no negative `front_gap` in the captured run
- `61-90` min `front_gap` remains `0.982152`

The `100v100` read remains mostly positive in the required regression window:

- `190-220` mean contact is `19.97`, still much better than the temporary
  working anchor `48.23`
- this is also better than the prior `back_off_keep_front` branch's `25.68`

There is one residual risk:

- `100v100` `230-280` mean contact is `23.82`
- that is slightly above the temporary working anchor `20.06` and above the
  prior `back_off_keep_front` branch's `14.37`
- however, front readability remains better than the anchor:
  - `230-280` mean `front_gap` is `7.50` vs anchor `5.73`
  - min `front_gap` is positive at `2.11` vs anchor `-0.69`

Plain-language read:

- yes, `36v36` late sticky firing contact goes down
- yes, a clearer later reopen-space window is created
- yes, early no-crossing gains are preserved
- `100v100` keeps the important `190-220` improvement, but carries a later
  `230-280` contact-load residual that should remain visible to Governance

### 2. One-sentence conclusion

The slice succeeds at the intended narrow job for `36v36`: late sticky contact
is reduced without giving back early no-crossing, but the implementation should
still be read as experimental because `100v100` has a later-window contact-load
residual.

### 3. Static owner/path audit

Changed active owner/path:

- [runtime/engine_skeleton.py](/E:/logh_sandbox/runtime/engine_skeleton.py)
  - `EngineTickSkeleton._compute_unit_desire_by_unit(...)`
  - existing experimental branch behind:
    - `runtime.physical.local_desire.experimental_signal_read_realignment_enabled`

Unchanged owner/path:

- `battle_relation_gap_raw` remains early guard only
- same-tick target source remains:
  - `selected_target_by_unit`
- Unit desire carrier remains:
  - `desired_heading_xy`
  - `desired_speed_scale`
- `resolve_combat(...)` ownership remains unchanged
- no second target owner
- no guide-target semantics
- no mode
- no retreat implementation
- no locomotion rewrite
- no module split
- owner-language / settings-surface cleanup line was not reopened

### 4. What changed in runtime behavior

The slice adds a bounded late reopen-space persistence read inside the existing
experimental branch.

Human-readable meaning:

- if the global line is no longer in worst compression
- but it is only barely reopened
- and a Unit is still in selected-target local firing contact
- then the Unit keeps some reopen-space discipline alive a little longer

The final implementation does **not** simply keep braking every Unit in contact.

That direct speed-only attempt was rejected during validation because it made
small-scale contact more sticky.

The final shape is:

1. keep early guard unchanged

- `battle_relation_gap_raw` still controls early no-crossing / early release
- it does not become the late restore owner

2. derive late persistence only from `battle_relation_gap_current`

- only a small positive gap band participates
- fully active around `0.08`
- cleared by `0.26`
- negative / truly compressed gap still belongs to the existing violation path

3. localize by selected-target contact geometry

- selected target remains the only target source
- a contact gate covers the selected-target firing band
- this does not create a guide target or second target owner

4. suppress late local heading over-commit

- the heading side does not get new freedom
- instead, late persistence suppresses local target-chasing when the line is
  only barely reopened

5. keep speed-side brake-only and light

- speed response remains brake-only
- it is not sprint / lunge / boost
- it is intentionally lighter than the earlier direct speed-only attempt

### 5. Variable-role discipline

#### 5.1 `battle_relation_gap_raw`

Job:

- early guard only

Still not used as:

- later restore owner
- retreat owner
- generic severity signal

#### 5.2 `battle_relation_gap_current`

Job:

- later compressed-line truth
- late positive-gap persistence band

Why this does not reopen the old role confusion:

- it does not decide early release
- it does not decide target identity
- it does not authorize retreat
- it only keeps a mild post-compression discipline alive while the line is
  barely reopened

#### 5.3 `battle_brake_drive_current`

Job:

- later severity / urgency when the relation is truly compressed

Still not used as:

- early guard
- retreat owner

#### 5.4 `battle_hold_weight_current`

Job:

- coherence cap in the existing back-off line

Still not used as:

- raw reopen-space drive
- retreat owner

#### 5.5 Selected-target local geometry

Job:

- auxiliary localizer only

Still not used as:

- second target owner
- strategic release owner
- fleet-side authorization

### 6. Compile check

Command:

```text
python -m py_compile runtime/engine_skeleton.py test_run/settings_accessor.py test_run/test_run_scenario.py test_run/test_run_execution.py test_run/test_run_entry.py
```

Result:

- pass

### 7. Narrow smoke

Smoke posture:

- maintained active scenario
- `battle_36v36`
- explicit experimental enablement:
  - `runtime.physical.local_desire.experimental_signal_read_realignment_enabled = true`
- `steps = 120`
- `capture_positions = false`
- `include_target_lines = false`
- `print_tick_summary = false`
- `plot_diagnostics_enabled = false`
- `post_elimination_extra_ticks = 0`

Result:

- `final_tick = 120`
- `first_contact_tick = 61`
- `first_damage_tick = 61`
- `in_contact_final = 12`
- `damage_events_final = 12`

Read:

- opening timing is unchanged
- the slice is affecting continuation behavior, not first-contact scheduling

### 8. Paired comparison against temporary working anchor

Anchor set:

- `analysis/reference_notes/eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_battle_36v36_baseline_20260420.json`
- `analysis/reference_notes/eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_battle_100v100_baseline_20260420.json`

Validation posture:

- explicit experimental enablement
- `capture_positions = true`
- `capture_hit_points = true`
- `include_target_lines = true`
- `steps = 500`

### 9. `battle_36v36` targeted review

Final state:

| case | A alive / hp | B alive / hp |
| --- | --- | --- |
| temporary working anchor | `28 / 2106.809046` | `27 / 2200.015838` |
| current experimental branch | `27 / 2005.035588` | `26 / 1953.795976` |

Opening:

- `first_contact_tick = 61`
- `first_damage_tick = 61`
- first negative `front_gap`:
  - anchor: `74`
  - current: none
- first negative `relation_gap`:
  - anchor: `73`
  - current: `75`

Window review:

| window | anchor mean contact | current mean contact | anchor mean front gap | current mean front gap | current min front gap |
| --- | --- | --- | --- | --- | --- |
| `61-90` | `36.10` | `38.57` | `3.806987` | `5.401274` | `0.982152` |
| `120-160` | `22.37` | `22.54` | `7.850096` | `8.919896` | `7.450495` |
| `190-220` | `1.74` | `8.68` | `10.702773` | `10.086128` | `8.077011` |
| `230-280` | `2.39` | `1.57` | `10.878128` | `11.511469` | `8.809829` |

Important sample ticks:

- `tick 70`
  - `in_contact = 68`
  - `front_gap = 6.017343`
  - `relation_gap = 0.177981`
  - `early_embargo_permission = 0.0`
- `tick 205`
  - `in_contact = 13`
  - `front_gap = 10.476127`
  - `relation_gap = 0.231017`
  - `early_embargo_permission = 1.0`
- `tick 250`
  - `in_contact = 6`
  - `front_gap = 11.725425`
  - `relation_gap = 0.391223`
  - `early_embargo_permission = 1.0`

Read:

- early no-crossing is preserved
- the later `230-280` reopen-space window is now cleaner than both the anchor
  and the prior back-off branch
- `190-220` remains more contact-heavy than the temporary anchor, but it is
  materially improved from the prior back-off branch

### 10. `battle_100v100` regression check

Final state:

| case | A alive / hp | B alive / hp |
| --- | --- | --- |
| temporary working anchor | `68 / 5344.369009` | `65 / 5181.952767` |
| current experimental branch | `69 / 5812.168146` | `67 / 5531.189497` |

Opening:

- `first_contact_tick = 58`
- `first_damage_tick = 58`
- first negative `front_gap`:
  - anchor: `74`
  - current: `83`
- first negative `relation_gap`:
  - anchor: `74`
  - current: `77`

Window review:

| window | anchor mean contact | current mean contact | anchor mean front gap | current mean front gap | current min front gap |
| --- | --- | --- | --- | --- | --- |
| `61-90` | `82.77` | `78.50` | `2.499705` | `4.095155` | `-0.156376` |
| `120-160` | `34.05` | `34.37` | `2.257424` | `7.523996` | `0.042067` |
| `190-220` | `48.23` | `19.97` | `-0.092796` | `3.989127` | `-0.634323` |
| `230-280` | `20.06` | `23.82` | `5.730726` | `7.502270` | `2.111053` |

Important sample ticks:

- `tick 70`
  - `in_contact = 134`
  - `front_gap = 5.900640`
  - `relation_gap = 0.130147`
- `tick 205`
  - `in_contact = 21`
  - `front_gap = 4.426194`
  - `relation_gap = 0.119933`
- `tick 250`
  - `in_contact = 20`
  - `front_gap = 4.493625`
  - `relation_gap = 0.115164`

Read:

- the required `190-220` regression check passes strongly
- large-scale early line discipline is preserved
- `230-280` has more contact than the anchor, but front readability is still
  better than the anchor and overlap is not returning

### 11. Targeted human-readable evidence

Opening contact:

- the opening still reads disciplined
- `36v36` does not return to negative `front_gap`
- `100v100` delays negative `front_gap` from tick `74` to tick `83`

Later sticky-contact phase:

- `36v36` no longer stays as welded in the late window:
  - prior back-off branch `190-220`: `15.71`
  - current branch `190-220`: `8.68`
  - prior back-off branch `230-280`: `3.06`
  - current branch `230-280`: `1.57`

Reopen-space window:

- `36v36` `230-280` now reads as a clearer reopen-space window:
  - mean `front_gap = 11.511469`
  - min `front_gap = 8.809829`
  - mean contact `1.57`

Residual rotating / fragmented recovery:

- still present under current locomotion semantics
- not hidden by this report
- this slice does not add literal keep-front backward motion, so imperfect
  rotational / fragmented recovery remains an honest residual

### 12. Drift explanation

The useful drift is intentional:

- late local target-chasing is suppressed a little longer when the line is only
  barely reopened
- speed response remains light and brake-only
- the behavior does not turn into retreat

The risky drift is also real:

- direct speed-only persistence made contact worse during internal validation
- the final implementation therefore uses heading-overcommit suppression as the
  main late persistence support, with only light speed-side restraint
- `100v100` still has a later `230-280` contact-load residual even though its
  front gap remains better than the anchor

### 13. Shortest conclusion

This slice achieves the narrow `36v36` late reopen-space objective without
giving back early no-crossing.

It should still remain experimental because:

- it improves the required `36v36` late-contact read
- it preserves the important `100v100` `190-220` gain
- but it leaves a visible `100v100` `230-280` residual that Governance should
  review before any maintained promotion.
