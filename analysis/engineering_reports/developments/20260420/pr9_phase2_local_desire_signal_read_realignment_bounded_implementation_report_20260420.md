## PR9 Phase II - Local Desire Signal Read Realignment Bounded Implementation Report

Date: 2026-04-20  
Scope: runtime local-desire signal-read realignment only  
Status: implemented locally on the refreshed temporary working anchor

### 1. Static owner/path audit

Changed owner/path:

- `runtime/engine_skeleton.py`
  - `EngineTickSkeleton._compute_unit_desire_by_unit(...)`

Exact local mechanism change:

- heading-side `local_heading_bias_weight` no longer depends on the shared
  facing-relative `heading_turn_need`
- heading-side bias is now driven by:
  - `near_contact_gate`
  - `front_bearing_need`
- speed-side remains driven by:
  - `heading_turn_need`
  - `speed_turn_need`
  - brake-only `desired_speed_scale`

What did **not** change:

- target-selection ownership
- `resolve_combat(...)` ownership
- `local_desire` carrier shape
- single same-tick target source
- mode / retreat / persistent memory
- broad locomotion-family ownership
- module split
- combat-coupling path

### 2. Files changed

- `runtime/engine_skeleton.py`
- `analysis/engineering_reports/developments/20260420/pr9_phase2_local_desire_signal_read_realignment_bounded_implementation_report_20260420.md`

### 3. Compile check

- `python -m py_compile runtime/engine_skeleton.py`

Result:

- pass

### 4. Narrow smoke

Maintained active path:

- `steps=120`

Result:

- `final_tick = 120`
- `first_contact_tick = 61`
- `first_damage_tick = 61`
- `engaged_count_final = 6`

Temporary working-anchor comparison:

- previous refreshed temporary anchor at the same smoke horizon had
  `engaged_count_final = 14`

### 5. Paired comparison against refreshed temporary working-anchor baselines

Anchor set:

- `analysis/reference_notes/eng_dev_v2.1_formation_only_a4b5ce2b7dba_dirty_temp_working_anchor_*.json`

#### `battle_36v36`

Baseline temporary anchor:

- `final_tick = 500`
- `first_contact_tick = 61`
- `first_damage_tick = 61`
- final fleet state:
  - `A alive=28 hp=2106.809046`
  - `B alive=27 hp=2200.015838`

Current after signal-read realignment:

- `final_tick = 500`
- `first_contact_tick = 61`
- `first_damage_tick = 61`
- final fleet state:
  - `A alive=21 hp=1228.687966`
  - `B alive=20 hp=1083.277576`

Read:

- battle surface drift is real and substantial
- opening timing is unchanged
- later battle remains much more contact-active and lethal than the temporary
  working anchor

#### `battle_100v100`

Baseline temporary anchor:

- `final_tick = 500`
- `first_contact_tick = 58`
- `first_damage_tick = 58`
- final fleet state:
  - `A alive=68 hp=5344.369009`
  - `B alive=65 hp=5181.952767`

Current after signal-read realignment:

- `final_tick = 500`
- `first_contact_tick = 58`
- `first_damage_tick = 58`
- final fleet state:
  - `A alive=46 hp=3164.317999`
  - `B alive=46 hp=3325.763631`

Read:

- battle drift is again substantial
- opening timing is unchanged
- the realignment increases sustained battle contact / damage relative to the
  temporary working anchor

#### `neutral_36`

- exact match on:
  - `position_frames`
  - `combat_telemetry`
  - `observer_telemetry` excluding `tick_elapsed_ms`

#### `neutral_100`

- exact match on:
  - `position_frames`
  - `combat_telemetry`
  - `observer_telemetry` excluding `tick_elapsed_ms`

### 6. Targeted human-readable evidence

#### Synthetic signal-read probe

Controlled geometry:

- fleet front: `0 deg`
- unit facing: `30 deg`
- selected target bearing: `30 deg`
- distance: `10.0`

Interpretation:

- target is already well aligned to unit-facing read
- but it is still off-axis relative to fleet front

Old heading-side read expectation:

- `heading_turn_need = 0`
- heading bias remained silent

Current result:

- `desired_heading_xy = (0.999887, 0.015059)`
- heading offset from base heading: `0.862840 deg`
- `desired_speed_scale = 1.0`

Read:

- heading-side now activates on fleet-front-relative off-axis opportunity
- speed-side remains later / weaker / brake-only and does not brake in this
  probe because the unit-facing turn burden is already low

#### `battle_36v36` focus window

In the refreshed temporary working anchor, the `tick 190..205` window had many
ticks with zero or near-zero contact.

After signal-read realignment, that same window reopens contact:

- `tick 190`
  - anchor:
    - `in_contact_count = 0`
    - `A->B target links = 0`
    - `B->A target links = 0`
  - current:
    - `in_contact_count = 9`
    - `A->B target links = 5`
    - `B->A target links = 4`
- `tick 205`
  - anchor:
    - `in_contact_count = 1`
    - `A->B target links = 0`
    - `B->A target links = 1`
  - current:
    - `in_contact_count = 10`
    - `A->B target links = 5`
    - `B->A target links = 5`

Read:

- this slice does what it was intended to do
- heading-side local desire is no longer silent once fleet-front-relative
  off-axis opportunities appear
- that new heading response materially changes battle continuation relative to
  the temporary working anchor

### 7. Explicit explanation of battle-surface drift

Engineering explanation of the observed drift:

- the refreshed temporary working anchor still had a silent heading-side read in
  many same-tick off-axis target situations because the primary activation path
  remained constrained by the unit-facing fire-cone-compressed signal
- this slice removes that silence on the heading side by letting
  `fleet front -> selected target bearing` drive heading bias directly
- speed-side remains conservative and brake-only, so the main battle change is
  not from broader speed aggression
- therefore the drift is best read as:
  - more units reorient into same-tick off-axis firing opportunities
  - more contact is sustained in later battle windows
  - battle lethality rises relative to the temporary working anchor

### 8. Current conclusion

This bounded slice is implemented correctly relative to the accepted proposal
scope:

- one target source kept
- only the signal read changed
- heading-side and speed-side reads are now split

But it is **not** a no-drift cleanup.

Current engineering read:

- neutral behavior remains unchanged
- battle behavior changes materially
- further progress should wait for governance review of whether this battle
  drift is an acceptable move from the temporary working anchor
