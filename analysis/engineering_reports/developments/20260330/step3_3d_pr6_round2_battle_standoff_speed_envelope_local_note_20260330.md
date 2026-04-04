# Step 3 3D PR #6 Round 2 Local Note
## Battle Standoff + Unit-Level Attack-Direction Speed Envelope

Status: local engineering note  
Scope: `test_run/` harness-only candidate work on PR `#6`  
Frozen runtime status: `runtime/engine_skeleton.py` untouched  
Remote status: local only / not yet pushed

## 1. Purpose

This local note records the first bounded Round 2 implementation step after the carrier was redefined away from reference-only logic.

This step adds two same-theme movement-realization seams on top of the existing PR `#6` transition carrier:

1. fleet-level battle standoff distance `d*`
2. unit-level attack-direction-aware speed envelope

The intent is not to solve battle behavior in one cut.

The intent is to stop reading battle target mainly as raw enemy-centroid pursuit, and to stop reading engaged unit movement freedom as directionally blind.

## 2. New Test-Only Surface

New `runtime.movement.v4a.test_only` keys:

- `battle_standoff_self_extent_weight`
- `battle_standoff_enemy_extent_weight`
- `battle_standoff_hold_band_ratio`
- `engaged_speed_scale`
- `attack_speed_lateral_scale`
- `attack_speed_backward_scale`

Current local default read:

- `battle_standoff_self_extent_weight = 0.15`
- `battle_standoff_enemy_extent_weight = 0.15`
- `battle_standoff_hold_band_ratio = 0.10`
- `engaged_speed_scale = 0.70`
- `attack_speed_lateral_scale = 0.65`
- `attack_speed_backward_scale = 0.35`

These remain harness/test-only and do not alter public baseline semantics.

## 3. Battle Standoff Read

The first bounded fleet-level desired engagement distance is now read as:

`d* = attack_range + self_w * own_forward_extent + enemy_w * enemy_forward_extent`

Current implementation details:

- `own_forward_extent` and `enemy_forward_extent` are measured from current alive positions
- projection is along the current fleet-to-reference axis
- battle target now reads:
  - approach while current distance is meaningfully greater than `d*`
  - hold while current distance is within the `d*` hold band
  - no active retreat branch in this first bounded read

Important local correction:

- an earlier local cut incorrectly treated `_normalize_direction()` output as a metric distance
- this was fixed before the current local read was retained

## 4. Unit-Level Attack-Direction Speed Envelope Read

The new engaged-unit speed seam now reads:

- non-engaged units keep the existing transition-speed budgeting
- engaged units get an additional speed allowance multiplier

Current read:

1. start from the already-computed transition speed
2. if the unit is engaged and has a valid engaged target:
   - compute attack direction from attacker to target
   - compute cosine between current unit orientation and that attack direction
   - map that cosine to a directional movement allowance:
     - forward attack -> highest allowance
     - lateral attack -> reduced allowance
     - backward attack -> lowest allowance
3. multiply by `engaged_speed_scale`

This is intentionally aligned with the existing combat-angle line conceptually:

- both use the same attacker-orientation vs attacker-to-target cosine read
- but combat quality and movement freedom remain separate mechanism effects

## 5. Local Quick Read

### Neutral sanity

Current local quick read:

- `neutral_transit_v1` still reaches objective cleanly
- `objective_reached_tick = 427`
- `final tick = 447`

So this Round 2 battle-side addition did not regress the current neutral carrier in the quick sanity path.

### Battle sanity

With the first overly-strong standoff defaults, battle stayed outside weapon range and did not honestly engage.

After reducing the test-only standoff weights to the current local defaults:

- battle no longer remains parked outside `attack_range`
- quick local run reaches:
  - `tick = 999`
  - alive counts roughly `38 / 34`
  - `min cross-fleet distance ≈ 4.46`
  - some units remain engaged at the final sampled state

So the current first bounded read is:

- battle standoff no longer blocks engagement entirely
- but battle still does not resolve cleanly
- this is a bounded seam opening, not a battle solution

## 6. Current Engineering Read

This round confirms:

1. battle standoff belongs inside the formation-transition carrier, not as optional later realism
2. unit-level attack-direction-aware speed limitation also belongs inside movement realization
3. both seams can be expressed honestly in `test_run/` without touching frozen runtime

This round also confirms:

- these seams alone do not solve battle plausibility
- they only make the carrier more honest about how approach/engagement movement should be read

## 7. Open Risks

Still open after this local step:

- battle remains unresolved in the quick default read
- matched neutral cases are still too rigid in Human motion read
- mismatch transition quality is still not honestly solved
- arrival plausibility and battle-contact plausibility remain separate live problems

## 8. Bottom Line

This Round 2 local step is accepted as:

- a real bounded carrier advance
- not a solution claim
- not a merge signal
- not a default-switch signal

The most honest current read is:

- battle target is now read less naively than raw centroid pursuit
- engaged-unit movement is now direction-aware
- but PR `#6` still remains a learning / review line, not a solved formation-transition line
