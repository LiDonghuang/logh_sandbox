## PR9 Phase II - `back_off_keep_front` Behavior-Line Bounded Implementation Report

Date: 2026-04-22  
Scope: bounded experimental runtime slice plus validation report  
Status: implemented behind existing explicit experimental enablement

**Line classification:** Behavior line  
**Owner classification:** fleet-authorized / unit-realized  
**Honest claim boundary:** this report may claim bounded give-ground / reopen-space / restore-line behavior under current locomotion semantics; it may not claim literal keep-front backward motion, turn-away retirement, or full retreat doctrine

### 1. Battle read first

This slice did not make Units "freer."

What it actually changed is narrower and more useful than that:

- front-rank Units are now less willing to keep turning local firing
  opportunity into continued early forward over-commit
- the first-contact line stays much more readable
- the worst early overlap is materially reduced

But the result is not a pure win across every battle window.

At `36v36`, the slice now reads less like early overrun and less like immediate
dog-fight breakup, but it also reads more like a broad, sustained firing line
that does not reopen enough space later.

Plain-language read:

- better:
  - less early crossing
  - less deep first-contact overlap
  - cleaner fleet-front readability
- still not good enough:
  - later contact can stay too sticky
  - reopen-space behavior is only partial
  - this is still not a maintained final battle read

At `100v100`, the same slice reads more favorable:

- later crossing
- shallower early overlap
- lower later contact load
- stronger preserved front readability

So the current implementation found a real behavior seam, but it is not yet a
uniformly settled maintained outcome across scales.

### 2. One-sentence conclusion

The implemented slice successfully turned `back_off_keep_front` into a real
fleet-authorized / Unit-realized behavior-line response, but the current result
is mixed:

- early crossing is much better controlled
- larger-scale battle reads improve
- `36v36` still holds too much later firing contact instead of reopening enough
  space

### 3. Static owner/path audit

Changed active owner/path:

- [runtime/engine_skeleton.py](/E:/logh_sandbox/runtime/engine_skeleton.py)
  - `EngineTickSkeleton._compute_unit_desire_by_unit(...)`

Unchanged owner/path:

- same-tick target source stays:
  - `selected_target_by_unit`
- current Unit desire carrier stays:
  - `desired_heading_xy`
  - `desired_speed_scale`
- `resolve_combat(...)` ownership stays unchanged
- no second target owner
- no guide-target semantics
- no mode
- no retreat implementation
- no locomotion rewrite
- no module split

### 4. Exact runtime change made

The runtime edit stayed inside the existing experimental branch in
`_compute_unit_desire_by_unit(...)`.

What changed:

1. `battle_relation_gap_raw` now remains only the early guard

- it still controls whether early local opportunity is even permitted
- it no longer also acts as the later restore owner

2. `battle_relation_gap_current` now remains the later compressed-line truth

- it still feeds the derived `relation_violation_severity`
- that severity now participates only in later give-ground authorization /
  persistence, not early release

3. `battle_brake_drive_current` now stays the later bounded severity / urgency

- it now directly strengthens the give-ground severity read
- it does not become the early guard

4. `battle_hold_weight_current` now acts as a coherence cap

- it now suppresses local heading opportunism under compressed-line give-ground
  conditions
- it is no longer used as a hidden restore drive that tries to pull heading back
  toward `fleet_front_hat`

5. `near_contact_gate` and local geometry remain auxiliary localizers only

- they still localize which Units are in the problem neighborhood
- they no longer own the whole response family

6. Experimental restore-line via direct relax toward `fleet_front_hat` was
   removed from the live branch

- the previous branch was still trying to use a heading-side restore pull
- this slice removes that drive and instead keeps restore behavior implicit
  through:
  - suppression of local over-commit
  - stronger brake-only restraint
  - continued fleet-side movement envelope ownership

### 5. Compile check

Command:

```text
python -m py_compile runtime/engine_skeleton.py test_run/settings_accessor.py test_run/test_run_scenario.py test_run/test_run_execution.py test_run/test_run_entry.py
```

Result:

- pass

### 6. Narrow smoke

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

- the bounded experimental line is live
- the opening timing is unchanged
- the new logic changes battle continuation rather than opening tick order

### 7. Paired comparison against current temporary working anchor

Anchor set:

- `analysis/reference_notes/eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_battle_36v36_baseline_20260420.json`
- `analysis/reference_notes/eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_battle_100v100_baseline_20260420.json`
- `analysis/reference_notes/eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_neutral_36_baseline_20260420.json`
- `analysis/reference_notes/eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_neutral_100_baseline_20260420.json`

Validation posture:

- explicit experimental enablement through the existing test-only surface
- `capture_positions = true`
- `capture_hit_points = true`
- `include_target_lines = true`

#### `battle_36v36`

Final state:

| case | A alive / hp | B alive / hp |
| --- | --- | --- |
| temporary working anchor | `28 / 2106.809046` | `27 / 2200.015838` |
| current experimental branch | `24 / 1744.609635` | `25 / 1897.845588` |

Key battle-read summary:

- opening timing is unchanged:
  - `first_contact_tick = 61`
  - `first_damage_tick = 61`
- first negative `front_gap` no longer occurs within the captured run:
  - `74 -> none`
- first negative `relation_gap` is delayed:
  - `73 -> 75`
- early window overlap is much shallower:
  - `min front_gap 61-90: -3.929596 -> 0.982152`

Window review:

| window | anchor mean contact | current mean contact | anchor mean front gap | current mean front gap |
| --- | --- | --- | --- | --- |
| `61-90` | `36.10` | `38.57` | `3.806987` | `5.401274` |
| `120-160` | `22.37` | `23.24` | `7.850096` | `8.870215` |
| `190-220` | `1.74` | `15.71` | `10.702773` | `8.528743` |
| `230-280` | `2.39` | `3.06` | `10.878128` | `10.998838` |

