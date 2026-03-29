# Step 3 3D Two-Layer Spacing Follow-Up and V4A Default Request

- Engine Version: `dev_v2.0`
- Modified Layer: `analysis / governance-facing follow-up note only`
- Affected Parameters: none in committed runtime
- New Variables Introduced: none
- Cross-Dimension Coupling: none
- Mapping Impact: none
- Governance Impact: records the second bounded comparison-path result and requests governance review of a possible future `v4a` default-read opening
- Backward Compatible: yes
- Summary: a second bounded comparison path (`64 units`) preserves the strong spacing-decoupling result, and engineering now asks governance whether `v4a` should be reviewed as a possible shared neutral+battle default candidate while keeping `v3a` retained

## Purpose

This note follows the two-layer spacing opening scope note.

It has two bounded jobs:

1. record the next comparison-path result after the initial spacing-decoupling probe
2. ask whether governance wants to open a bounded review of `v4a` as a possible shared default movement line for both neutral-transit and battle paths, while keeping `v3a` retained

This note is not an implementation instruction.

It is not a silent default switch.

## 1. New Bounded Result

After the first decoupling probe, one more bounded comparison path was checked using:

- `fleet_size = 64`
- `aspect_ratio = 1.0`
- `aspect_ratio = 4.0`

Two cases were compared:

### A. `coupled_2.0_2.0`
- spawn/reference spacing = `2.0`
- runtime low-level floor = `2.0`

### B. `decoupled_2.0_1.0`
- spawn/reference spacing = `2.0`
- runtime low-level floor = `1.0`

## 2. Follow-Up Read

The second comparison path preserved the same qualitative result as the first:

- the coupled case still stretched in early ordinary transit
- the decoupled case remained effectively rigid over the sampled early ticks

In the sampled `64-unit` read:

- `coupled_2.0_2.0` still showed:
  - width/depth drift
  - front extent growth
  - rear/front forward-slot error split

- `decoupled_2.0_1.0` held:
  - width/depth ratio at the initial rectangle read
  - front extent ratio at `1.0`
  - expected-position RMS error at `0.0`
  - rear / middle / front forward-slot error at `0.0`

So the decoupling result no longer reads like a `100-unit` special case.

## 3. Current Engineering Read After the Follow-Up

The current bounded read is now:

1. early standard-rectangle stretching still primarily reads as an ordinary-transit movement-vs-restore issue
2. the overloaded low-level spacing radius still reads as a major amplifier
3. the decoupling result remains strong across more than one bounded comparison path

This is still not enough to justify silent implementation.

But it is enough to justify a more serious governance read of the line.

## 4. Governance Request on `v4a`

In the current local investigation path, the useful rectangle/spacing probes are being run on:

- `movement_model = v4a`

Engineering now asks governance to consider a bounded discussion question:

Should `v4a` be reviewed as a possible shared default movement mechanism for:

- neutral-transit fixture work
- maintained battle-path work

while:

- keeping `v3a` retained
- not deleting the legacy line
- not silently switching the repo default by momentum

## 5. Why This Request Is Being Raised

This request is not based on one isolated number.

It is being raised because:

- the recent bounded hardening and spacing probes are already being interpreted through the current `v4a` path
- the current discussion is no longer just about one local tweak
- if future structural discussion continues to rely on `v4a`, governance may want to decide explicitly whether `v4a` should stay:
  - test-only
  - bounded-candidate
  - or default-review eligible

## 6. What Is Not Requested Here

This note does **not** request:

- immediate default switching
- deletion of `v3a`
- runtime baseline replacement by stealth
- implementation approval for two-layer spacing

It only asks governance whether:

1. the two-layer spacing line should continue to advance structurally
2. `v4a` should now be read as eligible for bounded default-review discussion across both neutral and battle paths

## Bottom Line

The new comparison path strengthens the spacing-decoupling conclusion.

Engineering therefore recommends that governance now review two bounded questions together:

1. whether the two-layer spacing discussion should continue beyond concept opening
2. whether `v4a` should be explicitly reviewed as a possible shared default movement line, with `v3a` still retained
