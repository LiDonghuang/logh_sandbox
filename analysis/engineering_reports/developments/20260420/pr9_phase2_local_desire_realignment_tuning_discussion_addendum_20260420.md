## PR9 Phase II - Local Desire Realignment Tuning Discussion Addendum

Date: 2026-04-20  
Scope: engineering-side tuning discussion only  
Status: additional report for governance follow-up; no new implementation in this note

### 1. One-sentence conclusion

The current local-desire signal-read realignment is directionally correct, but
its visible battle effect is too strong; at the current implementation stage the
practical tuning is dominated almost entirely by `heading_bias_cap`, while
`speed_brake_strength` is effectively not biting on the maintained battle path,
so the battle reads too much like sustained unit-level dog fight instead of a
coarser fleet-unit maneuver.

### 2. Active owner/path and live knobs

Current owner/path under discussion:

- `runtime/engine_skeleton.py`
  - `EngineTickSkeleton._compute_unit_desire_by_unit(...)`

Current exposed local-desire knobs:

- `runtime.physical.local_desire.turn_need_onset`
- `runtime.physical.local_desire.heading_bias_cap`
- `runtime.physical.local_desire.speed_brake_strength`

Current engineering read after the realignment slice:

- heading-side primary signal now follows
  `fleet front -> selected target bearing`
- speed-side remains on
  `unit facing -> selected target bearing`
- because heading-side no longer depends on the shared facing-relative turn
  signal, the visible amplitude is now controlled mainly by
  `heading_bias_cap`

### 3. Human observation adopted as engineering test target

Human observation to explain:

1. direction is now qualitatively correct:
   - units visibly break away from formation and later rejoin
2. the amplitude looks too large:
   - the battle now reads too much like sustained dog fight
   - that abstraction may fit a one-ship unit model, but not the current
     `1 unit ~= 100 ships` read
3. without a straight backward / back-out mechanism, the visual brokenness is
   amplified:
   - formation fragmentation persists instead of cleaning up
4. the existing "双方阵型保持距离" read is being damaged:
   - at first contact the front ranks overlap and overrun too deeply
   - then the system pulls back too abruptly
   - because there is no straight backward motion, the visible recovery reads
     as rotational collapse rather than disciplined separation

Engineering accepted this as the evaluation target for the tuning pass.

### 4. Tuning experiment setup

Reference anchor:

- refreshed temporary working-anchor baseline
  - `battle_36v36`
  - `battle_100v100`

Experiment discipline:

- no code changes during this pass
- parameter-only overrides on the current accepted implementation
- bounded run count well below DOE batch limits

Primary tested combinations on `battle_36v36`:

- current default:
  - `heading_bias_cap=0.06`
  - `speed_brake_strength=0.03`
- lower-cap candidates:
  - `0.04 / 0.03`
  - `0.03 / 0.03`
  - `0.02 / 0.03`
- stronger-brake probes:
  - `0.04 / 0.05`
  - `0.03 / 0.05`
  - `0.03 / 0.07`

Shortlist cross-check on `battle_100v100`:

- current default
- `heading_bias_cap=0.02`
- `heading_bias_cap=0.04`

### 5. Main findings

#### 5.1 Direction is correct

Engineering agrees with the human qualitative read:

- the slice now produces visible break-away / rejoin behavior
- this confirms that the heading-side signal read is no longer silent

This is consistent with the implementation intent of the slice.

#### 5.2 The amplitude problem is real

The battle effect is not just cosmetically larger; it is materially
behavior-bearing.

Representative current-default result (`battle_36v36`):

- temporary working-anchor final:
  - `A alive=28 hp=2106.809046`
  - `B alive=27 hp=2200.015838`
- current realignment default:
  - `A alive=21 hp=1228.687966`
  - `B alive=20 hp=1083.277576`

So the “too strong” read is supported by outcome-level evidence, not only by
viewer impression.

Engineering also agrees with the refined human read:

- the current visual result is not just "more active"
- it is too close to sustained unit-level dog fight
- that is the wrong granularity for the present fleet abstraction, where one
  `Unit` stands for a grouped body rather than a single ship

Related battle-surface evidence from the refreshed temporary working-anchor
comparison:

- `battle_36v36`, window `130..160`
  - anchor mean contact `22.26`, mean links `21.55`
  - current realignment mean contact `17.55`, mean links `16.97`
- `battle_100v100`, window `190..205`
  - anchor mean contact `64.50`, mean links `54.56`
  - current realignment mean contact `8.19`, mean links `6.44`

Engineering read:

- the slice is not merely adding local texture
- it is materially changing where and how long fleets remain in mutual contact
- this is consistent with the human read that the keep-distance behavior is no
  longer holding cleanly

#### 5.3 `heading_bias_cap` is currently the only clearly live knob

This tuning pass found that changing `heading_bias_cap` materially changes the
battle surface, while changing `speed_brake_strength` currently does not.

Examples from `battle_36v36`:

- `heading_bias_cap=0.04, speed_brake_strength=0.03`
- `heading_bias_cap=0.04, speed_brake_strength=0.05`

Result:

- effectively identical metrics across the measured windows

Likewise:

