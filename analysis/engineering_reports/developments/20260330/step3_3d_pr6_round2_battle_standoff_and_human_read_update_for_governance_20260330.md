# Step 3 3D PR #6 Round 2 Update for Governance
## Battle Standoff + Attack-Direction Speed Envelope

Status: engineering update / human-read update / discussion handoff  
Scope: PR `#6` active review / learning line  
Layer scope: `test_run/` harness-only candidate work  
Frozen runtime status: `runtime/engine_skeleton.py` untouched  
Decision scope: not merge approval, not default-switch approval, not solution claim

---

## I. Purpose

This note records the current bounded Round 2 advance on PR `#6`, plus the latest Human read after direct motion review.

The immediate goals of this round were:

1. continue the carrier as a **formation-transition carrier**, not a reference-surface tuning line
2. open battle target as **relative standoff distance**
3. open movement realization further via **unit-level attack-direction-aware speed envelope**
4. keep all work inside the current frozen-runtime discipline

This note also records the current stop point:

- the new seams are valuable
- Human judges them directionally correct
- but they expose the next major problem more clearly rather than solving the whole line

---

## II. What Was Added

This round added two new bounded `v4a test_only` mechanism lines in `test_run/`.

### A. Fleet-level battle standoff distance

Battle target no longer reads only as:

- move toward enemy centroid / enemy reference point

It now also reads through a first bounded desired engagement distance:

`d* = attack_range + self_w * own_forward_extent + enemy_w * enemy_forward_extent`

Current first bounded read:

- if current battle distance is well above `d*`, approach
- if current distance is near `d*`, hold
- this first bounded read does **not** yet include an active retreat branch

Important local correction:

- an early local cut accidentally treated a normalized-direction intensity flag as metric distance
- that was corrected before the current retained read

### B. Unit-level attack-direction-aware speed envelope

Engaged unit movement freedom is no longer direction-blind.

The current bounded read is:

- non-engaged units keep the existing transition budgeting
- engaged units receive additional speed limitation according to:
  - whether they are engaged
  - direction from attacker to current engaged target
  - cosine between attacker orientation and attack direction

This yields a bounded forward / lateral / backward movement allowance.

Conceptual coupling read:

- this shares the same attacker-orientation vs attacker-to-target cosine semantics as the existing combat-angle quality line
- but combat quality and movement freedom remain separate mechanism effects

---

## III. Current Local Defaults

Current retained test-only values:

- `battle_standoff_self_extent_weight = 0.15`
- `battle_standoff_enemy_extent_weight = 0.15`
- `battle_standoff_hold_band_ratio = 0.10`
- `engaged_speed_scale = 0.70`
- `attack_speed_lateral_scale = 0.65`
- `attack_speed_backward_scale = 0.35`

These are not being presented as final values.

They are only the current bounded local defaults that avoided the first failed read in which battle remained parked outside weapon range.

---

## IV. What Improved

### 1. Neutral did not regress in quick sanity read

Local quick sanity:

- `neutral_transit_v1`
- `objective_reached_tick = 427`
- `final tick = 447`

So the new battle-side seams did not obviously break the current neutral carrier in the quick local sanity path.

### 2. Battle standoff now reads as real mechanism, not empty naming

Human read:

- the `maintain d*` idea is basically correct
- this mechanism is now doing something real and meaningful

Engineering agrees.

The line now no longer reads as:

- only enemy-centroid pursuit under a different label

### 3. Direction-aware speed envelope did not expose an obvious immediate anomaly

Human read:

- no immediate abnormality was observed from the unit-level attack-direction-aware speed envelope itself

Engineering agrees with this bounded current read.

---

## V. Current Human Read

Human’s latest battle read, especially on `4 -> 4`, is now the most important control-surface result of this round.

### A. What looks correct

Human read:

- while battle begins, both fleets still maintain formation
- and they maintain it rather well

This is important.

It means the current line is not simply dissolving into shapeless contact chaos.

### B. What the next real problem is

As battle continues:

- each side’s effective front / fire plane drifts naturally
- but because both sides continue to maintain formation,
  only a subset of each formation remains in active exchange
- in Human read, this becomes mainly:
  - A left wing
  - against B left wing

This then evolves into:

- both fleets rotating counter-clockwise around that local left-wing junction

Human read:

- this is now the next major problem
- not failure of the new seams themselves

Engineering accepts this read.

---

## VI. Current Engineering Interpretation

Engineering read after Human review:

1. the new `d*` seam is correct in principle
2. the attack-direction-aware speed envelope is also a meaningful and plausible same-theme seam
3. the branch is still far from solved
4. the new seams mainly expose the next battle-plausibility problem more clearly

That next problem currently reads as:

- formation is preserved too faithfully relative to a drifting fire plane
- battle does not yet reorient or relax the formation honestly once sustained contact geometry changes

So the current battle line now appears to need one or both of these future directions:

### A. Fire-plane-aware front reorientation

Try to rotate / bias the maintained front so that:

- the formation’s active front better aligns with the direction that maximizes real fire opportunity

This is the “keep the formation, but turn the front intelligently” path.

### B. Post-contact local relaxation toward range entry

After contact begins, allow some bounded loosening of formation so units gain a controlled component that moves them toward:

- nearby local enemy elements
- in order to enter or preserve honest firing range

This is the “do not keep the formation so rigidly that only one wing keeps fighting” path.

No implementation claim is being made here.

These are simply the currently visible next directions exposed by Human motion read.

---

## VII. Methodological Read

This round reinforces the branch’s current methodology lesson:

- Human motion read remains the controlling review surface
- scalar cleanliness is insufficient

The round also shows a more constructive version of the same lesson:

- once the carrier owns a more honest seam, Human read can distinguish:
  - which new mechanism is basically right
  - from which newly exposed battle behavior now becomes the next real problem

That is what happened here.

Human does **not** currently read this round as:

- wasted work
- failed seam opening

Human reads it as:

- a meaningful carrier advance
- that correctly exposed the next formation/battle coupling problem

Engineering accepts that read.

---

## VIII. Current Operational Stop Point

Because Codex token budget is nearly exhausted this week, Engineering is not continuing implementation in this note’s turn.

Instead:

- current local work is being preserved on PR `#6`
- Human and Governance will discuss the newly exposed battle read first
- next implementation step is intentionally deferred

This is a deliberate pause, not a completion claim.

---

## IX. Bottom Line

Current accepted bounded read:

- the new fleet-level `d*` standoff seam is basically correct
- the unit-level attack-direction-aware speed envelope is also basically correct
- neither should be rolled back casually

But the next visible problem is now clearer:

- as sustained battle contact evolves, the active fire plane drifts
- current formation maintenance then localizes combat too strongly
- and battle devolves into left-wing junction rotation rather than honest broader engagement geometry

So PR `#6` should still continue as an active learning line,
with this round preserved as:

- real progress
- real same-theme seam opening
- and real Human-exposed next-problem clarification
