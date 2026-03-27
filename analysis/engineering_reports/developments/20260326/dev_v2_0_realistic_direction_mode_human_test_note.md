# dev_v2.0 Realistic Direction Mode Human Test Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: viewer-local human test guidance only
Affected Parameters: viewer CLI `--direction-mode`
New Variables Introduced: none beyond the new `realistic` mode itself
Cross-Dimension Coupling: human test compares two readout modes over the same replay output
Mapping Impact: none
Governance Impact: provides a bounded human-review path for the new viewer-local direction readout
Backward Compatible: yes

Summary
- Human comparison should use the same replay source and switch only `--direction-mode`.
- The most useful side-by-side comparison is `settings` versus `realistic`.
- `realistic` should look closer to actual local travel posture, especially at startup and near arrival.
- The expected result is reduced apparent jitter without changing the underlying path.

## 1. Recommended Launch Commands

Neutral-transit fixture with current layered mode:

```powershell
.\.venv_dev_v2_0\Scripts\python.exe -m viz3d_panda.app --source neutral_transit_fixture --direction-mode settings
```

Neutral-transit fixture with the new realized-path readout:

```powershell
.\.venv_dev_v2_0\Scripts\python.exe -m viz3d_panda.app --source neutral_transit_fixture --direction-mode realistic
```

## 2. What To Compare

Recommended viewing procedure:

1. pause early and use `N/B` single-step or hold-step
2. inspect the first several ticks
3. inspect the late arrival / flattening region
4. compare only the displayed heading cue, not the path geometry itself

## 3. Expected Differences

With `settings` on the current bounded neutral-transit carrier:

- the readout follows the existing layered direction mode
- under the current layered `composite` setting, the bounded no-enemy carrier effectively reads as `effective`
- early structured orientation posture and late flattening can look more visually active

With `realistic`:

- early heading should be closer to the realized local path tangent
- late near-arrival heading should hold steadier instead of reacting to tiny local movement noise
- the travel posture should look more physically plausible as a local replay readout

## 4. What Would Count As Success

Success for this viewer-local clarification means:

- `realistic` is visibly distinct from `effective/settings`
- startup posture looks less like structured intent jitter
- near-arrival posture looks less noisy
- the underlying path, stop behavior, and replay source remain unchanged

## 5. What Would Count As Failure

The change should be reconsidered if:

- `realistic` just collapses back into `effective` with no visible difference
- it introduces new oscillation that is not present in the replay path
- it depends on runtime changes or new replay fields
- it starts behaving like a new semantic system rather than a readout clarification