Important sample ticks:

- `tick 70`
  - anchor:
    - `in_contact = 72`
    - `front_gap = 4.579634`
    - `relation_gap = 0.162748`
  - current:
    - `in_contact = 68`
    - `front_gap = 6.017343`
    - `relation_gap = 0.177981`
- `tick 140`
  - anchor:
    - `in_contact = 25`
    - `front_gap = 5.460188`
  - current:
    - `in_contact = 27`
    - `front_gap = 7.047539`
- `tick 205`
  - anchor:
    - `in_contact = 1`
    - `front_gap = 13.508874`
  - current:
    - `in_contact = 17`
    - `front_gap = 9.485366`
    - `relation_gap = 0.211566`

Read:

- this slice clearly reduces early crossing / overlap
- fleet-front readability is better preserved
- but later reopen-space remains too weak at `36v36`
- the battle now tends toward a broad sustained firing line rather than a clean
  reopen-space window

#### `battle_100v100`

Final state:

| case | A alive / hp | B alive / hp |
| --- | --- | --- |
| temporary working anchor | `68 / 5344.369009` | `65 / 5181.952767` |
| current experimental branch | `71 / 6014.728370` | `69 / 5887.525359` |

Key battle-read summary:

- opening timing is unchanged:
  - `first_contact_tick = 58`
  - `first_damage_tick = 58`
- first negative `front_gap` is delayed:
  - `74 -> 83`
- first negative `relation_gap` is delayed:
  - `74 -> 77`
- early overlap is much shallower:
  - `min front_gap 61-90: -1.894438 -> -0.156376`

Window review:

| window | anchor mean contact | current mean contact | anchor mean front gap | current mean front gap |
| --- | --- | --- | --- | --- |
| `61-90` | `82.77` | `78.50` | `2.499705` | `4.095155` |
| `120-160` | `34.05` | `30.66` | `2.257424` | `7.286148` |
| `190-220` | `48.23` | `25.68` | `-0.092796` | `2.053866` |
| `230-280` | `20.06` | `14.37` | `5.730726` | `8.397246` |

Important sample ticks:

- `tick 70`
  - anchor:
    - `in_contact = 152`
    - `front_gap = 3.710692`
  - current:
    - `in_contact = 134`
    - `front_gap = 5.900640`
- `tick 140`
  - anchor:
    - `in_contact = 33`
    - `front_gap = 2.244950`
  - current:
    - `in_contact = 7`
    - `front_gap = 11.249895`
- `tick 205`
  - anchor:
    - `in_contact = 67`
    - `front_gap = -2.239328`
  - current:
    - `in_contact = 5`
    - `front_gap = 3.101131`
    - `relation_gap = -0.094349`

Read:

- at larger scale this slice reads substantially better than the anchor
- the line stays readable longer
- overlap is shallower
- later contact load is much lower

#### `neutral_36`

Comparison summary:

| case | final_tick | alive | hp | objective_reached_tick | final centroid distance |
| --- | --- | --- | --- | --- | --- |
| temporary working anchor | `447` | `36` | `3600.0` | `427` | `1.537790` |
| current experimental branch | `447` | `36` | `3600.0` | `427` | `1.537790` |

Read:

- unchanged in practical behavior
- expected, because there is no battle target / combat compression path here

#### `neutral_100`

Comparison summary:

| case | final_tick | alive | hp | objective_reached_tick | final centroid distance |
| --- | --- | --- | --- | --- | --- |
| temporary working anchor | `448` | `100` | `10000.0` | `428` | `1.112345` |
| current experimental branch | `448` | `100` | `10000.0` | `428` | `1.112345` |

Read:

- unchanged in practical behavior
- expected for the same reason as `neutral_36`

### 8. Targeted human-readable evidence

The strongest positive evidence is this:

- `battle_36v36` no longer reaches negative `front_gap`
- `battle_100v100` delays first negative `front_gap` by `9` ticks and keeps
  later windows much more open

The strongest negative evidence is this:

- `battle_36v36` still shows too much later contact persistence
- at `tick 205`, the current branch still has:
  - `in_contact = 17`
  with
  - `front_gap = 9.485366`

Human-readable interpretation:

- this is no longer an early-overlap failure
- it is now a partial-reopen-space failure
- the current slice preserves the front better, but does not yet reopen enough
  space at small scale

### 9. Explicit drift explanation

The drift is real and it is intentional in one respect:

- the slice was designed to stop early local firing opportunity from breaking
  fleet hold too soon

That part worked.

The remaining problem is also real:

- under current locomotion semantics, stronger suppression of local over-commit
  plus stronger brake-only restraint does not automatically create a clean later
  reopen-space behavior
- at `36v36`, it can instead settle into a broader, more readable, but still
  too persistent firing line

So the current drift should be read as:

- not a return to overlap-driven dog-fight chaos
- but also not yet a clean maintained back-off / space-reopening outcome

### 10. Residual semantics still acknowledged

This slice still remains below literal locomotion capability change.

It does **not** change the fact that current runtime semantics still allow and
may still visibly show:

- rotating pullback
- fragmented return
- collapse-like recovery after already-deep overlap

This report does not over-claim beyond that boundary.

### 11. Shortest conclusion

This bounded `back_off_keep_front` slice succeeded at:

- reducing early crossing
- preserving fleet-front readability
- improving larger-scale battle behavior

But it still leaves one important unresolved battle-read problem:

- `36v36` does not reopen enough later space and keeps too much firing contact

So the slice found the right behavior seam, but should still be treated as an
experimental bounded result rather than a maintained final outcome.
