# Intermix Indicator Design Note

Date: 2026-03-13  
Status: Engineering note  
Scope: Observer/diagnostic design only. No plot authorization. No runtime authorization.

## 1. Why This Note Exists

Recent close-contact review and the first hostile contact-impedance prototype both exposed the same gap:

- current plots do not directly encode hostile intermixing depth
- `projection_pairs_count` is too indirect
- `FrontCurv` and `C_W_PShare` are useful, but they are not contact-penetration indicators

This note asks a narrower question:

```text
What should count as a usable intermixing indicator?
```

## 2. Current Informal Metrics

During recent bounded prototype tests, two temporary pair-count diagnostics were used.

### 2.1 Overlap pairs

Definition:

```text
hostile unit pairs with distance < min_unit_spacing
```

Interpretation:

- broad hostile overlap / excessive proximity
- catches many contact pairs, including shallow crowding

### 2.2 Deep intermixing pairs

Definition:

```text
hostile unit pairs with distance < 0.5 * min_unit_spacing
```

Interpretation:

- deeper hostile penetration
- better aligned with the visual impression of "pass-through" or "weaving through"

## 3. Why The Raw Count Is Not Yet Mature

The current raw `deep pair count` is useful as a prototype-only diagnostic, but it is not yet strong enough to promote directly into a permanent plot.

### 3.1 Fleet-size sensitivity

Raw pair count scales with:

- total units
- local density
- number of available hostile pairings

This makes cross-case comparison noisy unless size is tightly controlled.

### 3.2 Hard-threshold sensitivity

The current definition is based on:

```text
distance < 0.5 * min_unit_spacing
```

That is easy to compute, but still a hard threshold. Small geometric changes can create step-like count changes.

### 3.3 Not yet integrated into observer telemetry

At present, this metric is not part of the standard observer telemetry family in `test_run`.

So the current signal is:

- experimentally useful
- but not yet standardized

## 4. Candidate Indicator Families

Three concept families appear worth distinguishing.

### A. Raw deep-pair count

Definition:

```text
count(hostile pairs with d < 0.5 * separation_radius)
```

Pros:

- simplest
- directly tied to visible deep interpenetration

Cons:

- size-sensitive
- threshold-sensitive
- poor portability across DOE grids

### B. Deep-intermix ratio

Definition candidate:

```text
deep_pairs / hostile_close_pairs
```

or

```text
deep_pairs / hostile_pair_normalizer
```

Pros:

- more scale-stable than raw count
- easier to compare across fleet sizes

Cons:

- depends on denominator choice
- still threshold-based

### C. Continuous intermix severity

Definition candidate:

For hostile pairs within a local radius, accumulate a continuous penetration penalty such as:

```text
severity += clamp01((r_mix - d) / r_mix)^p
```

where:

- `d` is hostile-pair distance
- `r_mix` is a mixing radius, likely near `min_unit_spacing`
- `p` controls sharpness

Pros:

- continuous
- more aligned with current modernization principle
- less brittle than hard pair counts

Cons:

- requires more design choice
- less immediately intuitive than a plain count

## 5. Current Engineering Preference

If the goal is only fast prototype debugging:

- raw `deep pair count` is acceptable

If the goal is a more durable observer diagnostic:

- continuous `intermix severity` is the stronger direction

If a middle step is needed:

- `deep-intermix ratio` is a reasonable bridge metric

So the provisional ordering is:

```text
continuous intermix severity
> deep-intermix ratio
> raw deep-pair count
```

## 6. Plot Readiness Judgment

Current judgment:

```text
Not yet plot-ready as a permanent observer slot.
```

Reason:

- the concept is promising
- but the present raw-count form is still prototype-grade

This does **not** mean the line should be dropped.

It means:

1. standardize the indicator first
2. compare at least one ratio/continuous variant
3. only then decide whether it deserves a stable plot slot

## 7. Slot Replacement Guidance

If this line later becomes mature enough for a temporary phase-specific plot, the most plausible slot to borrow is:

- `slot_09` (`Wedge`)

Reason:

- current phase is engagement substrate modernization
- wedge/doctrine readout is not the current primary concern
- `FrontCurv` and `C_W_PShare` still carry more immediate diagnostic value

This is only a provisional plotting judgment, not an implementation recommendation.

## 8. Recommendation

Do not yet promote `deep intermixing` raw count into a permanent plot.

Recommended next step:

1. keep raw deep-pair count as a prototype-only debug signal
2. design one normalized version and one continuous severity version
3. compare them on the mirrored neutral fixture
4. then re-evaluate plot readiness

## 9. Bottom Line

`Deep intermixing` is a meaningful contact-phase diagnostic direction, but its current raw-count form is not yet mature enough to become a permanent observer plot.

The more defensible long-term goal is:

```text
standardized intermix severity,
not just raw deep-pair count.
```
