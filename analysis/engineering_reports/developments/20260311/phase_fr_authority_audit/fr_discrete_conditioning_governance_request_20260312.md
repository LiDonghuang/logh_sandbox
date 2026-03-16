# FR Discrete Conditioning Governance Request

Date: 2026-03-12
Status: Request for Governance Direction
Thread: `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit`

Engine Version: current local test harness over frozen runtime baseline
Modified Layer: none in this request; interpretive request only
Affected Parameters: `FR`, `PD`, `MB`
New Variables Introduced: none
Cross-Dimension Coupling: current bounded probes use hard conditional windows on existing variables
Mapping Impact: none
Governance Impact: request direction on whether discrete conditional probe logic is acceptable beyond bounded diagnosis
Backward Compatible: yes

Summary

1. Current strongest `FR5`-centered probe has produced useful evidence, but it relies on multiple discrete `if` conditions.
2. A further `PD5` shoulder refinement also became most effective only when expressed with another hard condition: `MB <= 5`.
3. Human concern is that personality-parameter mechanisms should, in principle, avoid this kind of discrete branching and remain as continuous as possible.
4. Engineering agrees this concern is structurally valid.
5. Governance direction is now needed on whether these discrete probes are acceptable only as diagnostics, or whether correction work must now pivot toward a continuous authority-shaping form.

## 1. Reason for This Request

Current bounded probes have been useful because they localize the defect.

However, their current form is not elegant.

They are implemented as hard windows over existing variables, for example:

- strict pre-contact only
- `FR` midband only
- `PD > 0.5` only
- and in the shoulder refinement, `MB <= 5` only

Human concern is:

```text
personality-parameter mechanisms should not, in principle,
be driven mainly by discrete if-statement logic.
```

Engineering agrees that this concern is legitimate and should be reviewed explicitly before more candidate refinement continues.

## 2. Current Discrete Forms Under Discussion

### 2.1 Current strongest candidate

Current strongest bounded candidate:

- `exp_precontact_plus_fr_centroid_midband_pdhigh_precontact_strong_probe`

Current logic:

```text
if engaged_fraction <= 0.0
   and 0.125 < kappa <= 0.5
   and pd_norm > 0.5:
       kappa_eff = 0.125
else:
       kappa_eff = kappa
```

This is already a layered discrete gate:

- one phase boundary
- one FR-band boundary
- one PD boundary

### 2.2 PD5 shoulder refinement

The most promising shoulder refinement from the latest bounded in-memory trial was:

```text
if engaged_fraction <= 0.0
   and 0.125 < kappa <= 0.5:
       if pd_norm > 0.5:
           kappa_eff = 0.125
       elif pd_norm == 0.5 and MB_raw <= 5:
           kappa_eff = 0.125
       else:
           kappa_eff = kappa
```

Engineering shorthand for that trial was:

- `pd5_mb_le5`

This adds another hard condition:

- `MB <= 5`

So even though it behaves better than a broad `PD5` opening, it is also more discretized.

## 3. Why Engineering Used Discrete Probes So Far

The reason was diagnostic clarity, not design preference.

Engineering used hard windows because they are effective at answering very narrow questions such as:

- is the overreach really pre-contact
- is the overreach really in the `FR5` middle band
- is the suspicious continuation tied mainly to high `PD`
- is the shoulder risk concentrated at high `MB`

For those questions, discrete probes have been useful because:

- they localize causality sharply
- they keep experimental scope bounded
- they avoid editing frozen runtime baseline

So Engineering can justify them as:

```text
diagnostic probes
```

But Engineering cannot confidently justify them yet as:

```text
good long-lived correction style
```

## 4. Engineering Concern

Engineering now shares the human concern in a more specific form:

```text
The thread may be drifting from root-cause localization
into building a correction family whose behavior is too dependent
on hand-authored discrete windows.
```

That would create several risks:

- brittle behavior at thresholds
- semantic opacity
- hidden dependence on arbitrary cut lines
- reduced parameter continuity
- poor fit with personality-parameter design discipline

This is especially sensitive because current governance guidance already emphasizes:

- authority-space release
- coupling reduction
- substrate purification

A correction that only works by stacking discrete windows may solve local cases while still feeling mechanically artificial.

## 5. Current Engineering Judgment

Engineering judgment at this point is:

1. The discrete probes have served their diagnostic purpose.
2. They have been useful in identifying:
   - pre-contact centroid-restoration as the primary suspect path
   - `FR5 / PD8` as the clearest overreach slice
   - `PD5 + MB8` as the main shoulder risk
3. But the same success increases the pressure to decide whether the next stage must move toward a more continuous expression.

Engineering does **not** currently recommend:

- treating the growing `if` tree itself as the preferred correction architecture

Engineering is more comfortable treating the current probe family as:

- a bounded diagnosis scaffold

rather than:

- a baseline-ready correction language

## 6. Governance Questions

Engineering requests governance direction on the following:

1. Are the current hard-window probe forms acceptable only as temporary diagnostic instruments?
2. Should future correction preparation now explicitly prefer continuous or monotone authority-shaping over additional discrete gating?
3. Should the current strongest candidate remain an evidence anchor only, rather than be advanced as a stylistically acceptable correction candidate?
4. If `PD5` shoulder work continues, should governance require that it be expressed without adding further hard cut lines such as `MB <= 5`?
5. Is it governance's preference that the next bounded candidate search stay on the same identified centroid-restoration path, but switch from:

```text
hard conditional inclusion / exclusion
```

to:

```text
continuous attenuation / continuous authority shaping
```

## 7. Engineering Recommendation

Engineering recommends the following governance position:

```text
Treat the current discrete if-conditioned probes as acceptable diagnostic instruments,
but not as the preferred long-lived correction style.
```

More specifically:

1. keep the current discrete candidates as evidence anchors
2. do not discard the path diagnosis they provided
3. do not continue indefinitely by adding more threshold branches
4. if further correction preparation is authorized, shift the next candidate search toward:
   - continuous
   - monotone
   - path-local
   authority-shaping on the same centroid-restoration suspect path

## 8. Why This Matters for the Next Step

Without governance direction here, Engineering risks going down one of two bad paths:

- continuing to stack discrete exceptions because they produce local wins
- or discarding useful diagnostic progress prematurely in the name of elegance

This request asks governance to resolve that tension explicitly.

## 9. Reproducibility Notes

This request introduces no new experiment.

Relevant existing artifacts:

- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/fr5_threshold_governance_request_20260311_round3.md`
- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/fr5_authority_space_release_validation_note_20260311.md`
- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/fr_authority_reallocation_note_20260311.md`
- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/fr_coupling_path_lock_note_20260311.md`