- `heading_bias_cap=0.03, speed_brake_strength=0.03`
- `heading_bias_cap=0.03, speed_brake_strength=0.05`
- `heading_bias_cap=0.03, speed_brake_strength=0.07`

Result:

- again effectively identical in the measured battle windows

Engineering read:

- `speed_brake_strength` is not the current control point for the observed
  brokenness
- the speed-side read is still too cold / too collapsed to act as a practical
  tuning lever on the maintained battle path

#### 5.4 Lowering `heading_bias_cap` changes behavior, but not in a simple monotonic “less breakup” way

Key `battle_36v36` observations:

- current default `0.06 / 0.03`
  - window `130..160`
    - mean contact `17.55`
    - mean links `16.97`
    - mean RMS-sum `13.33`
  - final:
    - `A alive=21`
    - `B alive=20`

- `0.04 / 0.03`
  - window `130..160`
    - mean contact `21.26`
    - mean links `20.26`
    - mean RMS-sum `11.76`
  - final:
    - `A alive=21`
    - `B alive=20`

- `0.02 / 0.03`
  - window `130..160`
    - mean contact `19.58`
    - mean links `18.77`
    - mean RMS-sum `12.61`
  - final:
    - `A alive=22`
    - `B alive=21`

Engineering read:

- lowering the cap does not simply “cool everything down”
- the dynamics are nonlinear
- lower cap can reduce one form of visible spread while still increasing or
  redistributing sustained contact

#### 5.5 Cross-scale behavior is not stable yet

`battle_100v100` makes the issue clearer.

Temporary working anchor:

- window `190..205`
  - mean contact `64.50`
  - mean links `54.56`
  - mean RMS-sum `17.27`

Current default `0.06 / 0.03`:

- window `190..205`
  - mean contact `8.19`
  - mean links `6.44`
  - mean RMS-sum `19.09`

Candidate `0.02 / 0.03`:

- window `190..205`
  - mean contact `19.63`
  - mean links `18.69`
  - mean RMS-sum `17.78`

Candidate `0.04 / 0.03`:

- window `190..205`
  - mean contact `25.44`
  - mean links `23.88`
  - mean RMS-sum `17.67`

Engineering read:

- cap reduction does move the system
- but the scale response is not yet clean or obviously “settled”
- this is another reason not to treat the current slice as tune-complete

### 6. Engineering interpretation

Current best explanation is:

1. heading-side realignment succeeded in making local off-axis bias visible
2. but speed-side remains effectively dormant
3. so the slice currently behaves like:
   - strong heading freedom
   - weak practical speed restraint
4. without a true backward / disengage mechanism, this makes the battle read
   more broken than intended
5. because the standoff / keep-distance behavior is not being protected well
   enough, first contact can overrun into deep front-rank overlap before the
   system tries to recover
6. with no straight backward motion, that recovery is expressed largely through
   turning and circulation, which is why the formations read as rotationally
   collapsed rather than cleanly separated

Important nuance:

- the lack of straight backward motion is a real visual amplifier
- but engineering does **not** think that alone explains the present tuning
  difficulty
- the more immediate mechanism problem is that speed-side is still not a live
  regulator on the maintained path
- so the current slice has a real asymmetry:
  - heading-side can now pull units off the coarse front more easily
  - speed-side still cannot reliably impose a later, weaker, brake-only
    "do not over-commit" restraint
- that asymmetry is the most direct mechanism explanation for:
  - persistent broken-up dog-fight-like motion
  - damaged keep-distance behavior at first contact
  - pullback by rotation rather than by bounded backward separation

### 7. Minimal tuning judgment

What parameter-only tuning can do right now:

- adjust heading-side amplitude through `heading_bias_cap`

What parameter-only tuning cannot reliably do right now:

- use `speed_brake_strength` to materially soften the slice

Therefore, purely from the engineering-side tuning pass:

- `heading_bias_cap` is a valid knob
- but the current exposed parameter set is not yet a strong enough control panel
  to make this slice feel properly bounded across scales

### 8. Governance-facing recommendation

Recommended governance read:

1. the current slice direction is good and should not be reverted purely because
   it is visible
2. however, the current default should **not** yet be treated as a maintained
   regime
3. parameter-only cooling is possible on the heading side, but it is not
   sufficient as the whole answer
4. the next bounded governance question should not be “more brute-force cap
   tuning”
5. the more useful bounded question is:
   - how speed-side should become meaningfully active without introducing
     retreat, mode, or a second target source
6. the governance-side evaluation should explicitly include whether the next
   bounded correction preserves a fleet-scale read:
   - less sustained dog-fight-like breakup
   - better first-contact separation / standoff preservation
   - less rotational collapse in the absence of straight backward motion

### 9. If governance wants one shortest engineering summary

Shortest summary:

- the current slice is qualitatively right
- the visible amplitude is too strong and too dog-fight-like for the current
  unit abstraction
- `heading_bias_cap` is the only clearly live knob right now
- `speed_brake_strength` is effectively inert on the maintained path
- so the next useful discussion is not broad doctrine, but a bounded question
  about speed-side activation / damping becoming real while restoring
  keep-distance behavior and reducing rotational collapse
